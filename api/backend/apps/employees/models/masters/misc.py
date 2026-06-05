

import uuid

from django.db import models

from apps.employees.models.base import (
    MasterBaseModel,
    MetadataMixin,
    UUIDMasterBaseModel,
)


# ---------------------------------------------------------------------------
# mst_language
# ---------------------------------------------------------------------------


class Language(MasterBaseModel):
   

    iso_639_2_code = models.CharField(max_length=3, unique=True)

    class Meta:
        db_table = "mst_language"
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_language_code"),
            models.Index(fields=["iso_639_2_code"], name="idx_mst_language_iso639"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_language_code"),
            models.UniqueConstraint(
                fields=["iso_639_2_code"], name="uq_mst_language_iso639"
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_language_proficiency
# ---------------------------------------------------------------------------


class LanguageProficiency(MasterBaseModel):
  
    level_order = models.SmallIntegerField()

    class Meta:
        db_table = "mst_language_proficiency"
        verbose_name = "Language Proficiency"
        verbose_name_plural = "Language Proficiencies"
        ordering = ["level_order"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_lang_proficiency_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_lang_proficiency_code"
            ),
            models.CheckConstraint(
                check=models.Q(level_order__gte=1) & models.Q(level_order__lte=10),
                name="chk_mst_lang_proficiency_level_order",
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_proficiency_level
# ---------------------------------------------------------------------------


class ProficiencyLevel(MasterBaseModel):
   

    class Meta:
        db_table = "mst_proficiency_level"
        verbose_name = "Proficiency Level"
        verbose_name_plural = "Proficiency Levels"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_proficiency_level_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_proficiency_level_code"
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_nominee_purpose
# ---------------------------------------------------------------------------


class NomineePurpose(MasterBaseModel):
    

    class Meta:
        db_table = "mst_nominee_purpose"
        verbose_name = "Nominee Purpose"
        verbose_name_plural = "Nominee Purposes"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_nominee_purpose_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_nominee_purpose_code"
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_relation  — CONSTANT
# ---------------------------------------------------------------------------


class Relation(MasterBaseModel):
 

    is_dependent = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_relation"
        verbose_name = "Relation"
        verbose_name_plural = "Relations"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_relation_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_relation_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_occupation
# ---------------------------------------------------------------------------


class Occupation(MasterBaseModel):
   
    class Meta:
        db_table = "mst_occupation"
        verbose_name = "Occupation"
        verbose_name_plural = "Occupations"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_occupation_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_occupation_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_profession
# ---------------------------------------------------------------------------


class Profession(MasterBaseModel):
    

    class Meta:
        db_table = "mst_profession"
        verbose_name = "Profession"
        verbose_name_plural = "Professions"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_profession_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_profession_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_communication_channel
# ---------------------------------------------------------------------------


class CommunicationChannel(MasterBaseModel):
  
    class Meta:
        db_table = "mst_communication_channel"
        verbose_name = "Communication Channel"
        verbose_name_plural = "Communication Channels"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_comm_channel_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_comm_channel_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_communication_task
# ---------------------------------------------------------------------------


class CommunicationTask(MetadataMixin):
    

    id = models.SmallAutoField(primary_key=True)
    code = models.CharField(max_length=40, unique=True)
    label = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_communication_task"
        verbose_name = "Communication Task"
        verbose_name_plural = "Communication Tasks"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_comm_task_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_comm_task_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_document_type
# ---------------------------------------------------------------------------


class DocumentType(MasterBaseModel):
  

    description = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=80, default="General")
    is_expiry_required = models.BooleanField(default=False)
    is_number_required = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=100)
    allowed_file_types = models.JSONField(default=list, blank=True)

    class SidesRequired(models.TextChoices):
        FULL = "FULL", "Full"
        FRONT = "FRONT", "Front"
        BACK = "BACK", "Back"
        BOTH = "BOTH", "Both"

    class UploadType(models.TextChoices):
        SINGLE = "SINGLE", "Single Side"
        FRONT_BACK = "FRONT_BACK", "Front & Back Side"
        MULTIPLE = "MULTIPLE", "Multiple Files"

    upload_type = models.CharField(
        max_length=20,
        default=UploadType.SINGLE,
    )
    sides_required = models.CharField(
        max_length=10,
        choices=SidesRequired.choices,
        blank=True,
        null=True,
    )
    max_attachments = models.SmallIntegerField(default=2)
    # Post-audit additive columns (replaces separate mst_identity_document_type)
    is_identity_verifiable = models.BooleanField(default=False)
    identity_code = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = "mst_document_type"
        verbose_name = "Document Type"
        verbose_name_plural = "Document Types"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_document_type_code"),
            models.Index(fields=["display_order", "label"], name="idx_doc_type_order"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_document_type_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_document_side
# ---------------------------------------------------------------------------


class DocumentSide(MasterBaseModel):
    

    description = models.CharField(max_length=255, blank=True, null=True)
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_document_side"
        verbose_name = "Document Side"
        verbose_name_plural = "Document Sides"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_document_side_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_document_side_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_system_role  (UUID PK)
# ---------------------------------------------------------------------------


# class SystemRole(UUIDMasterBaseModel):
#     """
#     System-level RBAC roles: ADMIN / HR_MANAGER / EMPLOYEE / RECRUITER etc.
#     Used in employee_role_assignments.
#     """

#     code = models.CharField(max_length=30, unique=True)
#     label = models.CharField(max_length=200)
#     description = models.TextField(blank=True, null=True)
#     access_level = models.CharField(max_length=30, default="SELF_SERVICE")
#     is_custom = models.BooleanField(default=False)

#     class Meta:
#         db_table = "mst_system_role"
#         verbose_name = "System Role"
#         verbose_name_plural = "System Roles"
#         indexes = [
#             models.Index(fields=["code"], name="idx_mst_system_role_code"),
#         ]
#         constraints = [
#             models.UniqueConstraint(fields=["code"], name="uq_mst_system_role_code"),
#         ]

#     def __str__(self) -> str:
#         return self.label


# # ---------------------------------------------------------------------------
# # mst_default_role
# # ---------------------------------------------------------------------------


# class DefaultRole(MetadataMixin):
#     """
#     Maps a system role as the default role for new employees.
#     """

#     id = models.SmallAutoField(primary_key=True)
#     role = models.ForeignKey(
#         SystemRole,
#         on_delete=models.PROTECT,
#         db_column="role_id",
#         related_name="default_role_entries",
#     )
#     is_default = models.BooleanField(default=True)
#     is_active = models.BooleanField(default=True)

#     class Meta:
#         db_table = "mst_default_role"
#         verbose_name = "Default Role"
#         verbose_name_plural = "Default Roles"
#         indexes = [
#             models.Index(fields=["role"], name="idx_mst_default_role_role"),
#         ]

#     def __str__(self) -> str:
#         return f"Default: {self.role}"
