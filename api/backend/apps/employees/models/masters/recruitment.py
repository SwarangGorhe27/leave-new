"""
Recruitment Masters — C.5 from HRMS_ADMIN_SIDE.md

Tables (7):
  mst_job_function     — Job Function Master (ENG/SALES/HR/FIN)
  mst_job_level        — Job Level / Seniority (JR/SR/LEAD/MGR/DIRECTOR)
  mst_interview_round  — Interview Round Types
  mst_candidate_source — Candidate Sourcing Channel
  mst_offer_status     — Offer Letter Status
  mst_rejection_reason — Candidate Rejection Reasons
  mst_pipeline_stage   — ATS Pipeline Stages

PostgreSQL schema: employee
"""

from django.db import models

from ..base import CompanyMasterModel, FullAuditMasterModel


# ---------------------------------------------------------------------------
# mst_job_function
# ---------------------------------------------------------------------------


class JobFunction(FullAuditMasterModel):
    """Job Function Master — ENG / SALES / HR / FIN etc. Global master."""

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "mst_job_function"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_jobfunc_code"),
        ]


# ---------------------------------------------------------------------------
# mst_job_level
# ---------------------------------------------------------------------------


class JobLevel(FullAuditMasterModel):
    """Job Level / Seniority — JR / SR / LEAD / MGR / DIRECTOR."""

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_job_level"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_joblevel_code"),
        ]


# ---------------------------------------------------------------------------
# mst_interview_round
# ---------------------------------------------------------------------------


class InterviewRound(FullAuditMasterModel):
    """Interview Round Types — SCREENING / TECHNICAL / HR / MANAGERIAL / FINAL."""

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "mst_interview_round"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_intrnd_code"),
        ]


# ---------------------------------------------------------------------------
# mst_candidate_source
# ---------------------------------------------------------------------------


class CandidateSource(FullAuditMasterModel):
    """
    Candidate Sourcing Channel — NAUKRI / LINKEDIN / REFERRAL / CAMPUS / WALKIN.
    source_category CHECK IN (ACTIVE, PASSIVE, REFERRAL, CAMPUS, AGENCY).
    """

    class SourceCategory(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        PASSIVE = "PASSIVE", "Passive"
        REFERRAL = "REFERRAL", "Referral"
        CAMPUS = "CAMPUS", "Campus"
        AGENCY = "AGENCY", "Agency"

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    source_category = models.CharField(
        max_length=30, choices=SourceCategory.choices, null=True, blank=True
    )

    class Meta:
        db_table = "mst_candidate_source"
        indexes = [
            models.Index(fields=["source_category"], name="idx_mst_cansrc_cat"),
            models.Index(fields=["code"], name="idx_mst_cansrc_code"),
        ]


# ---------------------------------------------------------------------------
# mst_offer_status
# ---------------------------------------------------------------------------


class OfferStatus(FullAuditMasterModel):
    """
    Offer Letter Status — DRAFT / SENT / ACCEPTED / DECLINED / LAPSED / REVOKED.
    """

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_terminal = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_offer_status"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_offstatus_code"),
            models.Index(fields=["is_terminal"], name="idx_mst_offstatus_terminal"),
        ]


# ---------------------------------------------------------------------------
# mst_rejection_reason
# ---------------------------------------------------------------------------


class RejectionReason(CompanyMasterModel):
    """Candidate Rejection Reasons — company-scoped."""

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    rejection_stage = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        db_table = "mst_rejection_reason"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_rejreason_co"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_rejreason_co_code"
            ),
        ]


# ---------------------------------------------------------------------------
# mst_pipeline_stage
# ---------------------------------------------------------------------------


class PipelineStage(CompanyMasterModel):
    """
    ATS Pipeline Stages — SCREENING / INTERVIEW / OFFER / JOINED / REJECTED.
    is_terminal marks end-of-pipeline stages.
    """

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    sort_order = models.SmallIntegerField(default=0)
    is_terminal = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_pipeline_stage"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_pipstage_co"),
            models.Index(fields=["is_terminal"], name="idx_mst_pipstage_terminal"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "sort_order"],
                name="uq_mst_pipstage_co_order",
            ),
        ]
