from rest_framework import serializers

from apps.employees.serializers.employee.medical_details import (
    MedicalDetailsPayloadSerializer,
)


# ---------------------------------------------------------------------------
# Address
# ---------------------------------------------------------------------------

class EmployeeProfileAddressSerializer(serializers.Serializer):
    address_line1 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address_line2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    landmark = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city_id = serializers.IntegerField(required=False, allow_null=True)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    state_id = serializers.IntegerField(required=False, allow_null=True)
    state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country_id = serializers.IntegerField(required=False, allow_null=True)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pincode = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    start_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    to_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_same_as_permanent = serializers.BooleanField(required=False, allow_null=True)


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

class EmployeeProfileContactSerializer(serializers.Serializer):
    official_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    personal_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    mobile_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    personal_mobile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    alternate_mobile_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    alternate_mobile_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_mobile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    extension_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    emergency_contact_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    # FIX 5: changed from UUIDField to IntegerField — emergency_contact_relation uses integer PK
    emergency_contact_relation_id = serializers.IntegerField(required=False, allow_null=True)
    emergency_contact_relation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    emergency_contact_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    emergency_contact_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    skype_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    linkedin_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)


# ---------------------------------------------------------------------------
# Personal Details
# ---------------------------------------------------------------------------

class EmployeeProfilePersonalDetailsSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date_of_birth = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    actual_dob = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    actual_date_of_birth = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    joining_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gender_id = serializers.IntegerField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    nationality_id = serializers.IntegerField(required=False, allow_null=True)
    nationality = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    marital_status_id = serializers.IntegerField(required=False, allow_null=True)
    marital_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    marriage_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    spouse_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    place_of_birth = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    residential_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    father_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    religion_id = serializers.IntegerField(required=False, allow_null=True)
    religion = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    caste_id = serializers.IntegerField(required=False, allow_null=True)
    caste = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    caste_category_id = serializers.IntegerField(required=False, allow_null=True)
    caste_category = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mother_tongue_id = serializers.IntegerField(required=False, allow_null=True)
    mother_tongue = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    native_place = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dietary_preference = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    house_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    blood_group_id = serializers.IntegerField(required=False, allow_null=True)
    blood_group = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_physically_challenged = serializers.BooleanField(required=False, allow_null=True)
    disability_details = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    height_cm = serializers.DecimalField(required=False, max_digits=5, decimal_places=1, allow_null=True)
    weight_kg = serializers.DecimalField(required=False, max_digits=5, decimal_places=1, allow_null=True)
    identification_mark = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pre_existing_diseases = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    undergone_major_surgery = serializers.BooleanField(required=False, allow_null=True)
    is_international_employee = serializers.BooleanField(required=False, allow_null=True)
    is_ex_serviceman = serializers.BooleanField(required=False, allow_null=True)
    hobby = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    highest_qualification_id = serializers.IntegerField(required=False, allow_null=True)
    highest_qualification = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    total_work_experience_months = serializers.IntegerField(required=False, allow_null=True)
    relevant_work_experience_months = serializers.IntegerField(required=False, allow_null=True)


# ---------------------------------------------------------------------------
# Employment Details
# ---------------------------------------------------------------------------

class EmployeeProfileEmploymentDetailsSerializer(serializers.Serializer):
    employee_type_id = serializers.IntegerField(required=False, allow_null=True)
    employee_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    employee_work_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    category = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    wages_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    department = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    designation_id = serializers.UUIDField(required=False, allow_null=True)
    designation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    grade_id = serializers.UUIDField(required=False, allow_null=True)
    grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    shift_id = serializers.UUIDField(required=False, allow_null=True)
    shift = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_location_id = serializers.IntegerField(required=False, allow_null=True)
    work_location = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_of_hire_id = serializers.IntegerField(required=False, allow_null=True)
    source_of_hire = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    payroll_status_id = serializers.IntegerField(required=False, allow_null=True)
    payroll_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    transport_type_id = serializers.IntegerField(required=False, allow_null=True)
    transport_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    payroll_frequency = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    payment_mode = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    notice_period_days = serializers.IntegerField(required=False, allow_null=True)
    cost_center = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profit_center = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    function = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    wing = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    zone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    cadre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    batch = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    team = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    client = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    acquisition = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    biometric_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    holiday_list_id = serializers.UUIDField(required=False, allow_null=True)


class EmployeeProfileFamilyDetailsSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True, allow_null=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True, allow_null=True)
    relation_id = serializers.IntegerField(read_only=True, allow_null=True)
    relation = serializers.CharField(read_only=True, allow_null=True)
    date_of_birth = serializers.CharField(read_only=True, allow_null=True)
    gender_id = serializers.IntegerField(read_only=True, allow_null=True)
    gender = serializers.CharField(read_only=True, allow_null=True)
    blood_group_id = serializers.IntegerField(read_only=True, allow_null=True)
    blood_group = serializers.CharField(read_only=True, allow_null=True)
    phone = serializers.CharField(read_only=True, allow_null=True)
    mobile_no = serializers.CharField(read_only=True, allow_null=True)
    occupation_id = serializers.IntegerField(read_only=True, allow_null=True)
    occupation = serializers.CharField(read_only=True, allow_null=True)
    is_dependent = serializers.BooleanField(read_only=True)
    isDependent = serializers.BooleanField(read_only=True)
    is_emergency_contact = serializers.BooleanField(read_only=True)
    emergency_contact = serializers.BooleanField(read_only=True)


class EmployeeProfileSectionSerializer(serializers.Serializer):
    """Read model — field names match employee Profile Section UI."""

    employee_id = serializers.UUIDField(read_only=True)
    employee_code = serializers.CharField(read_only=True)
    salutation = serializers.CharField(read_only=True, allow_null=True)
    first_name = serializers.CharField(read_only=True)
    middle_name = serializers.CharField(read_only=True, allow_null=True)
    last_name = serializers.CharField(read_only=True)
    preferred_name = serializers.CharField(read_only=True, allow_null=True)
    personal_email = serializers.CharField(read_only=True, allow_null=True)
    official_email = serializers.CharField(read_only=True, allow_null=True)
    personal_mobile = serializers.CharField(read_only=True, allow_null=True)
    work_mobile = serializers.CharField(read_only=True, allow_null=True)
    alternate_mobile_number = serializers.CharField(read_only=True, allow_null=True)
    extension_number = serializers.CharField(read_only=True, allow_null=True)
    username = serializers.CharField(read_only=True, allow_null=True)
    bio_about = serializers.CharField(read_only=True, allow_null=True)
    profile_photo = serializers.CharField(read_only=True, allow_null=True)
    signature_upload = serializers.CharField(read_only=True, allow_null=True)

# ---------------------------------------------------------------------------
# Main GET serializer
# ---------------------------------------------------------------------------

class EmployeeProfileSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField(read_only=True)
    employee_code = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    middle_name = serializers.CharField(read_only=True, allow_null=True)
    last_name = serializers.CharField(read_only=True)
    salutation = serializers.CharField(read_only=True, allow_null=True)
    nickname = serializers.CharField(read_only=True, allow_null=True)
    # FIX 1: added gender field
    gender = serializers.CharField(read_only=True, allow_null=True)
    date_of_joining = serializers.CharField(read_only=True)
    date_of_birth = serializers.CharField(read_only=True)
    wish_on_date = serializers.CharField(read_only=True, allow_null=True)
    status = serializers.CharField(read_only=True)
    profile_picture_url = serializers.CharField(read_only=True, allow_null=True)
    signature_url = serializers.CharField(read_only=True, allow_null=True)
    biography = serializers.CharField(read_only=True, allow_null=True)
    tags = serializers.ListField(child=serializers.CharField(), read_only=True, allow_null=True)
    work_location = serializers.CharField(read_only=True, allow_null=True)
    profile_section = EmployeeProfileSectionSerializer(read_only=True)
    current_address = EmployeeProfileAddressSerializer(read_only=True, allow_null=True)
    permanent_address = EmployeeProfileAddressSerializer(read_only=True, allow_null=True)
    contacts = EmployeeProfileContactSerializer(read_only=True, allow_null=True)
    personal_details = EmployeeProfilePersonalDetailsSerializer(read_only=True, allow_null=True)
    medical_details = MedicalDetailsPayloadSerializer(read_only=True, allow_null=True)
    employment_details = EmployeeProfileEmploymentDetailsSerializer(read_only=True, allow_null=True)
    family_details = EmployeeProfileFamilyDetailsSerializer(many=True, read_only=True)


# ---------------------------------------------------------------------------
# Update serializers (PATCH / PUT)
# ---------------------------------------------------------------------------

class EmployeeProfileContactUpdateSerializer(serializers.Serializer):
    official_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    personal_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    mobile_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    personal_mobile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    alternate_mobile_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    alternate_mobile_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_mobile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    extension_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    emergency_contact_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    # FIX 5: changed from UUIDField to IntegerField — emergency_contact_relation uses integer PK
    emergency_contact_relation_id = serializers.IntegerField(required=False, allow_null=True)
    emergency_contact_phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    emergency_contact_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    skype_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    linkedin_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class EmployeeProfilePersonalDetailsUpdateSerializer(serializers.Serializer):
    nationality_id = serializers.IntegerField(required=False, allow_null=True)
    marital_status_id = serializers.IntegerField(required=False, allow_null=True)
    marriage_date = serializers.DateField(required=False, allow_null=True)
    spouse_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    place_of_birth = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    residential_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    father_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    religion_id = serializers.IntegerField(required=False, allow_null=True)
    caste_id = serializers.IntegerField(required=False, allow_null=True)
    caste_category_id = serializers.IntegerField(required=False, allow_null=True)
    mother_tongue_id = serializers.IntegerField(required=False, allow_null=True)
    native_place = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dietary_preference = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    house_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    blood_group_id = serializers.IntegerField(required=False, allow_null=True)
    is_physically_challenged = serializers.BooleanField(required=False, allow_null=True)
    disability_details = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    height_cm = serializers.DecimalField(required=False, max_digits=5, decimal_places=1, allow_null=True)
    weight_kg = serializers.DecimalField(required=False, max_digits=5, decimal_places=1, allow_null=True)
    identification_mark = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pre_existing_diseases = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    undergone_major_surgery = serializers.BooleanField(required=False, allow_null=True)
    is_international_employee = serializers.BooleanField(required=False, allow_null=True)
    is_ex_serviceman = serializers.BooleanField(required=False, allow_null=True)
    hobby = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    highest_qualification_id = serializers.IntegerField(required=False, allow_null=True)
    total_work_experience_months = serializers.IntegerField(required=False, allow_null=True)
    relevant_work_experience_months = serializers.IntegerField(required=False, allow_null=True)

    def validate_height_cm(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Height must be greater than 0.")
        return value

    def validate_weight_kg(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Weight must be greater than 0.")
        return value

    def validate(self, attrs):
        total = attrs.get("total_work_experience_months")
        relevant = attrs.get("relevant_work_experience_months")
        if total is not None and total < 0:
            raise serializers.ValidationError(
                {"total_work_experience_months": "Total experience cannot be negative."}
            )
        if relevant is not None and relevant < 0:
            raise serializers.ValidationError(
                {"relevant_work_experience_months": "Relevant experience cannot be negative."}
            )
        if total is not None and relevant is not None and relevant > total:
            raise serializers.ValidationError(
                {"relevant_work_experience_months": "Relevant experience cannot exceed total experience."}
            )
        return attrs


class EmployeeProfileEmploymentDetailsUpdateSerializer(serializers.Serializer):
    employee_type_id = serializers.IntegerField(required=False, allow_null=True)
    employee_work_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    wages_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    department_id = serializers.UUIDField(required=False, allow_null=True)
    designation_id = serializers.UUIDField(required=False, allow_null=True)
    grade_id = serializers.UUIDField(required=False, allow_null=True)
    shift_id = serializers.UUIDField(required=False, allow_null=True)
    work_location_id = serializers.IntegerField(required=False, allow_null=True)
    source_of_hire_id = serializers.IntegerField(required=False, allow_null=True)
    payroll_status_id = serializers.IntegerField(required=False, allow_null=True)
    transport_type_id = serializers.IntegerField(required=False, allow_null=True)
    payroll_frequency = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    payment_mode = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    notice_period_days = serializers.IntegerField(required=False, allow_null=True)
    cost_center = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profit_center = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    function = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    wing = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    zone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    cadre = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    batch = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    team = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    client = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    acquisition = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    biometric_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    holiday_list_id = serializers.UUIDField(required=False, allow_null=True)


class EmployeeProfileAddressUpdateSerializer(serializers.Serializer):
    address_line1 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address_line2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    landmark = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city_id = serializers.IntegerField(required=False, allow_null=True)
    state_id = serializers.IntegerField(required=False, allow_null=True)
    country_id = serializers.IntegerField(required=False, allow_null=True)
    pincode = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    to_date = serializers.DateField(required=False, allow_null=True)
    is_same_as_permanent = serializers.BooleanField(required=False, allow_null=True)


class EmployeeProfileFamilyDetailsUpdateSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    relation_id = serializers.IntegerField(required=False, allow_null=True)
    date_of_birth = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"],
    )
    gender_id = serializers.IntegerField(required=False, allow_null=True)
    blood_group_id = serializers.IntegerField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mobile_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    occupation_id = serializers.IntegerField(required=False, allow_null=True)
    is_dependent = serializers.BooleanField(required=False, allow_null=True)
    isDependent = serializers.BooleanField(required=False, allow_null=True)
    is_emergency_contact = serializers.BooleanField(required=False, allow_null=True)
    emergency_contact = serializers.BooleanField(required=False, allow_null=True)
    remove = serializers.BooleanField(required=False, default=False)
    delete = serializers.BooleanField(required=False, default=False)


class EmployeeProfileSectionUpdateSerializer(serializers.Serializer):
    """PATCH payload keys aligned with employee Profile Section UI."""

    salutation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    preferred_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    personal_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    official_email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    personal_mobile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_mobile = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    alternate_mobile_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    extension_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=150)
    bio_about = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_photo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    signature_upload = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class EmployeeProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    salutation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    nickname = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    preferred_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    biography = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bio_about = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_picture_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_photo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    signature_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    # FIX 1: accept `gender_id` (master SMALLINT PK) for updates
    gender_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_gender_id(self, value):
        if value is None:
            return value
        from apps.employees.models.masters.personal import Gender

        if not Gender.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid gender_id")
        return value
    date_of_joining = serializers.DateField(required=False, allow_null=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    wish_on_date = serializers.DateField(required=False, allow_null=True)
    status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_section = EmployeeProfileSectionUpdateSerializer(required=False)
    contacts = EmployeeProfileContactUpdateSerializer(required=False)
    personal_details = EmployeeProfilePersonalDetailsUpdateSerializer(required=False)
    medical_details = MedicalDetailsPayloadSerializer(required=False)
    employment_details = EmployeeProfileEmploymentDetailsUpdateSerializer(required=False)
    current_address = EmployeeProfileAddressUpdateSerializer(required=False)
    permanent_address = EmployeeProfileAddressUpdateSerializer(required=False)
    family_details = EmployeeProfileFamilyDetailsUpdateSerializer(many=True, required=False)

    def validate(self, attrs):
        if "preferred_name" in attrs:
            attrs["nickname"] = attrs.pop("preferred_name")
        if "bio_about" in attrs:
            attrs["biography"] = attrs.pop("bio_about")
        if "profile_photo" in attrs:
            attrs["profile_picture_url"] = attrs.pop("profile_photo")
        # Validate referenced master IDs to avoid invalid foreign keys.
        from rest_framework import serializers as _serializers

        nested_master_map = {
            None: {
                "gender_id": ("apps.employees.models.masters.personal", "Gender"),
            },
            "contacts": {
                "emergency_contact_relation_id": (
                    "apps.employees.models.masters.misc",
                    "Relation",
                ),
            },
            "personal_details": {
                "nationality_id": (
                    "apps.employees.models.masters.personal",
                    "Nationality",
                ),
                "marital_status_id": (
                    "apps.employees.models.masters.personal",
                    "MaritalStatus",
                ),
                "religion_id": ("apps.employees.models.masters.personal", "Religion"),
                "caste_id": ("apps.employees.models.masters.personal", "Caste"),
                "caste_category_id": (
                    "apps.employees.models.masters.personal",
                    "CasteCategory",
                ),
                "mother_tongue_id": (
                    "apps.employees.models.masters.personal",
                    "MotherTongue",
                ),
                "blood_group_id": (
                    "apps.employees.models.masters.personal",
                    "BloodGroup",
                ),
                "highest_qualification_id": (
                    "apps.employees.models.masters.education",
                    "EducationLevel",
                ),
            },
            "employment_details": {
                "employee_type_id": (
                    "apps.employees.models.masters.employment",
                    "EmployeeType",
                ),
                "category_id": (
                    "apps.employees.models.masters.employment",
                    "EmployeeCategory",
                ),
                "department_id": (
                    "apps.employees.models.masters.organization",
                    "Department",
                ),
                "designation_id": (
                    "apps.employees.models.masters.organization",
                    "Designation",
                ),
                "grade_id": ("apps.employees.models.masters.organization", "Grade"),
                "shift_id": (
                    "apps.employees.models.masters.hr_setup",
                    "Shift",
                ),
                "work_location_id": (
                    "apps.employees.models.masters.location",
                    "OfficeLocation",
                ),
                "source_of_hire_id": (
                    "apps.employees.models.masters.employment",
                    "SourceOfHire",
                ),
                "payroll_status_id": (
                    "apps.employees.models.masters.employment",
                    "PayrollStatus",
                ),
                "transport_type_id": (
                    "apps.employees.models.masters.employment",
                    "TransportType",
                ),
                "holiday_list_id": (
                    "apps.employees.models.masters.hr_setup",
                    "HolidayCalendar",
                ),
            },
            "current_address": {
                "city_id": ("apps.employees.models.masters.location", "City"),
                "state_id": ("apps.employees.models.masters.location", "State"),
                "country_id": ("apps.employees.models.masters.location", "Country"),
            },
            "permanent_address": {
                "city_id": ("apps.employees.models.masters.location", "City"),
                "state_id": ("apps.employees.models.masters.location", "State"),
                "country_id": ("apps.employees.models.masters.location", "Country"),
            },
        }

        errors = {}
        for section, master_map in nested_master_map.items():
            payload = attrs if section is None else attrs.get(section)
            if not payload:
                continue

            section_errors = {}
            for field, (module_path, class_name) in master_map.items():
                if field not in payload:
                    continue
                value = payload.get(field)
                if value is None:
                    continue
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    model = getattr(module, class_name)
                except Exception:
                    continue

                try:
                    exists = model.objects.filter(id=value, is_active=True).exists()
                except Exception:
                    exists = model.objects.filter(id=value).exists()

                if not exists:
                    section_errors[field] = f"Invalid {field}"

            if section is None:
                errors.update(section_errors)
            elif section_errors:
                errors[section] = section_errors

        if errors:
            raise _serializers.ValidationError(errors)

        return attrs
    # FIX 2: added profile_picture_url and biography to update serializer
    profile_picture_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    biography = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    contacts = EmployeeProfileContactUpdateSerializer(required=False)
    personal_details = EmployeeProfilePersonalDetailsUpdateSerializer(required=False)
    employment_details = EmployeeProfileEmploymentDetailsUpdateSerializer(required=False)
    current_address = EmployeeProfileAddressUpdateSerializer(required=False)
    permanent_address = EmployeeProfileAddressUpdateSerializer(required=False)
