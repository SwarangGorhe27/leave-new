"""ViewSets for audit-addition master APIs."""

from rest_framework.decorators import action
from rest_framework.response import Response

from apps.employees.models.masters.audit_additions import (
    AuthorizedSignatory,
    BulletinCategory,
    ClearanceItemType,
    ContractStatus,
    CounterParty,
    EmployeeFilter,
    FormCategory,
    ImportType,
    LetterApprovalType,
    PaymentType,
    PolicyCategory,
    PositionChangeReason,
    ReportingManager,
    ResidentialStatus,
    SeparationMode,
    VerificationStatus,
)
from apps.masters.serializers.audit_additions import (
    AuthorizedSignatoryListSerializer,
    AuthorizedSignatorySerializer,
    BulletinCategoryListSerializer,
    BulletinCategorySerializer,
    ClearanceItemTypeListSerializer,
    ClearanceItemTypeSerializer,
    ContractStatusListSerializer,
    ContractStatusSerializer,
    CounterPartyListSerializer,
    CounterPartySerializer,
    EmployeeFilterListSerializer,
    EmployeeFilterSerializer,
    FormCategoryListSerializer,
    FormCategorySerializer,
    ImportTypeListSerializer,
    ImportTypeSerializer,
    LetterApprovalTypeListSerializer,
    LetterApprovalTypeSerializer,
    PaymentTypeListSerializer,
    PaymentTypeSerializer,
    PolicyCategoryListSerializer,
    PolicyCategorySerializer,
    PositionChangeReasonListSerializer,
    PositionChangeReasonSerializer,
    ReportingManagerListSerializer,
    ReportingManagerSerializer,
    ResidentialStatusListSerializer,
    ResidentialStatusSerializer,
    SeparationModeListSerializer,
    SeparationModeSerializer,
    VerificationStatusListSerializer,
    VerificationStatusSerializer,
)
from apps.masters.views.base import ActiveMasterViewSet
"""Master ViewSets for audit/additional employee setup tables."""

from rest_framework import serializers

from apps.employees.models.masters.audit_additions import VerificationStatus


def _bool_param(request, name):
    value = request.query_params.get(name, "").lower()
    if value in ("true", "false"):
        return value == "true"
    return None


def _actor_employee_id(request):
    user = getattr(request, "user", None)
    employee = getattr(user, "employee_profile", None)
    return getattr(employee, "id", None)


class AuditAdditionMasterViewSet(ActiveMasterViewSet):
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
    search_lookup_fields = ("code", "name")
    display_field = "name"

    def perform_create(self, serializer):
        actor_id = _actor_employee_id(self.request)
        save_kwargs = {}
        if actor_id:
            save_kwargs["created_by"] = actor_id
            save_kwargs["updated_by"] = actor_id
        serializer.save(**save_kwargs)

    def perform_update(self, serializer):
        actor_id = _actor_employee_id(self.request)
        if actor_id:
            serializer.save(updated_by=actor_id)
            return
        serializer.save()


class CompanyFilteredMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        return qs


class SeparationModeViewSet(AuditAdditionMasterViewSet):
    queryset = SeparationMode.objects.all()
    serializer_class = SeparationModeSerializer
    list_serializer_class = SeparationModeListSerializer
    ordering = ["sort_order", "name"]
    ordering_fields = ["code", "name", "sort_order", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        for flag in ("is_voluntary", "is_terminal"):
            value = _bool_param(self.request, flag)
            if value is not None:
                qs = qs.filter(**{flag: value})
        return qs


class ContractStatusViewSet(AuditAdditionMasterViewSet):
    queryset = ContractStatus.objects.all()
    serializer_class = ContractStatusSerializer
    list_serializer_class = ContractStatusListSerializer
    ordering = ["sort_order", "name"]
    ordering_fields = ["code", "name", "sort_order", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        value = _bool_param(self.request, "is_terminal")
        if value is not None:
            qs = qs.filter(is_terminal=value)
        return qs


class VerificationStatusViewSet(AuditAdditionMasterViewSet):
    queryset = VerificationStatus.objects.all()
    serializer_class = VerificationStatusSerializer
    list_serializer_class = VerificationStatusListSerializer
    ordering = ["sort_order", "name"]
    ordering_fields = ["code", "name", "sort_order", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        for flag in ("is_positive", "is_terminal"):
            value = _bool_param(self.request, flag)
            if value is not None:
                qs = qs.filter(**{flag: value})
        return qs


class ResidentialStatusViewSet(AuditAdditionMasterViewSet):
    queryset = ResidentialStatus.objects.all()
    serializer_class = ResidentialStatusSerializer
    list_serializer_class = ResidentialStatusListSerializer


class PaymentTypeViewSet(AuditAdditionMasterViewSet):
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer
    list_serializer_class = PaymentTypeListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        for flag in ("requires_bank_account", "requires_ifsc"):
            value = _bool_param(self.request, flag)
            if value is not None:
                qs = qs.filter(**{flag: value})
        return qs


class EmployeeFilterViewSet(CompanyFilteredMixin, AuditAdditionMasterViewSet):
    queryset = EmployeeFilter.objects.all()
    serializer_class = EmployeeFilterSerializer
    list_serializer_class = EmployeeFilterListSerializer
    search_fields = ["code", "name", "description"]

    def get_queryset(self):
        qs = super().get_queryset()
        if filter_type := self.request.query_params.get("filter_type", "").upper():
            qs = qs.filter(filter_type=filter_type)
        value = _bool_param(self.request, "is_system")
        if value is not None:
            qs = qs.filter(is_system=value)
        return qs


class BulletinCategoryViewSet(CompanyFilteredMixin, AuditAdditionMasterViewSet):
    queryset = BulletinCategory.objects.all()
    serializer_class = BulletinCategorySerializer
    list_serializer_class = BulletinCategoryListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if context_type := self.request.query_params.get("context_type", "").upper():
            qs = qs.filter(context_type=context_type)
        return qs


class PolicyCategoryViewSet(CompanyFilteredMixin, AuditAdditionMasterViewSet):
    queryset = PolicyCategory.objects.all()
    serializer_class = PolicyCategorySerializer
    list_serializer_class = PolicyCategoryListSerializer
    ordering = ["sort_order", "name"]
    ordering_fields = ["code", "name", "sort_order", "created_at"]


class FormCategoryViewSet(CompanyFilteredMixin, AuditAdditionMasterViewSet):
    queryset = FormCategory.objects.all()
    serializer_class = FormCategorySerializer
    list_serializer_class = FormCategoryListSerializer


class ImportTypeViewSet(AuditAdditionMasterViewSet):
    queryset = ImportType.objects.all()
    serializer_class = ImportTypeSerializer
    list_serializer_class = ImportTypeListSerializer
    search_fields = ["code", "name", "module_category"]
    ordering = ["sort_order", "name"]
    ordering_fields = ["code", "name", "module_category", "sort_order", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if module_category := self.request.query_params.get("module_category"):
            qs = qs.filter(module_category__iexact=module_category)
        value = _bool_param(self.request, "requires_effective_date")
        if value is not None:
            qs = qs.filter(requires_effective_date=value)
        return qs


class LetterApprovalTypeViewSet(AuditAdditionMasterViewSet):
    queryset = LetterApprovalType.objects.all()
    serializer_class = LetterApprovalTypeSerializer
    list_serializer_class = LetterApprovalTypeListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        for flag in ("requires_digital_signature", "requires_approver"):
            value = _bool_param(self.request, flag)
            if value is not None:
                qs = qs.filter(**{flag: value})
        return qs


class ClearanceItemTypeViewSet(CompanyFilteredMixin, AuditAdditionMasterViewSet):
    queryset = ClearanceItemType.objects.all()
    serializer_class = ClearanceItemTypeSerializer
    list_serializer_class = ClearanceItemTypeListSerializer
    ordering = ["sort_order", "name"]
    ordering_fields = ["code", "name", "sort_order", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if department_id := self.request.query_params.get("responsible_department_id"):
            qs = qs.filter(responsible_department_id=department_id)
        return qs


class PositionChangeReasonViewSet(AuditAdditionMasterViewSet):
    queryset = PositionChangeReason.objects.all()
    serializer_class = PositionChangeReasonSerializer
    list_serializer_class = PositionChangeReasonListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if change_type := self.request.query_params.get("change_type", "").upper():
            qs = qs.filter(change_type=change_type)
        return qs


class CounterPartyViewSet(CompanyFilteredMixin, AuditAdditionMasterViewSet):
    queryset = CounterParty.objects.all()
    serializer_class = CounterPartySerializer
    list_serializer_class = CounterPartyListSerializer
    search_fields = ["code", "name", "gstin", "pan", "contact_email", "contact_phone"]

    def get_queryset(self):
        qs = super().get_queryset()
        if counter_party_type := self.request.query_params.get(
            "counter_party_type", ""
        ).upper():
            qs = qs.filter(counter_party_type=counter_party_type)
        return qs


class AuthorizedSignatoryViewSet(CompanyFilteredMixin, AuditAdditionMasterViewSet):
    queryset = AuthorizedSignatory.objects.all()
    serializer_class = AuthorizedSignatorySerializer
    list_serializer_class = AuthorizedSignatoryListSerializer
    search_fields = ["signatory_name", "signatory_title"]
    ordering_fields = ["signatory_name", "signatory_title", "created_at"]
    ordering = ["signatory_name"]
    search_lookup_fields = ("signatory_name", "signatory_title")
    display_field = "signatory_name"

    def get_queryset(self):
        qs = super().get_queryset()
        if employee_id := self.request.query_params.get("employee_id"):
            qs = qs.filter(employee_id=employee_id)
        return qs


class ReportingManagerViewSet(CompanyFilteredMixin, AuditAdditionMasterViewSet):
    queryset = ReportingManager.objects.select_related(
        "employee",
        "designation",
        "department",
    )
    serializer_class = ReportingManagerSerializer
    list_serializer_class = ReportingManagerListSerializer
    search_fields = [
        "employee__employee_code",
        "employee__first_name",
        "employee__middle_name",
        "employee__last_name",
        "designation__title",
        "department__name",
    ]
    ordering_fields = [
        "employee__employee_code",
        "designation__title",
        "department__name",
        "sort_order",
        "created_at",
    ]
    ordering = ["sort_order", "employee__employee_code"]
    search_lookup_fields = (
        "employee__employee_code",
        "employee__first_name",
        "employee__middle_name",
        "employee__last_name",
        "designation__title",
        "department__name",
    )
    display_field = "employee"

    def _select_related_fields(self):
        return ["employee", "designation", "department"]

    def _display_value(self, instance):
        return instance.employee.full_name

    def get_queryset(self):
        qs = super().get_queryset()
        if employee_id := self.request.query_params.get("employee_id"):
            qs = qs.filter(employee_id=employee_id)
        if designation_id := self.request.query_params.get("designation_id"):
            qs = qs.filter(designation_id=designation_id)
        if department_id := self.request.query_params.get("department_id"):
            qs = qs.filter(department_id=department_id)
        value = _bool_param(self.request, "is_primary")
        if value is not None:
            qs = qs.filter(is_primary=value)
        return qs

    @action(detail=False, methods=["get"])
    def simple_list(self, request):
        """Return active managers in a simplified format for dropdowns."""
        queryset = self.get_queryset().filter(is_active=True)
        
        managers = []
        for manager in queryset:
            managers.append({
                "id": str(manager.employee.id),
                "name": manager.employee.full_name,
                "employeeCode": manager.employee.employee_code,
                "designation": manager.designation.title if manager.designation else None,
                "department": manager.department.name if manager.department else None,
            })
        
        return Response({"results": managers})


class VerificationStatusListSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name", read_only=True)

    class Meta:
        model = VerificationStatus
        fields = [
            "id",
            "code",
            "name",
            "label",
            "is_positive",
            "is_terminal",
            "sort_order",
            "is_active",
        ]


class VerificationStatusSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name", read_only=True)

    class Meta:
        model = VerificationStatus
        fields = [
            "id",
            "code",
            "name",
            "label",
            "is_positive",
            "is_terminal",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
            "deleted_at",
            "meta_data",
            "meta_version",
            "created_by_system",
            "updated_by_system",
            "created_source",
            "updated_source",
            "meta_tags",
            "extra_attributes",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "deleted_at"]


# class VerificationStatusViewSet(ActiveMasterViewSet):
#     """ViewSet for background/document verification status master data."""

#     queryset = VerificationStatus.objects.all()
#     serializer_class = VerificationStatusSerializer
#     list_serializer_class = VerificationStatusListSerializer
#     search_fields = ["code", "name"]
#     search_lookup_fields = ("code", "name")
#     ordering_fields = ["sort_order", "code", "name", "created_at"]
#     ordering = ["sort_order", "name"]
#     display_field = "name"
