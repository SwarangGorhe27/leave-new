"""
Admin serializers for employee salary page.
"""

from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from apps.employees.models.salary import EmployeeSalary


MONEY_MAX = Decimal("999999999999.99")


def _money(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise serializers.ValidationError("Enter a valid amount.")
    if amount < 0:
        raise serializers.ValidationError("Amount cannot be negative.")
    if amount > MONEY_MAX:
        raise serializers.ValidationError("Amount is too large.")
    return amount.quantize(Decimal("0.01"))


class EmployeeSalarySerializer(serializers.ModelSerializer):
    basicSalary = serializers.DecimalField(source="basic_salary", max_digits=14, decimal_places=2, read_only=True)
    houseRentAllowance = serializers.DecimalField(source="house_rent_allowance", max_digits=14, decimal_places=2, read_only=True)
    conveyanceAllowance = serializers.DecimalField(source="conveyance_allowance", max_digits=14, decimal_places=2, read_only=True)
    medicalAllowance = serializers.DecimalField(source="medical_allowance", max_digits=14, decimal_places=2, read_only=True)
    specialAllowance = serializers.DecimalField(source="special_allowance", max_digits=14, decimal_places=2, read_only=True)
    providentFund = serializers.DecimalField(source="provident_fund", max_digits=14, decimal_places=2, read_only=True)
    taxDeductedAtSource = serializers.DecimalField(source="tax_deducted_at_source", max_digits=14, decimal_places=2, read_only=True)
    grossSalary = serializers.DecimalField(source="gross_salary", max_digits=14, decimal_places=2, read_only=True)
    totalDeductions = serializers.DecimalField(source="total_deductions", max_digits=14, decimal_places=2, read_only=True)
    netSalary = serializers.DecimalField(source="net_salary", max_digits=14, decimal_places=2, read_only=True)
    annualCtc = serializers.DecimalField(source="annual_ctc", max_digits=14, decimal_places=2, read_only=True)
    payFrequency = serializers.CharField(source="pay_frequency", read_only=True)
    effectiveFrom = serializers.DateField(source="effective_from", read_only=True)
    effectiveTo = serializers.DateField(source="effective_to", read_only=True)
    summaryCards = serializers.SerializerMethodField()
    earnings = serializers.SerializerMethodField()
    deductions = serializers.SerializerMethodField()
    annualCtcCard = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeSalary
        fields = [
            "id",
            "employee",
            "currency",
            "payFrequency",
            "basicSalary",
            "houseRentAllowance",
            "conveyanceAllowance",
            "medicalAllowance",
            "specialAllowance",
            "providentFund",
            "taxDeductedAtSource",
            "grossSalary",
            "totalDeductions",
            "netSalary",
            "annualCtc",
            "remarks",
            "effectiveFrom",
            "effectiveTo",
            "summaryCards",
            "earnings",
            "deductions",
            "annualCtcCard",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_summaryCards(self, obj):
        period = "Per Month" if obj.pay_frequency == "MONTHLY" else "Per Year"
        return [
            {
                "key": "grossSalary",
                "title": "Gross Salary",
                "amount": obj.gross_salary,
                "caption": period,
                "editable": True,
            },
            {
                "key": "totalDeductions",
                "title": "Total Deductions",
                "amount": obj.total_deductions,
                "caption": "PF + TDS",
                "editable": True,
            },
            {
                "key": "netSalary",
                "title": "Net Salary",
                "amount": obj.net_salary,
                "caption": "Take Home",
                "editable": False,
            },
        ]

    def get_earnings(self, obj):
        items = [
            ("basicSalary", "Basic Salary", obj.basic_salary),
            ("houseRentAllowance", "House Rent Allowance (HRA)", obj.house_rent_allowance),
            ("conveyanceAllowance", "Conveyance Allowance", obj.conveyance_allowance),
            ("medicalAllowance", "Medical Allowance", obj.medical_allowance),
            ("specialAllowance", "Special Allowance", obj.special_allowance),
        ]
        return {
            "title": "Earnings",
            "items": [{"key": key, "label": label, "amount": amount, "editable": True} for key, label, amount in items],
            "total": {"key": "grossSalary", "label": "Gross Earnings", "amount": obj.gross_salary},
        }

    def get_deductions(self, obj):
        items = [
            ("providentFund", "Provident Fund (PF)", obj.provident_fund),
            ("taxDeductedAtSource", "Tax Deducted at Source (TDS)", obj.tax_deducted_at_source),
        ]
        return {
            "title": "Deductions",
            "items": [{"key": key, "label": label, "amount": amount, "editable": True} for key, label, amount in items],
            "total": {"key": "totalDeductions", "label": "Total Deductions", "amount": obj.total_deductions},
            "netTakeHome": {
                "key": "netSalary",
                "label": "Net Take Home",
                "amount": obj.net_salary,
                "caption": "After all deductions",
            },
        }

    def get_annualCtcCard(self, obj):
        return {
            "key": "annualCtc",
            "title": "Annual CTC",
            "caption": f"Cost to Company per year ({obj.currency})",
            "amount": obj.annual_ctc,
            "editable": False,
        }


class EmployeeSalaryWriteSerializer(serializers.Serializer):
    basicSalary = serializers.CharField(required=False)
    houseRentAllowance = serializers.CharField(required=False)
    conveyanceAllowance = serializers.CharField(required=False)
    medicalAllowance = serializers.CharField(required=False)
    specialAllowance = serializers.CharField(required=False)
    providentFund = serializers.CharField(required=False)
    taxDeductedAtSource = serializers.CharField(required=False)
    currency = serializers.CharField(required=False, max_length=3)
    payFrequency = serializers.ChoiceField(required=False, choices=EmployeeSalary.PayFrequency.choices)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    effectiveFrom = serializers.DateField(required=False, allow_null=True)
    effectiveTo = serializers.DateField(required=False, allow_null=True)

    def validate_basicSalary(self, value): return _money(value)
    def validate_houseRentAllowance(self, value): return _money(value)
    def validate_conveyanceAllowance(self, value): return _money(value)
    def validate_medicalAllowance(self, value): return _money(value)
    def validate_specialAllowance(self, value): return _money(value)
    def validate_providentFund(self, value): return _money(value)
    def validate_taxDeductedAtSource(self, value): return _money(value)

    def validate_currency(self, value):
        cleaned = str(value or "").strip().upper()
        if len(cleaned) != 3 or not cleaned.isalpha():
            raise serializers.ValidationError("Currency must be a 3-letter ISO code.")
        return cleaned

    def validate(self, attrs):
        if not self.partial:
            required = {
                "basicSalary",
                "houseRentAllowance",
                "conveyanceAllowance",
                "medicalAllowance",
                "specialAllowance",
                "providentFund",
                "taxDeductedAtSource",
            }
            missing = sorted(required - set(attrs.keys()))
            if missing:
                raise serializers.ValidationError({
                    field: "This field is required." for field in missing
                })

        instance = self.context.get("instance")
        values = {
            "basicSalary": attrs.get("basicSalary", getattr(instance, "basic_salary", Decimal("0.00"))),
            "houseRentAllowance": attrs.get("houseRentAllowance", getattr(instance, "house_rent_allowance", Decimal("0.00"))),
            "conveyanceAllowance": attrs.get("conveyanceAllowance", getattr(instance, "conveyance_allowance", Decimal("0.00"))),
            "medicalAllowance": attrs.get("medicalAllowance", getattr(instance, "medical_allowance", Decimal("0.00"))),
            "specialAllowance": attrs.get("specialAllowance", getattr(instance, "special_allowance", Decimal("0.00"))),
            "providentFund": attrs.get("providentFund", getattr(instance, "provident_fund", Decimal("0.00"))),
            "taxDeductedAtSource": attrs.get("taxDeductedAtSource", getattr(instance, "tax_deducted_at_source", Decimal("0.00"))),
        }
        gross = (
            values["basicSalary"]
            + values["houseRentAllowance"]
            + values["conveyanceAllowance"]
            + values["medicalAllowance"]
            + values["specialAllowance"]
        )
        deductions = values["providentFund"] + values["taxDeductedAtSource"]
        if deductions > gross:
            raise serializers.ValidationError({
                "totalDeductions": "Total deductions cannot be greater than gross earnings."
            })

        effective_from = attrs.get("effectiveFrom")
        effective_to = attrs.get("effectiveTo")
        if instance:
            effective_from = effective_from if "effectiveFrom" in attrs else instance.effective_from
            effective_to = effective_to if "effectiveTo" in attrs else instance.effective_to
        if effective_from and effective_to and effective_to < effective_from:
            raise serializers.ValidationError({
                "effectiveTo": "Effective to date must be on or after effective from date."
            })

        return attrs
