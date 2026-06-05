"""
Base model classes for the Employee module.

Hierarchy:
  MetadataMixin          — 11-field universal metadata block (abstract)
  MasterBaseModel        — SMALLINT PK + code + label (abstract, for mst_* tables)
  UUIDMasterBaseModel    — UUID PK master variant (abstract)
  BaseModel              — UUID PK transaction base (abstract)
  PIIBaseModel           — UUID PK + PII classification fields (abstract)
  TransactionBaseModel   — alias for BaseModel (UUID PK, non-PII transactions)
  TransactionPIIBaseModel— alias for PIIBaseModel (UUID PK + PII)
  FullAuditMasterModel   — UUID PK master with created_by / updated_by (abstract)
  CompanyMasterModel     — UUID PK company-scoped master (abstract)
  SoftDeleteMixin        — is_deleted + deleted_by (mixin)
  AuditMixin             — created_by + updated_by UUIDs (mixin)

PostgreSQL schema: employee
All concrete models must declare:
    class Meta:
        db_table = "<table_name>"

═══════════════════════════════════════════════════════════════════════════════
FIELD ORDERING STRATEGY — Field.creation_counter manipulation
═══════════════════════════════════════════════════════════════════════════════

Django determines column order via Field.creation_counter (a global integer
incremented each time a Field object is instantiated).  Abstract base-class
fields are instantiated at import time — long before concrete-model files are
loaded — so they always receive *lower* counters and sort *first* in the table.

To push metadata fields to the END of every table we jump the global counter
to a very high value BEFORE instantiating those fields, then restore it to the
normal range for structural (PK / identity) fields.

Counter tiers used:
  NORMAL         (~10 – ~50 000)  : id, code, label, company_id (structural)
  TIER_FLAG      700 001          : is_active
  TIER_PII       900 001–900 003  : data_classification, encryption_version, pii_flag
  TIER_AUDIT_FK 1 000 001–002     : created_by, updated_by  (FullAuditMasterModel only)
  TIER_META     1 000 011+        : created_at, updated_at, deleted_at, meta_data, …

Result for every concrete model:
  id / code / label   → FIRST   (from abstract base, normal counter)
  [business fields]   → MIDDLE  (from concrete model, loaded later → higher counter)
  is_active           → NEAR-LAST (700 001 unless overridden with a higher counter)
  PII classification  → NEAR-LAST (900 001+)
  Audit FKs           → NEAR-LAST (1 000 001+)
  Metadata            → ALWAYS LAST (1 000 011+)
═══════════════════════════════════════════════════════════════════════════════
"""

import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.fields import Field as _DjangoField


# ---------------------------------------------------------------------------
# Counter helpers
# ---------------------------------------------------------------------------

_NORMAL_COUNTER = _DjangoField.creation_counter  # save BEFORE any jump


def _jump(n: int) -> None:
    """Set global Field.creation_counter to n (next field gets n + 1)."""
    _DjangoField.creation_counter = n


def _restore() -> None:
    """Restore counter to the pre-jump checkpoint saved at module load."""
    _DjangoField.creation_counter = _NORMAL_COUNTER


# ═══════════════════════════════════════════════════════════════════════════
# Internal high-counter mixins
# (leading underscore = internal; use the public aliases below)
# ═══════════════════════════════════════════════════════════════════════════

# ── Tier FLAG — is_active (counter 700 001) ─────────────────────────────────
_jump(700_000)


class _IsActiveMixin(models.Model):
    """
    Provides is_active with creation_counter 700 001.
    Sorts AFTER all concrete-model business fields (which get counters < 50 000).
    """

    is_active = models.BooleanField(default=True)  # 700 001

    class Meta:
        abstract = True


# ── Tier PII — classification fields (counter 900 001–900 003) ──────────────
_jump(900_000)


class _PIIFieldsMixin(models.Model):
    """
    PII classification fields.
    Counters 900 001–900 003 → sort after business fields, before metadata.
    """

    data_classification = models.CharField(  # 900 001
        max_length=30,
        default="CONFIDENTIAL",
        blank=True,
        null=True,
        help_text="PII classification: PUBLIC / INTERNAL / CONFIDENTIAL / RESTRICTED",
    )
    encryption_version = models.SmallIntegerField(  # 900 002
        default=1,
        null=True,
        blank=True,
        help_text="Schema version of the encryption algorithm applied to PII fields",
    )
    pii_flag = models.BooleanField(  # 900 003
        default=True,
        help_text="Indicates this record contains personally identifiable information",
    )

    class Meta:
        abstract = True


# ── Tier AUDIT_FK — created_by / updated_by (counter 1 000 001–002) ─────────
_jump(1_000_000)


class _AuditUserFields(models.Model):
    """
    Audit-user FK references.
    Counters 1 000 001–002 → sort after all business fields and PII, before
    temporal metadata.
    """

    created_by = models.UUIDField(null=True, blank=True)  # 1 000 001
    updated_by = models.UUIDField(null=True, blank=True)  # 1 000 002

    class Meta:
        abstract = True


# ── Tier META — temporal + JSON metadata (counter 1 000 011+) ────────────────
_jump(1_000_010)


class _MetadataFields(models.Model):
    """
    11-field universal metadata block.
    Counters 1 000 011–021 → ALWAYS sort LAST in every table.
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=False)  # 1 000 011
    updated_at = models.DateTimeField(auto_now=True)  # 1 000 012
    deleted_at = models.DateTimeField(null=True, blank=True)  # 1 000 013
    meta_data = models.JSONField(default=dict, blank=True, null=True)  # 1 000 014
    meta_version = models.IntegerField(default=1)  # 1 000 015
    created_by_system = models.CharField(  # 1 000 016
        max_length=50, default="SYSTEM", blank=True, null=True
    )
    updated_by_system = models.CharField(  # 1 000 017
        max_length=50, default="SYSTEM", blank=True, null=True
    )
    created_source = models.CharField(max_length=50, blank=True, null=True)  # 1 000 018
    updated_source = models.CharField(max_length=50, blank=True, null=True)  # 1 000 019
    meta_tags = ArrayField(models.TextField(), blank=True, null=True)  # 1 000 020
    extra_attributes = models.JSONField(
        default=dict, blank=True, null=True
    )  # 1 000 021

    class Meta:
        abstract = True


# ── Restore counter for structural abstract bases ────────────────────────────
_restore()


# ═══════════════════════════════════════════════════════════════════════════
# Public API — abstract base models
# ═══════════════════════════════════════════════════════════════════════════

# ---------------------------------------------------------------------------
# MetadataMixin  (public alias — backward-compatible)
# ---------------------------------------------------------------------------


class MetadataMixin(_MetadataFields):
    """
    Public alias for _MetadataFields.

    Inherit this to attach the standard 11-field metadata block at TIER_META
    (counter ≥ 1 000 011), guaranteeing metadata appears LAST in every table.

    Fields:
      created_at, updated_at, deleted_at, meta_data, meta_version,
      created_by_system, updated_by_system, created_source, updated_source,
      meta_tags, extra_attributes
    """

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Master base models
# ---------------------------------------------------------------------------


class MasterBaseModel(_MetadataFields, _IsActiveMixin):
    """
    Abstract base for SMALLINT auto-increment PK master tables (mst_*).

    Column order achieved:
      id, code, label        → NORMAL counter  (structural identity)
      [subclass own fields]  → NORMAL counter  (loaded later → higher than base)
      is_active              → TIER_FLAG 700 001
      created_at … extra_attributes → TIER_META 1 000 011+
    """

    id = models.SmallAutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    label = models.CharField(max_length=100)

    class Meta:
        abstract = True


class UUIDMasterBaseModel(_MetadataFields, _IsActiveMixin):
    """
    Abstract base for UUID PK master tables (mst_company, mst_department, etc.).

    Column order achieved:
      id                     → NORMAL counter
      [subclass own fields]  → NORMAL counter (higher than base)
      is_active              → TIER_FLAG 700 001
      created_at …           → TIER_META 1 000 011+
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Transaction base models
# ---------------------------------------------------------------------------


class BaseModel(_MetadataFields, _IsActiveMixin):
    """
    Abstract base for UUID PK transaction tables (non-PII).

    Column order achieved:
      id                     → NORMAL counter
      [subclass own fields]  → NORMAL counter (higher than base)
      is_active              → TIER_FLAG 700 001
      created_at …           → TIER_META 1 000 011+
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class PIIBaseModel(BaseModel, _PIIFieldsMixin):
    """
    Abstract base for UUID PK tables containing PII.

    Column order achieved:
      id                               → NORMAL counter
      [subclass own fields]            → NORMAL counter (higher than base)
      is_active                        → TIER_FLAG 700 001
      data_classification …pii_flag   → TIER_PII  900 001+
      created_at …                     → TIER_META 1 000 011+

    Note: If a subclass explicitly re-declares data_classification / pii_flag
    (e.g. Employee), those override fields receive the concrete-model's counter
    (which is > base counter but < TIER_PII) and will sort immediately after
    the other explicitly-defined fields in that model — still well before
    the temporal metadata tier.
    """

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Soft-delete / audit standalone mixins
# ---------------------------------------------------------------------------


class SoftDeleteMixin(models.Model):
    """
    Adds soft-delete support: is_deleted + deleted_by.
    Apply alongside BaseModel or MasterBaseModel.
    """

    is_deleted = models.BooleanField(default=False)
    deleted_by = models.UUIDField(null=True, blank=True)

    class Meta:
        abstract = True


class AuditMixin(models.Model):
    """
    Adds created_by / updated_by UUID references (no DB-level FK to avoid
    circular imports).  For use as a standalone mixin on models that need
    explicit audit trail but do NOT inherit FullAuditMasterModel.
    """

    created_by = models.UUIDField(null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Full-spec abstract bases for new doc-defined masters
# ---------------------------------------------------------------------------


class FullAuditMasterModel(_MetadataFields, _AuditUserFields, _IsActiveMixin):
    """
    Abstract base for UUID PK global masters with full audit trail.

    Matches the standard 7-field + audit block from HRMS_ADMIN_SIDE.md:
      id, is_active, created_at, updated_at, deleted_at,
      created_by (UUID → employees), updated_by (UUID → employees),
      meta_data (JSONB).

    Column order achieved:
      id                     → NORMAL counter
      [subclass own fields]  → NORMAL counter (higher than base)
      is_active              → TIER_FLAG     700 001
      created_by, updated_by → TIER_AUDIT_FK 1 000 001+
      created_at …           → TIER_META     1 000 011+

    Use for masters NOT scoped to a company (e.g. mst_workflow_type,
    mst_approval_action, mst_audit_event_type, etc.).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CompanyMasterModel(FullAuditMasterModel):
    """
    Abstract base for UUID PK company-scoped masters with full audit trail.

    Column order achieved:
      id, company_id         → NORMAL counter  (structural identity)
      [subclass own fields]  → NORMAL counter  (higher than base)
      is_active              → TIER_FLAG     700 001
      created_by, updated_by → TIER_AUDIT_FK 1 000 001+
      created_at …           → TIER_META     1 000 011+

    company_id is stored as a plain UUID (no DB-level FK) to support
    schema-based multi-tenancy without cross-schema FK constraints.
    """

    company_id = models.UUIDField(
        null=False,
        blank=False,
        help_text="Owning company (logical FK → mst_company.id)",
    )

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Backward-compatible transaction aliases
# (used by employee.py and other transaction-layer models)
# ---------------------------------------------------------------------------


class TransactionBaseModel(BaseModel):
    """
    Alias for BaseModel.
    Provided for backward compatibility with models that import this name.
    """

    class Meta:
        abstract = True


class TransactionPIIBaseModel(PIIBaseModel):
    """
    Alias for PIIBaseModel.
    Provided for backward compatibility with models that import this name.
    """

    class Meta:
        abstract = True
