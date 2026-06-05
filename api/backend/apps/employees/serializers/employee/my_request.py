"""Employee My Request screen serializers."""

from rest_framework import serializers

from apps.employees.constants import ChangeRequestAction, ESSModule
from apps.employees.models import EmployeeChangeRequest
from apps.employees.serializers.employee.extended import ChangeRequestSubmitSerializer


REQUEST_SECTION_LABELS = {
    ESSModule.PROFILE: "All Profile Information",
    ESSModule.PERSONAL: "Personal Information",
    ESSModule.EMPLOYMENT: "Employment Details",
    ESSModule.ADDRESS: "Address Details",
    ESSModule.FAMILY: "Family Details",
    ESSModule.EDUCATION: "Education Details",
    ESSModule.BANK: "Bank / PF / ESI",
    ESSModule.NOMINEE: "Nominee Details",
    ESSModule.INSURANCE: "Insurance Details",
    ESSModule.LANGUAGE: "Language Details",
    ESSModule.PASSPORT: "Passport / Visa Details",
    ESSModule.EXPERIENCE: "Experience Details",
    ESSModule.SKILL: "Skill / Certification",
    ESSModule.DOCUMENT: "Document Details",
    ESSModule.MEDICAL: "Medical Details",
    ESSModule.SOCIAL: "Social Profile",
}

REQUEST_MODULE_CHOICES = [
    (module, REQUEST_SECTION_LABELS[module])
    for module in ESSModule.ALL
    if module in REQUEST_SECTION_LABELS
]


class MyRequestSubmitSerializer(serializers.Serializer):
    module = serializers.ChoiceField(choices=REQUEST_MODULE_CHOICES)
    description = serializers.CharField(max_length=1000)
    request_data = serializers.DictField(required=False, default=dict)
    action = serializers.ChoiceField(
        choices=[
            (ChangeRequestAction.CREATE, ChangeRequestAction.CREATE),
            (ChangeRequestAction.UPDATE, ChangeRequestAction.UPDATE),
            (ChangeRequestAction.DELETE, ChangeRequestAction.DELETE),
        ],
        default=ChangeRequestAction.UPDATE,
    )
    record_id = serializers.UUIDField(required=False, allow_null=True, default=None)

    def validate(self, attrs):
        request_data = attrs.get("request_data") or {}
        if not request_data:
            attrs["request_data"] = {
                "_request_only": True,
                "description": attrs["description"],
            }
            return attrs

        serializer = ChangeRequestSubmitSerializer(
            data={
                "module": attrs["module"],
                "action": attrs["action"],
                "request_data": request_data,
                "record_id": attrs.get("record_id"),
                "remarks": attrs["description"],
            }
        )
        serializer.is_valid(raise_exception=True)
        return attrs


class MyRequestUpdateSerializer(MyRequestSubmitSerializer):
    module = serializers.ChoiceField(choices=REQUEST_MODULE_CHOICES, required=False)
    description = serializers.CharField(max_length=1000, required=False)
    request_data = serializers.DictField(required=False)
    action = serializers.ChoiceField(
        choices=[
            (ChangeRequestAction.CREATE, ChangeRequestAction.CREATE),
            (ChangeRequestAction.UPDATE, ChangeRequestAction.UPDATE),
            (ChangeRequestAction.DELETE, ChangeRequestAction.DELETE),
        ],
        required=False,
    )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one field is required.")
        return attrs


class MyRequestListItemSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()
    submitted_at = serializers.DateTimeField(source="created_at")

    class Meta:
        model = EmployeeChangeRequest
        fields = [
            "id",
            "title",
            "section",
            "module",
            "action",
            "status",
            "message",
            "employee_remarks",
            "admin_remarks",
            "submitted_at",
            "reviewed_at",
            "updated_at",
        ]

    def get_title(self, obj):
        return REQUEST_SECTION_LABELS.get(obj.module, obj.get_module_display())

    def get_section(self, obj):
        return {
            "value": obj.module,
            "label": REQUEST_SECTION_LABELS.get(obj.module, obj.get_module_display()),
        }

    def get_message(self, obj):
        employee_name = getattr(obj.employee, "full_name", "") or "Employee"
        title = REQUEST_SECTION_LABELS.get(obj.module, obj.get_module_display()).lower()
        return f"{employee_name} submitted {title} for admin review."


class MyRequestDetailSerializer(MyRequestListItemSerializer):
    class Meta(MyRequestListItemSerializer.Meta):
        fields = MyRequestListItemSerializer.Meta.fields + [
            "request_data",
            "old_data",
            "record_id",
        ]
