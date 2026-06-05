"""
Employee self-service views — public API surface.

Implementation lives in dedicated modules; this package only re-exports.
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.employees.permissions import IsActiveEmployee

from .family_choices_views import (
    FamilyOccupationsChoiceView,
    FamilyRelationsChoiceView,
)
from .education_choices_views import (
    EducationInstitutionsChoiceView,
    EducationPassingYearsChoiceView,
    EducationQualificationsChoiceView,
    EducationSpecializationsChoiceView,
    EducationUniversitiesChoiceView,
)
from .address_details_views import MyAddressDetailsView
from .access_card_details_views import MyAccessCardDetailsView
from .bank_statutory_details_views import MyBankStatutoryDetailsView
from .education_details_views import MyEducationDetailsView
from .employment_details_views import MyEmploymentDetailsView
from .family_details_views import MyFamilyDetailsView
from .insurance_details_views import MyInsuranceDetailsView
from .language_details_views import MyLanguageDetailsView
from .passport_visa_choices_views import (
    CountriesChoiceView,
    PassportCategoryChoiceView,
    PassportStatusChoiceView,
    VisaStatusChoiceView,
    VisaTypeChoiceView,
)
from .passport_visa_details_views import MyPassportVisaDetailsView
from .nominee_details_views import (
    MyNomineeDetailsView,
    NomineePurposesChoiceView,
    NomineeRelationsChoiceView,
)
from .personal_details_views import MyPersonalDetailsView
from .medical_details_views import MyMedicalDetailsView
from .profile_views import MyProfileView
from .social_profile_views import MySocialProfileView
from .salary_details_views import MySalaryDetailsView
from .my_request_views import MyRequestDetailView, MyRequestListCreateView
from .section_views import (
    MyAddressView,
    MyAssetsView,
    MyBankView,
    MyDocumentsView,
    MyEducationView,
    MyExperienceView,
    MyFamilyView,
    MyLanguageView,
    MyNomineeView,
    MyPassportView,
    MyPersonalView,
)
from .upload_views import (
    CertificateUploadView,
    DocumentUploadView,
    PassportDocumentUploadView,
    ProfilePictureUploadView,
    ProfilePictureView,
    SignatureUploadView,
)

__all__ = [
    "CertificateUploadView",
    "CountriesChoiceView",
    "DocumentUploadView",
    "FamilyOccupationsChoiceView",
    "FamilyRelationsChoiceView",
    "MyAddressView",
    "MyAddressDetailsView",
    "MyAccessCardDetailsView",
    "MyAssetsView",
    "MyBankView",
    "MyBankStatutoryDetailsView",
    "MyDocumentsView",
    "MyEducationDetailsView",
    "MyEducationView",
    "EducationInstitutionsChoiceView",
    "EducationPassingYearsChoiceView",
    "EducationQualificationsChoiceView",
    "EducationSpecializationsChoiceView",
    "EducationUniversitiesChoiceView",
    "MyEmploymentDetailsView",
    "MyEmploymentView",
    "MyExperienceView",
    "MyFamilyDetailsView",
    "MyFamilyView",
    "MyInsuranceDetailsView",
    "MyLanguageView",
    "MyLanguageDetailsView",
    "MyMedicalDetailsView",
    "MyNomineeView",
    "MyNomineeDetailsView",
    "NomineePurposesChoiceView",
    "NomineeRelationsChoiceView",
    "MyPassportView",
    "MyPassportVisaDetailsView",
    "PassportCategoryChoiceView",
    "PassportStatusChoiceView",
    "VisaStatusChoiceView",
    "VisaTypeChoiceView",
    "MyPersonalDetailsView",
    "MyPersonalView",
    "MyProfileView",
    "MySocialProfileView",
    "MySalaryDetailsView",
    "MyRequestDetailView",
    "MyRequestListCreateView",
    "PassportDocumentUploadView",
    "ProfilePictureUploadView",
    "ProfilePictureView",
    "SignatureUploadView",
]

# Backward-compatible aliases for legacy imports
MyEmploymentView = MyEmploymentDetailsView

_EMPLOYEE_PERMISSION_CLASSES = [IsAuthenticated, IsActiveEmployee]

for _view_name in __all__:
    _view = globals().get(_view_name)
    if isinstance(_view, type) and issubclass(_view, APIView):
        _view.permission_classes = _EMPLOYEE_PERMISSION_CLASSES

del _view_name, _view
