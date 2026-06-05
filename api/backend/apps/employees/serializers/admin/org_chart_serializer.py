"""
Org chart serializers for admin APIs.
"""

from rest_framework import serializers


class NullableUUIDField(serializers.UUIDField):
    """UUID field that treats empty Swagger placeholders as null."""

    def to_internal_value(self, data):
        if data in (None, "", "|null", "null"):
            return None
        return super().to_internal_value(data)


class EmployeeSearchResultSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    employee_code = serializers.CharField()
    full_name = serializers.CharField()
    designation = serializers.CharField(allow_null=True)
    department = serializers.CharField(allow_null=True)
    team = serializers.CharField(allow_null=True)
    manager_id = serializers.UUIDField(allow_null=True)
    manager_name = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    profile_picture_url = serializers.CharField(allow_null=True)


class OrgChartNodeSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    employee_code = serializers.CharField()
    label = serializers.CharField()
    full_name = serializers.CharField()
    designation = serializers.CharField(allow_null=True)
    department = serializers.CharField(allow_null=True)
    team = serializers.CharField(allow_null=True)
    manager_id = serializers.UUIDField(allow_null=True)
    is_top_level = serializers.BooleanField(default=False)
    children = serializers.ListField(child=serializers.DictField(), default=list)


class OrgChartTreeSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    top_level_manager_id = serializers.UUIDField(allow_null=True)
    roots = serializers.ListField(child=serializers.DictField())
    nodes = serializers.ListField(child=serializers.DictField())
    edges = serializers.ListField(child=serializers.DictField())


class TopLevelManagerSerializer(serializers.Serializer):
    manager_id = serializers.UUIDField()


class AssignManagerSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField(
        help_text="Employee UUID to update.",
    )
    manager_id = NullableUUIDField(
        required=False,
        allow_null=True,
        help_text="Manager UUID, or null to clear the manager.",
    )


class MassTransferSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(
        required=False,
        help_text="Company UUID. Required when the tenant has multiple companies.",
    )
    from_manager_id = serializers.UUIDField()
    employee_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )
    to_manager_id = serializers.UUIDField()


class AssignManagerResponseSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    manager_id = serializers.CharField(allow_null=True)
    manager_name = serializers.CharField(allow_null=True)


class MassTransferResponseSerializer(serializers.Serializer):
    from_manager_id = serializers.CharField()
    to_manager_id = serializers.CharField()
    transferred_count = serializers.IntegerField()
    employee_ids = serializers.ListField(child=serializers.CharField())


class TopLevelManagerResponseSerializer(serializers.Serializer):
    company_id = serializers.CharField()
    top_level_manager_id = serializers.CharField()
    top_level_manager_name = serializers.CharField()


class OrgChartExportSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=["png", "pdf"])
    company_id = serializers.UUIDField(required=False)
    team = serializers.CharField(required=False, allow_blank=True)
    manager_id = serializers.UUIDField(required=False, allow_null=True)
    image_base64 = serializers.CharField(required=False, allow_blank=True)
