"""
attendance/services/ingest.py

Ingest service — the brain of the punch ingest pipeline.

Responsibilities:
  1. Resolve all employee codes in one bulk DB query (no N+1)
  2. Split punches into resolved and unresolved buckets
  3. Bulk insert resolved punches into att_punch_log (ignore_conflicts for dedup)
  4. Bulk insert unresolved punches into att_unmapped_punch_log
  5. Return a summary the view can return to the agent

Design decisions:
  - All DB writes happen in a single transaction — partial batch failures
    are rolled back cleanly
  - ignore_conflicts=True on bulk_create means the same punch sent twice
    (agent retry after a failed push) is silently ignored — no duplicates
  - Employee resolution uses bulk query — one DB round trip for the whole batch
  - View stays thin — zero business logic there
"""
import logging
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from apps.attendance.models import PunchLog, UnmappedPunchLog
from apps.attendance.utils.employee_resolver import (
    ResolutionFailure,
    ResolvedEmployee,
    resolve_employees_bulk,
)
from apps.attendance.models.enums import PunchSource
from decimal import Decimal

log = logging.getLogger(__name__)


@dataclass
class IngestSummary:
    """
    Result returned by the ingest service to the view.
    Mirrors the response payload the agent expects.
    """
    accepted:   int
    duplicates: int
    unmapped:   int
    errors:     list[str]


def ingest_punches(validated_punches: list[dict]) -> IngestSummary:
    """
    Full ingest pipeline for one batch of validated punch dicts.

    Args:
        validated_punches: List of dicts from BulkIngestSerializer.validated_data["punches"]
                           Each dict already has punch_type (not direction) after serializer validation.

    Returns:
        IngestSummary with accepted / duplicates / unmapped / errors counts.
    """
    if not validated_punches:
        return IngestSummary(accepted=0, duplicates=0, unmapped=0, errors=[])

    # ── Step 1: Resolve all employee codes in one query ───────────────────────
    employee_codes = [p["employee_code"] for p in validated_punches]
    resolution_map = resolve_employees_bulk(employee_codes)

    # ── Step 2: Split into resolved and unresolved buckets ────────────────────
    resolved_punches:   list[dict] = []
    unresolved_punches: list[dict] = []

    for punch in validated_punches:
        code   = punch["employee_code"]
        result = resolution_map.get(code)

        if isinstance(result, ResolvedEmployee):
            resolved_punches.append({**punch, "_resolved": result})
        else:
            reason = result.reason if isinstance(result, ResolutionFailure) else "Unknown resolution error"
            unresolved_punches.append({**punch, "_reason": reason})

    log.info(
        "Ingest batch: total=%d resolved=%d unresolved=%d",
        len(validated_punches),
        len(resolved_punches),
        len(unresolved_punches),
    )

    accepted   = 0
    duplicates = 0
    unmapped   = 0
    errors     = []

    with transaction.atomic():

        # ── Step 3: Bulk insert resolved punches ──────────────────────────────
        if resolved_punches:
            punch_objects = [
                PunchLog(
                    company_id        = p["_resolved"].company_id,
                    employee_id       = p["_resolved"].employee_id,
                    essl_log_id       = p["essl_log_id"],
                    essl_source_table = p.get("essl_source_table") or "",
                    punch_time        = p["punch_time"],
                    punch_type        = p["direction"] ,
                    punch_source      = PunchSource.BIOMETRIC,
                    essl_device_id    = p.get("device_id"),
                    latitude          = p.get("latitude"),
                    longitude         = p.get("longitude"),
                    raw_payload       = _build_raw_payload(p),
                    source             = p.get("source", "ESSL"),
                    # punch_mode         = p.get("punch_mode"),
                    # face_verified      = p.get("face_verified"),
                    meta_data          = p.get("meta_data", {}),
                    # is_within_geofence = p.get("is_within_geofence"),
                )
                for p in resolved_punches
            ]

            # ignore_conflicts=True — ON CONFLICT DO NOTHING on the
            # unique_together(essl_log_id, essl_source_table) constraint.
            # Django returns only the actually inserted rows in created list.
            created = PunchLog.objects.bulk_create(
                punch_objects,
                ignore_conflicts=True,
                batch_size=500,
            )
            accepted   = len(created)
            duplicates = len(resolved_punches) - accepted

            log.info(
                "att_punch_log: inserted=%d duplicates_skipped=%d",
                accepted, duplicates,
            )

        # ── Step 4: Bulk insert unresolved punches ────────────────────────────
        # Company is unknown — we can't resolve it without the employee.
        # UnmappedPunchLog.company is required (NOT NULL) per base model,
        # so we need a fallback. Options:
        #   a) Make company nullable on UnmappedPunchLog only
        #   b) Use a sentinel "unknown" company
        # We go with (a) — override company to nullable in UnmappedPunchLog.
        # See UnmappedPunchLog.Meta for the override.
        if unresolved_punches:
            unmapped_objects = [
                UnmappedPunchLog(
                    # company_id intentionally null — can't resolve without employee
                    essl_user_id      = p["employee_code"],
                    essl_log_id       = p["essl_log_id"],
                    essl_source_table = p.get("essl_source_table"),
                    punch_time        = p["punch_time"],
                    punch_type        = p["punch_type"],
                    device_id         = p.get("device_id"),
                    reason            = p["_reason"],
                    raw_payload       = _build_raw_payload(p),
                )
                for p in unresolved_punches
            ]

            UnmappedPunchLog.objects.bulk_create(
                unmapped_objects,
                ignore_conflicts=True,  # dedup on (essl_log_id, essl_source_table)
                batch_size=500,
            )
            unmapped = len(unresolved_punches)

            log.warning(
                "att_unmapped_punch_log: stored=%d unresolved punches. "
                "Codes: %s",
                unmapped,
                list({p["employee_code"] for p in unresolved_punches})[:10],
            )

    return IngestSummary(
        accepted=accepted,
        duplicates=duplicates,
        unmapped=unmapped,
        errors=errors,
    )


def _build_raw_payload(punch: dict) -> dict:
    """
    Build the raw_payload JSON from a punch dict.
    Strips internal keys (prefixed with _) used only by the service.
    Serialises punch_time to ISO string for JSON compatibility.
    """
    payload = {}

    for key, value in punch.items():
        if key.startswith("_"):
            continue

        if hasattr(value, "isoformat"):
            payload[key] = value.isoformat()
        elif isinstance(value, Decimal):
            payload[key] = str(value)
        else:
            payload[key] = value

    return payload