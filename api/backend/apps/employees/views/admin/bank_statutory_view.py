"""
Bank, PF, and ESI views for the admin employee details page.
"""

import json

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.parsers import BaseParser, FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.serializers.admin.bank_statutory_serializer import (
    BankAccountUpdateSerializer,
    BankStatutoryDetailsSerializer,
    BankStatutoryCreateSerializer,
    BankStatutoryCreateWithEmployeeSerializer,
    StatutoryContributionsUpdateSerializer,
)
from apps.employees.models.employee import Employee
from apps.employees.services.admin.bank_statutory_service import (
    create_bank_account,
    deactivate_bank_account,
    get_bank_statutory_details,
    update_statutory_contributions,
    upsert_bank_account,
)
from apps.employees.services.bank_statutory_details import (
    apply_bank_statutory_details,
    validate_bank_statutory_details,
)


BANK_ACCOUNT_FIELDS = {
    "bank",
    "bank_code",
    "bank_name",
    "account_type",
    "account_number",
    "ifsc_code",
    "micr_code",
    "branch_name",
    "branch_address",
    "account_holder_name",
    "bank_status",
    "is_primary",
    "is_salary_account",
    "payment_type_id",
}


class PlainTextJSONParser(BaseParser):
    media_type = "text/plain"

    def parse(self, stream, media_type=None, parser_context=None):
        raw_body = stream.read().decode("utf-8")
        if not raw_body.strip():
            return {}
        try:
            return json.loads(raw_body)
        except ValueError as exc:
            raise ParseError("Text body must contain valid JSON.") from exc


class BankStatutoryDetailsView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
        "PATCH": ["employee.edit_employee"],
    }
    parser_classes = [JSONParser, PlainTextJSONParser, FormParser, MultiPartParser]

    def get(self, request, employee_id):
        try:
            details = get_bank_statutory_details(employee_id)
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BankStatutoryDetailsSerializer(details)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, employee_id):
        serializer = BankStatutoryCreateSerializer(
            data=request.data,
            context={"require_coverage_identifiers": True},
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            validated_data = serializer.validated_data

            if "bank_account" in validated_data:
                details = create_bank_account(
                    employee_id,
                    validated_data["bank_account"],
                    updated_by=updated_by,
                )
            else:
                details = get_bank_statutory_details(employee_id)

            contribution_data = {
                key: validated_data[key]
                for key in ("statutory_documents", "pf_details", "esi_details", "lwf_details")
                if key in validated_data
            }
            if contribution_data:
                details = update_statutory_contributions(
                    employee_id,
                    contribution_data,
                    updated_by=updated_by,
                )
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = BankStatutoryDetailsSerializer(details)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, employee_id):
        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            details = get_bank_statutory_details(employee_id)

            if "bank_accounts" in request.data:
                employee = get_object_or_404(Employee, id=employee_id, is_active=True)
                cleaned = validate_bank_statutory_details(
                    {"bank_accounts": request.data["bank_accounts"]}
                )
                apply_bank_statutory_details(employee, cleaned)
                details = get_bank_statutory_details(employee_id)
            elif "bank_account" in request.data:
                bank_serializer = BankAccountUpdateSerializer(
                    data=request.data["bank_account"],
                    partial=True,
                )
                bank_serializer.is_valid(raise_exception=True)
                details = upsert_bank_account(
                    employee_id,
                    bank_serializer.validated_data,
                    updated_by=updated_by,
                )
            elif BANK_ACCOUNT_FIELDS.intersection(request.data.keys()):
                bank_serializer = BankAccountUpdateSerializer(
                    data=request.data,
                    partial=True,
                )
                bank_serializer.is_valid(raise_exception=True)
                details = upsert_bank_account(
                    employee_id,
                    bank_serializer.validated_data,
                    updated_by=updated_by,
                )

            contribution_data = {
                key: request.data[key]
                for key in ("statutory_documents", "pf_details", "esi_details", "lwf_details")
                if key in request.data
            }
            if contribution_data:
                contribution_serializer = StatutoryContributionsUpdateSerializer(
                    data=contribution_data,
                    partial=True,
                    context={"require_coverage_identifiers": False},
                )
                contribution_serializer.is_valid(raise_exception=True)
                details = update_statutory_contributions(
                    employee_id,
                    contribution_serializer.validated_data,
                    updated_by=updated_by,
                )
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = BankStatutoryDetailsSerializer(details)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class BankStatutoryCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.edit_employee"]
    parser_classes = [JSONParser, PlainTextJSONParser, FormParser, MultiPartParser]

    def post(self, request):
        serializer = BankStatutoryCreateWithEmployeeSerializer(
            data=request.data,
            context={"require_coverage_identifiers": True},
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            validated_data = serializer.validated_data
            employee_id = validated_data["employee_id"]

            if "bank_account" in validated_data:
                details = create_bank_account(
                    employee_id,
                    validated_data["bank_account"],
                    updated_by=updated_by,
                )
            else:
                details = get_bank_statutory_details(employee_id)

            contribution_data = {
                key: validated_data[key]
                for key in ("statutory_documents", "pf_details", "esi_details", "lwf_details")
                if key in validated_data
            }
            if contribution_data:
                details = update_statutory_contributions(
                    employee_id,
                    contribution_data,
                    updated_by=updated_by,
                )
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = BankStatutoryDetailsSerializer(details)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class BankAccountAdminView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.edit_employee"]
    parser_classes = [JSONParser, PlainTextJSONParser, FormParser, MultiPartParser]

    def _save(self, request, employee_id, response_status, partial):
        serializer = BankAccountUpdateSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            details = upsert_bank_account(
                employee_id,
                serializer.validated_data,
                updated_by=updated_by,
            )
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = BankStatutoryDetailsSerializer(details)
        return Response(response_serializer.data, status=response_status)

    def post(self, request, employee_id):
        serializer = BankAccountUpdateSerializer(data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)

        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            details = create_bank_account(
                employee_id,
                serializer.validated_data,
                updated_by=updated_by,
            )
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = BankStatutoryDetailsSerializer(details)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request, employee_id):
        return self._save(request, employee_id, status.HTTP_200_OK, partial=True)


class BankAccountItemAdminView(APIView):
    """Delete a single employee bank account (soft delete)."""

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.edit_employee"]

    def delete(self, request, employee_id, account_id):
        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            details = deactivate_bank_account(
                str(employee_id),
                str(account_id),
                updated_by=updated_by,
            )
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = BankStatutoryDetailsSerializer(details)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class StatutoryContributionsAdminView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.edit_employee"]
    parser_classes = [JSONParser, PlainTextJSONParser, FormParser, MultiPartParser]

    def _save(self, request, employee_id, response_status):
        serializer = StatutoryContributionsUpdateSerializer(
            data=request.data,
            partial=True,
            context={
                "require_coverage_identifiers": response_status == status.HTTP_201_CREATED
            },
        )
        serializer.is_valid(raise_exception=True)

        try:
            updated_by = request.user if request.user and request.user.is_authenticated else None
            details = update_statutory_contributions(
                employee_id,
                serializer.validated_data,
                updated_by=updated_by,
            )
        except Http404:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response_serializer = BankStatutoryDetailsSerializer(details)
        return Response(response_serializer.data, status=response_status)

    def post(self, request, employee_id):
        return self._save(request, employee_id, status.HTTP_201_CREATED)

    def patch(self, request, employee_id):
        return self._save(request, employee_id, status.HTTP_200_OK)
