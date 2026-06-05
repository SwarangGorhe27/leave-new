from rest_framework import serializers

from apps.employees.models import (
    Employee,
    EmployeeAddress,
    EmployeeBankAccount,
    EmployeeDocument,
    EmployeeEducation,
    EmployeeEmploymentDetails,
    EmployeeFamilyMember,
    EmployeeInsurancePolicy,
    EmployeeLanguageProficiency,
    EmployeeNominee,
    EmployeePersonalDetails,
)


class PersonalDetailsReadSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="employee.first_name", read_only=True)
    middle_name = serializers.CharField(source="employee.middle_name", read_only=True, allow_null=True)
    last_name = serializers.CharField(source="employee.last_name", read_only=True)
    date_of_birth = serializers.DateField(source="employee.date_of_birth", read_only=True)
    actual_dob = serializers.DateField(source="employee.wish_on_date", read_only=True, allow_null=True)
    actual_date_of_birth = serializers.DateField(source="employee.wish_on_date", read_only=True, allow_null=True)
    joining_date = serializers.DateField(source="employee.date_of_joining", read_only=True)
    gender_id = serializers.IntegerField(source="employee.gender_id", read_only=True)
    gender = serializers.SerializerMethodField()
    marital_status_id = serializers.IntegerField(read_only=True, allow_null=True)
    marital_status = serializers.SerializerMethodField()
    religion_id = serializers.IntegerField(read_only=True, allow_null=True)
    religion = serializers.SerializerMethodField()
    caste_id = serializers.IntegerField(read_only=True, allow_null=True)
    caste = serializers.SerializerMethodField()
    caste_category_id = serializers.IntegerField(read_only=True, allow_null=True)
    caste_category = serializers.SerializerMethodField()
    blood_group_id = serializers.IntegerField(read_only=True, allow_null=True)
    blood_group = serializers.SerializerMethodField()
    nationality_id = serializers.IntegerField(read_only=True, allow_null=True)
    nationality = serializers.SerializerMethodField()
    height = serializers.DecimalField(
        source="height_cm",
        max_digits=5,
        decimal_places=1,
        read_only=True,
        allow_null=True,
    )
    weight = serializers.DecimalField(
        source="weight_kg",
        max_digits=5,
        decimal_places=1,
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = EmployeePersonalDetails
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "father_name",
            "spouse_name",
            "date_of_birth",
            "actual_dob",
            "actual_date_of_birth",
            "place_of_birth",
            "gender_id",
            "gender",
            "marital_status_id",
            "marital_status",
            "blood_group_id",
            "blood_group",
            "nationality_id",
            "nationality",
            "religion_id",
            "religion",
            "caste_id",
            "caste",
            "caste_category_id",
            "caste_category",
            "identification_mark",
            "height",
            "height_cm",
            "weight",
            "weight_kg",
            "is_physically_challenged",
            "is_international_employee",
            "joining_date",
        ]

    def _master_label(self, obj):
        if obj is None:
            return None
        return getattr(obj, "name", None) or getattr(obj, "label", None)

    def get_gender(self, obj):
        return self._master_label(getattr(obj.employee, "gender", None))

    def get_marital_status(self, obj):
        return self._master_label(obj.marital_status)

    def get_religion(self, obj):
        return self._master_label(obj.religion)

    def get_caste(self, obj):
        return self._master_label(obj.caste)

    def get_caste_category(self, obj):
        return self._master_label(obj.caste_category)

    def get_blood_group(self, obj):
        return self._master_label(obj.blood_group)

    def get_nationality(self, obj):
        return self._master_label(obj.nationality)


class EmploymentDetailsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeEmploymentDetails
        fields = "__all__"


class AddressReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAddress
        fields = "__all__"


class FamilyMemberReadSerializer(serializers.ModelSerializer):
    """Serializer for family member - showing only essential fields for frontend UI."""
    
    # Display nested objects for dropdowns
    relation = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    blood_group = serializers.SerializerMethodField()
    occupation = serializers.SerializerMethodField()
    relationship_id = serializers.IntegerField(source="relation_id", read_only=True)
    relationship = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    age_years = serializers.SerializerMethodField()
    
    # Format phone field
    phone = serializers.CharField(source="mobile_no", read_only=True)
    
    class Meta:
        model = EmployeeFamilyMember
        fields = [
            "id",
            "first_name",
            "last_name",
            "date_of_birth",
            "age",
            "age_years",
            "relationship_id",
            "relationship",
            "relation",
            "gender",
            "blood_group",
            "occupation",
            "phone",
            "email",
            "is_dependent",
            "is_nominee",
        ]
    
    def get_relation(self, obj):
        """Return relation as dict with id and label."""
        if obj.relation:
            return {
                "id": obj.relation.id,
                "label": obj.relation.label,
                "code": obj.relation.code,
            }
        return None

    def get_relationship(self, obj):
        """Return relationship label for card UI."""
        if obj.relation:
            return obj.relation.label
        return None

    def get_age_years(self, obj):
        """Return age in completed years."""
        if not obj.date_of_birth:
            return None
        from datetime import date

        today = date.today()
        return today.year - obj.date_of_birth.year - (
            (today.month, today.day)
            < (obj.date_of_birth.month, obj.date_of_birth.day)
        )

    def get_age(self, obj):
        """Return age display used by family card UI."""
        age_years = self.get_age_years(obj)
        if age_years is None:
            return None
        return f"{age_years} Years"
    
    def get_gender(self, obj):
        """Return gender as dict with id and label."""
        if obj.gender:
            return {
                "id": obj.gender.id,
                "label": obj.gender.label,
                "code": obj.gender.code,
            }
        return None
    
    def get_blood_group(self, obj):
        """Return blood group as dict with id and label."""
        if obj.blood_group:
            return {
                "id": obj.blood_group.id,
                "label": obj.blood_group.label,
                "code": obj.blood_group.code,
            }
        return None
    
    def get_occupation(self, obj):
        """Return occupation as dict with id and label."""
        if obj.occupation:
            return {
                "id": obj.occupation.id,
                "label": obj.occupation.label,
                "code": obj.occupation.code,
            }
        return None


class EducationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeEducation
        fields = "__all__"


class BankAccountReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeBankAccount
        fields = "__all__"


class NomineeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeNominee
        fields = "__all__"


class InsuranceReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeInsurancePolicy
        fields = "__all__"


class LanguageReadSerializer(serializers.ModelSerializer):
    language_id = serializers.IntegerField(read_only=True)
    language = serializers.SerializerMethodField()
    read_proficiency_id = serializers.IntegerField(read_only=True)
    read_proficiency = serializers.SerializerMethodField()
    write_proficiency_id = serializers.IntegerField(read_only=True)
    write_proficiency = serializers.SerializerMethodField()
    speak_proficiency_id = serializers.IntegerField(read_only=True)
    speak_proficiency = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeLanguageProficiency
        fields = [
            "id",
            "employee",
            "language_id",
            "language",
            "read_proficiency_id",
            "read_proficiency",
            "write_proficiency_id",
            "write_proficiency",
            "speak_proficiency_id",
            "speak_proficiency",
            "is_mother_tongue",
            "is_active",
        ]

    def _master_value(self, obj):
        if obj is None:
            return None
        return {
            "id": obj.id,
            "label": getattr(obj, "label", None) or getattr(obj, "name", None),
            "code": getattr(obj, "code", None),
        }

    def get_language(self, obj):
        return self._master_value(obj.language)

    def get_read_proficiency(self, obj):
        return self._master_value(obj.read_proficiency)

    def get_write_proficiency(self, obj):
        return self._master_value(obj.write_proficiency)

    def get_speak_proficiency(self, obj):
        return self._master_value(obj.speak_proficiency)


class DocumentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = "__all__"


class MyFullProfileSerializer(serializers.ModelSerializer):
    personal_details = PersonalDetailsReadSerializer(read_only=True)
    employment_details = EmploymentDetailsReadSerializer(read_only=True)
    addresses = AddressReadSerializer(many=True, read_only=True)
    family_members = FamilyMemberReadSerializer(many=True, read_only=True)
    education_records = EducationReadSerializer(many=True, read_only=True)
    bank_accounts = BankAccountReadSerializer(many=True, read_only=True)
    nominees = NomineeReadSerializer(many=True, read_only=True)
    insurance_policies = InsuranceReadSerializer(many=True, read_only=True)
    language_proficiencies = LanguageReadSerializer(many=True, read_only=True)
    documents = DocumentReadSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = "__all__"
