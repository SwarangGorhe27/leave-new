"""
Employee Self-Service (ESS) API URL Configuration

Base URL: /api/employee/

All endpoints require:
  - Authentication: Bearer token in Authorization header
  - Active employee profile: IsActiveEmployee permission
  - Data Ownership: Users can only access their own employee data
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import LoginView

from apps.employees.views.employee import (
    CertificateUploadView,
    CountriesChoiceView,
    DocumentUploadView,
    FamilyOccupationsChoiceView,
    FamilyRelationsChoiceView,
    MyAddressDetailsView,
    MyAccessCardDetailsView,
    MyAssetsView,
    MyBankView,
    MyBankStatutoryDetailsView,
    MyDocumentsView,
    EducationInstitutionsChoiceView,
    EducationPassingYearsChoiceView,
    EducationQualificationsChoiceView,
    EducationSpecializationsChoiceView,
    EducationUniversitiesChoiceView,
    MyEducationDetailsView,
    MyEducationView,
    MyEmploymentDetailsView,
    MyExperienceView,
    MyFamilyDetailsView,
    MyFamilyView,
    MyInsuranceDetailsView,
    MyLanguageView,
    MyLanguageDetailsView,
    MyMedicalDetailsView,
    MyNomineeDetailsView,
    NomineePurposesChoiceView,
    NomineeRelationsChoiceView,
    MyPassportView,
    MyPassportVisaDetailsView,
    PassportCategoryChoiceView,
    PassportStatusChoiceView,
    MySalaryDetailsView,
    VisaStatusChoiceView,
    VisaTypeChoiceView,
    MyPersonalDetailsView,
    MyProfileView,
    MyRequestDetailView,
    MyRequestListCreateView,
    MySocialProfileView,
    PassportDocumentUploadView,
    ProfilePictureUploadView,
    SignatureUploadView,
)

app_name = "ess_employee"

urlpatterns = [
    # AUTH
    path("login/", LoginView.as_view(), name="employee-login"),
    path("refresh/", TokenRefreshView.as_view(), name="employee-token-refresh"),

    # ═══════════════════════════════════════════════════════════════════════
    # PROFILE & AGGREGATED DATA
    # ═══════════════════════════════════════════════════════════════════════
    path("my-profile/", MyProfileView.as_view(), name="my-profile"),
    # GET  — Returns complete profile with all related data

    path("my-requests/", MyRequestListCreateView.as_view(), name="my-requests"),
    path("my-requests/<uuid:pk>/", MyRequestDetailView.as_view(), name="my-request-detail"),
    
    # ═══════════════════════════════════════════════════════════════════════
    # PERSONAL INFORMATION SECTIONS
    # ═══════════════════════════════════════════════════════════════════════
    path("my-personal-details/", MyPersonalDetailsView.as_view(), name="my-personal-details"),
    # GET   — Personal Details form (screenshot fields, real DB data)
    # PATCH — Edit → change request → admin approve/reject
    # POST  — Same as PATCH (Submit)
    
    path("my-employment/", MyEmploymentDetailsView.as_view(), name="my-employment"),
    # GET/PATCH/POST — Employment Details form; edits submit for admin approval
    
    path("my-address-details/", MyAddressDetailsView.as_view(), name="my-address-details"),
    # GET  — All addresses (permanent, current, etc.)
    
    path("my-family-details/", MyFamilyDetailsView.as_view(), name="my-family-details"),
    # GET   — Family Details form (screenshot fields, real DB data)
    # PATCH — Edit rows → change request → admin approve/reject
    # POST  — Same as PATCH (Submit)

    path("my-family/", MyFamilyView.as_view(), name="my-family"),
    # GET  — Legacy raw family_members list (prefer my-family-details/)
    
    # ═══════════════════════════════════════════════════════════════════════
    # FAMILY MEMBER CHOICES/LOOKUPS
    # ═══════════════════════════════════════════════════════════════════════
    path("family/choices/relations/", FamilyRelationsChoiceView.as_view(), name="family-relations"),
    path("family/choices/occupations/", FamilyOccupationsChoiceView.as_view(), name="family-occupations"),
    # GET — Master dropdowns: { "count", "results": [{ "id", "label" }, ...] }
    
    # ═══════════════════════════════════════════════════════════════════════
    # PASSPORT & VISA CHOICES/LOOKUPS
    # ═══════════════════════════════════════════════════════════════════════
    path("passport-visa/choices/categories/", PassportCategoryChoiceView.as_view(), name="passport-categories"),
    path("passport-visa/choices/passport-statuses/", PassportStatusChoiceView.as_view(), name="passport-statuses"),
    path("passport-visa/choices/visa-types/", VisaTypeChoiceView.as_view(), name="visa-types"),
    path("passport-visa/choices/visa-statuses/", VisaStatusChoiceView.as_view(), name="visa-statuses"),
    path("passport-visa/choices/countries/", CountriesChoiceView.as_view(), name="countries"),
    # GET — Master dropdowns: { "count", "results": [{ "id", "label" }, ...] }
    
    # ═══════════════════════════════════════════════════════════════════════
    # EDUCATION & SKILLS
    # ═══════════════════════════════════════════════════════════════════════
    path("my-education-details/", MyEducationDetailsView.as_view(), name="my-education-details"),
    # GET   — Education Details form (screenshot fields)
    # PATCH — Edit rows → change request → admin approve/reject
    # POST  — Same as PATCH (Submit)

    path("education/choices/qualifications/", EducationQualificationsChoiceView.as_view(), name="education-qualifications"),
    path("education/choices/specializations/", EducationSpecializationsChoiceView.as_view(), name="education-specializations"),
    path("education/choices/institutions/", EducationInstitutionsChoiceView.as_view(), name="education-institutions"),
    path("education/choices/universities/", EducationUniversitiesChoiceView.as_view(), name="education-universities"),
    path("education/choices/passing-years/", EducationPassingYearsChoiceView.as_view(), name="education-passing-years"),

    path("my-education/", MyEducationView.as_view(), name="my-education"),
    # GET  — Legacy raw education records (prefer my-education-details/)
    
    path("my-language/", MyLanguageView.as_view(), name="my-language"),
    # GET  — All language proficiencies
    
    path("my-language-details/", MyLanguageDetailsView.as_view(), name="my-language-details"),
    # GET   — Language Details form (screenshot fields, real DB data)
    # PATCH — Edit → change request → admin approve/reject
    # POST  — Same as PATCH (Submit)
    
    path("my-experience/", MyExperienceView.as_view(), name="my-experience"),
    # GET  — All work experience records
    
    # ═══════════════════════════════════════════════════════════════════════
    # FINANCIAL & RELATED INFORMATION
    # ═══════════════════════════════════════════════════════════════════════
    path("my-bank/", MyBankView.as_view(), name="my-bank"),
    # GET  — All bank account details

    path(
        "my-bank-statutory-details/",
        MyBankStatutoryDetailsView.as_view(),
        name="my-bank-statutory-details",
    ),
    # GET/PATCH/POST - Bank / PF / ESI screen; edits submit for admin approval
    
    path("my-nominee/", MyNomineeDetailsView.as_view(), name="my-nominee"),
    # GET/PATCH/POST - Nominee Details form; edits submit for admin approval
    path("nominee/choices/relations/", NomineeRelationsChoiceView.as_view(), name="nominee-relations"),
    path("nominee/choices/purposes/", NomineePurposesChoiceView.as_view(), name="nominee-purposes"),
    # GET - Nominee master dropdowns
    
    path("my-insurance-details/", MyInsuranceDetailsView.as_view(), name="my-insurance-details"),
    path("my-salary/", MySalaryDetailsView.as_view(), name="my-salary"),
    # GET/PATCH/POST — Insurance Details form; edits submit for admin approval
    
    # ═══════════════════════════════════════════════════════════════════════
    # DOCUMENTS & TRAVEL
    # ═══════════════════════════════════════════════════════════════════════
    path("my-documents/", MyDocumentsView.as_view(), name="my-documents"),
    # GET  — All uploaded documents
    
    path("my-passport-details/", MyPassportVisaDetailsView.as_view(), name="my-passport-details"),
    # GET   — Passport & Visa Details form (screenshot fields, real DB data)
    # PATCH — Edit rows → change request → admin approve/reject
    # POST  — Same as PATCH (Submit)
    
    path("my-passport/", MyPassportView.as_view(), name="my-passport"),
    # GET  — All passport and visa records
    
    path("my-assets/", MyAssetsView.as_view(), name="my-assets"),
    # GET  — Company-issued assets (access cards, etc.)

    path(
        "my-access-card-details/",
        MyAccessCardDetailsView.as_view(),
        name="my-access-card-details",
    ),
    # GET  — Access Card Details screen fields; employee read-only
    
    # ═══════════════════════════════════════════════════════════════════════
    # HEALTH & SOCIAL
    # ═══════════════════════════════════════════════════════════════════════
    path("my-medical-details/", MyMedicalDetailsView.as_view(), name="my-medical-details"),
    # GET/PATCH/POST — Emergency & Medical Information form; edits submit for admin approval
    
    path("my-social-profile/", MySocialProfileView.as_view(), name="my-social-profile"),
    # GET/PATCH/POST — Social & Professional Profiles form; edits submit for admin approval
    
    # ═══════════════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════════════
    
    
    
    
    # ═══════════════════════════════════════════════════════════════════════
    # FILE UPLOADS
    # ═══════════════════════════════════════════════════════════════════════
    path("profile-picture/", ProfilePictureUploadView.as_view(), name="profile-picture"),
    # PUT/PATCH — Upload profile picture (multipart/form-data)
    #   Form field: profile_picture (image file)

    path("upload/signature/", SignatureUploadView.as_view(), name="upload-signature"),
    # PUT/PATCH — Upload signature (multipart/form-data)
    #   Form field: signature_upload (image or PDF, max 2 MB)
    
    path("upload/document/", DocumentUploadView.as_view(), name="upload-document"),
    # POST — Upload general document (multipart/form-data)
    #   Form fields: document (file), document_name (optional), remarks (optional)
    
    path("upload/passport/", PassportDocumentUploadView.as_view(), name="upload-passport"),
    # POST — Upload passport/visa document (multipart/form-data)
    #   Form fields: document (file), document_kind (optional), record_id (optional)
    
    path("upload/certificate/", CertificateUploadView.as_view(), name="upload-certificate"),
    # POST — Upload skill/training certificate (multipart/form-data)
    #   Form fields: document (file), record_id (optional)
]
