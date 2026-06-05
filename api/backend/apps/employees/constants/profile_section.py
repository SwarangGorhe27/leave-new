"""
Profile Section UI — field sets (matches employee module screenshot).

Read-only on form: employee_id, employee_code
Employee Submit → change request (PROFILE) → Admin approve → DB update
Admin: GET / PATCH profile_section directly
"""

# All keys returned by GET (screenshot labels)
PROFILE_SECTION_FIELDS = (
    "employee_id",
    "employee_code",
    "salutation",
    "middle_name",
    "preferred_name",
    "personal_email",
    "personal_mobile",
    "extension_number",
    "bio_about",
    "profile_photo",
    "first_name",
    "last_name",
    "official_email",
    "work_mobile",
    "alternate_mobile_number",
    "username",
    "signature_upload",
)

# Employee may request changes to these via Submit (change request)
PROFILE_SECTION_EMPLOYEE_EDITABLE = frozenset({
    "salutation",
    "middle_name",
    "preferred_name",
    "personal_email",
    "personal_mobile",
    "extension_number",
    "bio_about",
    "profile_photo",
    "first_name",
    "last_name",
    "work_mobile",
    "alternate_mobile_number",
    "username",
    "signature_upload",
})

# Admin PATCH may also set official_email
PROFILE_SECTION_ADMIN_EDITABLE = PROFILE_SECTION_EMPLOYEE_EDITABLE | frozenset({
    "official_email",
})
