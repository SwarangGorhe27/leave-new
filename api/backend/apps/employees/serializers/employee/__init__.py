"""Employee serializers — read models and change-request / upload serializers."""

from apps.employees.serializers.employee.assets import (
    AssetReadSerializer,
)
from apps.employees.serializers.employee.bank_statutory_details import (
    BankAccountDetailsRowSerializer,
    BankStatutoryDetailsSerializer,
    BankStatutoryDetailsSubmitSerializer,
    StatutoryDetailsSerializer,
)
from apps.employees.serializers.employee.access_card_details import (
    AccessCardDetailsSerializer,
    AccessCardDetailsRowSerializer,
)
from apps.employees.serializers.employee.address_details import (
    AddressDetailsSubmitSerializer,
)
from apps.employees.serializers.employee.extended import (
    AdminApproveSerializer,
    AdminChangeRequestDetailSerializer,
    AdminRejectSerializer,
    ChangeRequestReadSerializer,
    ChangeRequestSubmitSerializer,
    DocumentUploadSerializer,
    MedicalEmergencyReadSerializer,
    PassportDocumentUploadSerializer,
    PassportVisaReadSerializer,
    ProfilePictureUploadSerializer,
    SignatureUploadSerializer,
    SkillCertificationReadSerializer,
    SocialProfileReadSerializer,
    WorkExperienceReadSerializer,
)
from apps.employees.serializers.employee.employment_details import (
    EmploymentDetailsSubmitSerializer,
)
from apps.employees.serializers.employee.insurance_details import (
    InsuranceDetailsSubmitSerializer,
)
from apps.employees.serializers.employee.medical_details import (
    MedicalDetailsSubmitSerializer,
)
from apps.employees.serializers.employee.nominee_details import (
    NomineeDetailsSubmitSerializer,
)
from apps.employees.serializers.employee.personal_details import (
    PersonalDetailsSubmitSerializer,
)
from apps.employees.serializers.employee.profile_section import (
    ProfileSectionAdminUpdateSerializer,
    ProfileSectionEmployeeSubmitSerializer,
    ProfileSectionSerializer,
)
from apps.employees.serializers.employee.social_profile import (
    SocialProfileSubmitSerializer,
)
from apps.employees.serializers.employee.salary_details import (
    EmployeeSalaryDetailsSerializer,
)
from apps.employees.serializers.employee.my_request import (
    MyRequestDetailSerializer,
    MyRequestListItemSerializer,
    MyRequestSubmitSerializer,
    MyRequestUpdateSerializer,
)
from apps.employees.serializers.employee.read_serializers import (
    AddressReadSerializer,
    BankAccountReadSerializer,
    DocumentReadSerializer,
    EducationReadSerializer,
    EmploymentDetailsReadSerializer,
    FamilyMemberReadSerializer,
    InsuranceReadSerializer,
    LanguageReadSerializer,
    MyFullProfileSerializer,
    NomineeReadSerializer,
    PersonalDetailsReadSerializer,
)

__all__ = [
    "AddressReadSerializer",
    "AddressDetailsSubmitSerializer",
    "AccessCardDetailsRowSerializer",
    "AccessCardDetailsSerializer",
    "AdminApproveSerializer",
    "AdminChangeRequestDetailSerializer",
    "AdminRejectSerializer",
    "AssetReadSerializer",
    "BankAccountReadSerializer",
    "BankAccountDetailsRowSerializer",
    "BankStatutoryDetailsSerializer",
    "BankStatutoryDetailsSubmitSerializer",
    "ChangeRequestReadSerializer",
    "ChangeRequestSubmitSerializer",
    "DocumentReadSerializer",
    "DocumentUploadSerializer",
    "EducationReadSerializer",
    "EmploymentDetailsReadSerializer",
    "EmploymentDetailsSubmitSerializer",
    "EmployeeSalaryDetailsSerializer",
    "FamilyMemberReadSerializer",
    "InsuranceReadSerializer",
    "InsuranceDetailsSubmitSerializer",
    "LanguageReadSerializer",
    "MedicalEmergencyReadSerializer",
    "MedicalDetailsSubmitSerializer",
    "MyFullProfileSerializer",
    "MyRequestDetailSerializer",
    "MyRequestListItemSerializer",
    "MyRequestSubmitSerializer",
    "MyRequestUpdateSerializer",
    "NomineeReadSerializer",
    "NomineeDetailsSubmitSerializer",
    "PassportDocumentUploadSerializer",
    "PassportVisaReadSerializer",
    "PersonalDetailsReadSerializer",
    "PersonalDetailsSubmitSerializer",
    "ProfileSectionAdminUpdateSerializer",
    "ProfileSectionEmployeeSubmitSerializer",
    "ProfileSectionSerializer",
    "ProfilePictureUploadSerializer",
    "SignatureUploadSerializer",
    "SkillCertificationReadSerializer",
    "SocialProfileReadSerializer",
    "SocialProfileSubmitSerializer",
    "StatutoryDetailsSerializer",
    "WorkExperienceReadSerializer",
]
