"""Admin direct-edit section APIs for employee profile pages."""

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_spectacular.utils import extend_schema, extend_schema_view
except ImportError:  # pragma: no cover

    def extend_schema(*args, **kwargs):
        def decorator(obj):
            return obj

        return decorator

    def extend_schema_view(**kwargs):
        def decorator(cls):
            return cls

        return decorator

from apps.employees.constants import ESSModule
from apps.employees.models import Employee, EmployeeChangeRequest
from apps.security.permissions import HasRBACPermission
from apps.employees.serializers.employee.address_details import (
    AddressDetailsSubmitSerializer,
)
from apps.employees.serializers.employee.employment_details import (
    EmploymentDetailsSubmitSerializer,
)
from apps.employees.serializers.admin.insurance_policy_serializer import (
    AdminInsurancePolicyListSerializer,
    AdminInsurancePolicySerializer,
)
from apps.employees.serializers.employee.language_details import (
    LanguageDetailsSubmitSerializer,
)
from apps.employees.serializers.employee.medical_details import (
    MedicalDetailsSubmitSerializer,
)
from apps.employees.serializers.employee.personal_details import (
    PersonalDetailsSubmitSerializer,
)
from apps.employees.services.address_details import (
    apply_address_details,
    build_address_details,
)
from apps.employees.services.employment_details import (
    apply_employment_details,
    build_employment_details,
)
from apps.employees.services.admin.insurance_policy_service import (
    create_employee_insurance_policy,
    delete_employee_insurance_policy,
    get_employee_insurance_policy,
    list_employee_insurance_policies,
    update_employee_insurance_policy,
)
from apps.employees.services.language_details import (
    apply_language_details,
    build_language_details,
)
from apps.employees.services.medical_details import (
    apply_medical_details,
    build_medical_details,
)
from apps.employees.services.personal_details import (
    apply_personal_details,
    build_personal_details,
)
from apps.employees.services.validators import ModuleValidator


def _validation_error_response(exc):
    if hasattr(exc, "detail"):
        return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
    return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


def _apply_or_400(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except (IntegrityError, ValueError) as exc:
        return _validation_error_response(exc)
    except Exception as exc:
        if hasattr(exc, "detail"):
            return _validation_error_response(exc)
        raise
    return None


class _AdminSectionView(APIView):
    serializer_class = None
    response_key = None
    module = None
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "PATCH": ["employee.edit_employee"],
        "PUT": ["employee.edit_employee"],
    }

    def get_employee(self, employee_id):
        return get_object_or_404(Employee, pk=employee_id)

    def validate_request_data(self, request, employee):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        data.pop("remarks", None)
        if self.module is None:
            return data
        return ModuleValidator.validate(
            self.module,
            data,
            EmployeeChangeRequest.Action.UPDATE,
            employee=employee,
        )

    def get_response_payload(self, employee):
        raise NotImplementedError

    def apply_data(self, employee, data):
        raise NotImplementedError

    def get(self, request, employee_id):
        employee = self.get_employee(employee_id)
        return Response({self.response_key: self.get_response_payload(employee)})

    def patch(self, request, employee_id):
        employee = self.get_employee(employee_id)
        data = self.validate_request_data(request, employee)
        error_response = _apply_or_400(self.apply_data, employee, data)
        if error_response is not None:
            return error_response
        employee = self.get_employee(employee_id)
        return Response({self.response_key: self.get_response_payload(employee)})

    def put(self, request, employee_id):
        return self.patch(request, employee_id)


@extend_schema_view(
    get=extend_schema(summary="Get employee personal details (Admin)"),
    patch=extend_schema(
        summary="Update employee personal details (Admin)",
        request=PersonalDetailsSubmitSerializer,
    ),
)
class EmployeePersonalDetailsAdminView(_AdminSectionView):
    serializer_class = PersonalDetailsSubmitSerializer
    response_key = "personal_details"
    module = ESSModule.PERSONAL

    def get_employee(self, employee_id):
        return get_object_or_404(
            Employee.objects.select_related(
                "gender",
                "personal_details",
                "personal_details__marital_status",
                "personal_details__religion",
                "personal_details__caste",
                "personal_details__caste_category",
                "personal_details__nationality",
                "personal_details__blood_group",
            ),
            pk=employee_id,
        )

    def get_response_payload(self, employee):
        return build_personal_details(employee)

    def apply_data(self, employee, data):
        apply_personal_details(employee, data)


@extend_schema_view(
    get=extend_schema(summary="Get employee address details (Admin)"),
    patch=extend_schema(
        summary="Update employee address details (Admin)",
        request=AddressDetailsSubmitSerializer,
    ),
)
class EmployeeAddressDetailsAdminView(_AdminSectionView):
    serializer_class = AddressDetailsSubmitSerializer
    response_key = "address_details"
    module = ESSModule.ADDRESS

    def get_employee(self, employee_id):
        return get_object_or_404(
            Employee.objects.prefetch_related(
                "addresses__city",
                "addresses__state",
                "addresses__country",
            ),
            pk=employee_id,
        )

    def get(self, request, employee_id):
        employee = self.get_employee(employee_id)
        return Response(build_address_details(employee))

    def patch(self, request, employee_id):
        employee = self.get_employee(employee_id)
        data = self.validate_request_data(request, employee)
        error_response = _apply_or_400(self.apply_data, employee, data)
        if error_response is not None:
            return error_response
        employee = self.get_employee(employee_id)
        return Response(build_address_details(employee))

    def get_response_payload(self, employee):
        return build_address_details(employee)

    def apply_data(self, employee, data):
        apply_address_details(employee, data)


@extend_schema_view(
    get=extend_schema(summary="Get employee employment details (Admin)"),
    patch=extend_schema(
        summary="Update employee employment details (Admin)",
        request=EmploymentDetailsSubmitSerializer,
    ),
)
class EmployeeEmploymentDetailsAdminView(_AdminSectionView):
    serializer_class = EmploymentDetailsSubmitSerializer
    response_key = "employment_details"
    module = ESSModule.EMPLOYMENT

    def get_employee(self, employee_id):
        return get_object_or_404(
            Employee.objects.select_related(
                "employment_details",
                "employment_details__department",
                "employment_details__department__parent_department",
                "employment_details__designation",
                "employment_details__employee_type",
                "employment_details__category",
                "employment_details__grade",
                "employment_details__office_location",
                "employment_details__shift",
                "employment_details__source_of_hire",
                "lifecycle",
            ).prefetch_related("reporting_relationships__reports_to_employee"),
            pk=employee_id,
        )

    def get_response_payload(self, employee):
        return build_employment_details(employee)

    def apply_data(self, employee, data):
        apply_employment_details(employee, data)


@extend_schema_view(
    get=extend_schema(summary="Get employee language details (Admin)"),
    patch=extend_schema(
        summary="Update employee language details (Admin)",
        request=LanguageDetailsSubmitSerializer,
    ),
)
class EmployeeLanguageDetailsAdminView(_AdminSectionView):
    serializer_class = LanguageDetailsSubmitSerializer
    response_key = "language_details"
    module = None

    def get_employee(self, employee_id):
        return get_object_or_404(
            Employee.objects.prefetch_related(
                "language_proficiencies__language",
                "language_proficiencies__read_proficiency",
                "language_proficiencies__write_proficiency",
                "language_proficiencies__speak_proficiency",
            ),
            pk=employee_id,
        )

    def get_response_payload(self, employee):
        return build_language_details(employee)

    def apply_data(self, employee, data):
        apply_language_details(employee, data)


@extend_schema_view(
    get=extend_schema(summary="Get employee medical details (Admin)"),
    patch=extend_schema(
        summary="Update employee medical details (Admin)",
        request=MedicalDetailsSubmitSerializer,
    ),
)
class EmployeeMedicalDetailsAdminView(_AdminSectionView):
    serializer_class = MedicalDetailsSubmitSerializer
    response_key = "medical_details"
    module = ESSModule.MEDICAL

    def get_response_payload(self, employee):
        return build_medical_details(employee)

    def apply_data(self, employee, data):
        apply_medical_details(employee, data)


@extend_schema_view(
    get=extend_schema(summary="List employee insurance policies (Admin)"),
    post=extend_schema(
        summary="Create employee insurance policy (Admin)",
        request=AdminInsurancePolicySerializer,
    ),
    patch=extend_schema(
        summary="Replace/update employee insurance policies (Admin)",
        request=AdminInsurancePolicyListSerializer,
    ),
)
class EmployeeInsuranceDetailsAdminView(APIView):
    """
    GET   /api/admin/employees/<employee_id>/insurance-details/
    POST  /api/admin/employees/<employee_id>/insurance-details/
    PATCH /api/admin/employees/<employee_id>/insurance-details/
    """

    serializer_class = AdminInsurancePolicyListSerializer
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
        "PATCH": ["employee.edit_employee"],
    }

    def get_employee(self, employee_id):
        return get_object_or_404(Employee, pk=employee_id)

    def get(self, request, employee_id):
        employee = self.get_employee(employee_id)
        return Response({"insurance_details": list_employee_insurance_policies(employee)})

    def post(self, request, employee_id):
        employee = self.get_employee(employee_id)
        serializer = AdminInsurancePolicySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            policy = create_employee_insurance_policy(employee, serializer.validated_data)
        except Exception as exc:
            if hasattr(exc, "detail"):
                return _validation_error_response(exc)
            raise
        return Response(
            {"insurance_policy": policy},
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request, employee_id):
        employee = self.get_employee(employee_id)
        serializer = AdminInsurancePolicyListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = []
        try:
            for row in serializer.validated_data["insurance_details"]:
                policy_id = row.get("id")
                if policy_id:
                    updated.append(update_employee_insurance_policy(employee, policy_id, row))
                else:
                    updated.append(create_employee_insurance_policy(employee, row))
        except Exception as exc:
            if hasattr(exc, "detail"):
                return _validation_error_response(exc)
            raise
        return Response({"insurance_details": updated})


@extend_schema_view(
    get=extend_schema(summary="Get employee insurance policy (Admin)"),
    post=extend_schema(
        summary="Update employee insurance policy (Admin, compatibility)",
        request=AdminInsurancePolicySerializer,
    ),
    patch=extend_schema(
        summary="Update employee insurance policy (Admin)",
        request=AdminInsurancePolicySerializer,
    ),
    delete=extend_schema(summary="Remove employee insurance policy (Admin)"),
)
class EmployeeInsurancePolicyAdminView(APIView):
    """
    GET    /api/admin/employees/<employee_id>/insurance-details/<policy_id>/
    POST   /api/admin/employees/<employee_id>/insurance-details/<policy_id>/
    PATCH  /api/admin/employees/<employee_id>/insurance-details/<policy_id>/
    DELETE /api/admin/employees/<employee_id>/insurance-details/<policy_id>/
    """

    serializer_class = AdminInsurancePolicySerializer
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions_by_method = {
        "GET": ["employee.view_employee"],
        "POST": ["employee.edit_employee"],
        "PATCH": ["employee.edit_employee"],
        "DELETE": ["employee.delete_employee"],
    }

    def get_employee(self, employee_id):
        return get_object_or_404(Employee, pk=employee_id)

    def get(self, request, employee_id, policy_id):
        employee = self.get_employee(employee_id)
        return Response({"insurance_policy": get_employee_insurance_policy(employee, policy_id)})

    def patch(self, request, employee_id, policy_id):
        employee = self.get_employee(employee_id)
        serializer = AdminInsurancePolicySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            policy = update_employee_insurance_policy(
                employee,
                policy_id,
                serializer.validated_data,
            )
        except Exception as exc:
            if hasattr(exc, "detail"):
                return _validation_error_response(exc)
            raise
        return Response({"insurance_policy": policy})

    def post(self, request, employee_id, policy_id):
        return self.patch(request, employee_id, policy_id)

    def delete(self, request, employee_id, policy_id):
        employee = self.get_employee(employee_id)
        delete_employee_insurance_policy(employee, policy_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
