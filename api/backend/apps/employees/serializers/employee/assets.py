"""Serializers for Employee Assets"""

from rest_framework import serializers

from apps.employees.models import EmployeeAsset


class AssetReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for employee assets"""

    asset_category_name = serializers.CharField(
        source="asset_category.label", read_only=True, allow_null=True
    )
    asset_condition_name = serializers.CharField(
        source="asset_condition.label", read_only=True, allow_null=True
    )

    class Meta:
        model = EmployeeAsset
        fields = [
            "id",
            "asset_name",
            "asset_code",
            "asset_category",
            "asset_category_name",
            "serial_no",
            "assign_date",
            "return_date",
            "asset_condition",
            "asset_condition_name",
            "status",
            "remarks",
            "created_at",
        ]
        read_only_fields = fields
