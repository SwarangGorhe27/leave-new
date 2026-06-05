"""
Employee Asset serializers for admin employee details.

Security Note: All serializers use Django ORM parameterized queries only.
No raw SQL is used to prevent SQL injection attacks.
"""

from rest_framework import serializers
from datetime import date

from apps.employees.models.assets import EmployeeAsset
from apps.employees.models.masters.performance_training import AssetCategory, AssetCondition
from apps.employees.models.employee import Employee


class EmployeeAssetDetailSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for EmployeeAsset.
    Used for retrieving and displaying employee asset assignments.
    """
    employee_name = serializers.SerializerMethodField()
    asset_category_code = serializers.CharField(source="asset_category.code", read_only=True)
    asset_category_label = serializers.CharField(source="asset_category.name", read_only=True)
    asset_condition_code = serializers.CharField(source="asset_condition.code", read_only=True, allow_null=True)
    asset_condition_label = serializers.CharField(source="asset_condition.name", read_only=True, allow_null=True)
    
    # CamelCase aliases for frontend compatibility
    assetName = serializers.CharField(source="asset_name", read_only=True)
    assetId = serializers.CharField(source="asset_code", read_only=True)
    assetCategory = serializers.UUIDField(source="asset_category_id", read_only=True)
    assetCategoryLabel = serializers.CharField(source="asset_category.name", read_only=True)
    serialNumber = serializers.CharField(source="serial_no", read_only=True)
    assignDate = serializers.DateField(source="assign_date", read_only=True)
    returnDate = serializers.DateField(source="return_date", read_only=True)
    assetCondition = serializers.UUIDField(source="asset_condition_id", read_only=True, allow_null=True)
    assetConditionLabel = serializers.CharField(source="asset_condition.name", read_only=True, allow_null=True)

    class Meta:
        model = EmployeeAsset
        fields = [
            "id",
            "employee",
            "employee_name",
            "asset_name",
            "asset_code",
            "asset_category",
            "asset_category_code",
            "asset_category_label",
            "serial_no",
            "assign_date",
            "return_date",
            "asset_condition",
            "asset_condition_code",
            "asset_condition_label",
            "status",
            "remarks",
            "is_active",
            "created_at",
            "updated_at",
            
            # frontend camelcase
            "assetName",
            "assetId",
            "assetCategory",
            "assetCategoryLabel",
            "serialNumber",
            "assignDate",
            "returnDate",
            "assetCondition",
            "assetConditionLabel",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        """Return employee full name."""
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None


class EmployeeAssetCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Write serializer for EmployeeAsset.
    Handles creation and updates with thorough validation.
    """
    # Accept standard snake_case and camelCase field aliases
    assetName = serializers.CharField(
        source="asset_name",
        required=False,
        max_length=150,
        allow_blank=False,
    )
    assetId = serializers.CharField(
        source="asset_code",
        required=False,
        max_length=50,
        allow_blank=True,
        allow_null=True,
    )
    assetCategory = serializers.PrimaryKeyRelatedField(
        source="asset_category",
        queryset=AssetCategory.objects.filter(is_active=True),
        required=False,
    )
    serialNumber = serializers.CharField(
        source="serial_no",
        required=False,
        max_length=100,
        allow_blank=True,
        allow_null=True,
    )
    assignDate = serializers.DateField(
        source="assign_date",
        required=False,
    )
    returnDate = serializers.DateField(
        source="return_date",
        required=False,
        allow_null=True,
    )
    assetCondition = serializers.PrimaryKeyRelatedField(
        source="asset_condition",
        queryset=AssetCondition.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    
    # Explicitly use CharField to allow case-insensitive validation
    status = serializers.CharField(required=False)

    class Meta:
        model = EmployeeAsset
        fields = [
            "asset_name",
            "asset_code",
            "asset_category",
            "serial_no",
            "assign_date",
            "return_date",
            "asset_condition",
            "status",
            "remarks",
            
            # camelcase fields
            "assetName",
            "assetId",
            "assetCategory",
            "serialNumber",
            "assignDate",
            "returnDate",
            "assetCondition",
        ]
        extra_kwargs = {
            "asset_name": {"required": False},
            "asset_category": {"required": False},
            "assign_date": {"required": False},
        }

    def validate_asset_name(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Asset name cannot be empty.")
        return value.strip()

    def validate_asset_code(self, value):
        if value:
            return value.strip()
        return value

    def validate_serial_no(self, value):
        if value:
            return value.strip()
        return value

    def validate_assign_date(self, value):
        if value and value < date.today():
            raise serializers.ValidationError(
                "Assign date must be today or a future date."
            )
        return value

    def validate_return_date(self, value):
        if value and value < date.today():
            raise serializers.ValidationError(
                "Return date must be today or a future date."
            )
        return value

    def validate_status(self, value):
        if value in (None, ""):
            return value
        normalized = str(value).strip().upper().replace(" ", "_")
        valid = {choice.value for choice in EmployeeAsset.StatusChoices}
        if normalized not in valid:
            raise serializers.ValidationError(
                f"Invalid status. Allowed values: {', '.join(sorted(valid))}."
            )
        return normalized

    def validate(self, data):
        """
        Overall validation including dates.
        """
        instance = getattr(self, "instance", None)
        assign_date = data.get("assign_date")
        return_date = data.get("return_date")
        assign_date_provided = "assign_date" in data or "assignDate" in getattr(self, "initial_data", {})
        return_date_provided = "return_date" in data or "returnDate" in getattr(self, "initial_data", {})

        if self.partial and instance is not None:
            if assign_date is None:
                assign_date = instance.assign_date
            if return_date is None and not return_date_provided:
                return_date = instance.return_date

        if not data.get("status"):
            data["status"] = EmployeeAsset.StatusChoices.ASSIGNED

        if not self.partial:
            if not data.get("asset_name"):
                raise serializers.ValidationError({"assetName": "Asset name is required."})
            if not data.get("asset_category"):
                raise serializers.ValidationError({"assetCategory": "Asset category is required."})
            if not data.get("assign_date"):
                raise serializers.ValidationError({"assignDate": "Assign date is required."})

        if (not self.partial or assign_date_provided) and assign_date and assign_date < date.today():
            raise serializers.ValidationError({
                "assignDate": "Assign date must be today or a future date."
            })

        if return_date_provided and return_date and return_date < date.today():
            raise serializers.ValidationError({
                "returnDate": "Return date must be today or a future date."
            })

        if assign_date and return_date and return_date < assign_date:
            raise serializers.ValidationError({
                "returnDate": "Return date must be on or after the assign date."
            })

        return data
