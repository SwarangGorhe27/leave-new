"""Business logic for manual punch APIs."""

from __future__ import annotations

import csv
import io
import logging
from collections import Counter

import pandas as pd
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from apps.attendance.models import AuditActionSource, AuditActionType, HRAttendanceAuditLog, PunchSource
from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.serializers.swipe_logs.manual_punch_serializers import ManualPunchCreateSerializer
from apps.attendance.validators.manual_punch_validators import ManualPunchValidator
from apps.employees.models import Employee

logger = logging.getLogger(__name__)


class ManualPunchService:
    """Service handling manual punch CRUD, stats, and bulk import."""

    @staticmethod
    def _actor_employee(user):
        return getattr(user, "employee_profile", None) or getattr(user, "employee", None)

    @staticmethod
    def _base_queryset(company_id):
        return PunchLog.objects.filter(
            company_id=company_id,
            punch_source=PunchSource.MANUAL,
        ).exclude(meta_data__is_deleted=True).select_related("employee", "created_by")

    @staticmethod
    def _create_audit_log(*, company_id, record_id, action, changed_by_id=None, old_data=None, new_data=None):
        try:
            HRAttendanceAuditLog.objects.create(
                company_id=company_id,
                table_name="att_punch_log",
                record_id=str(record_id),
                action=action,
                old_data=old_data,
                new_data=new_data,
                changed_by_id=changed_by_id,
                action_source=AuditActionSource.HR_ADMIN if changed_by_id else AuditActionSource.SYSTEM,
            )
        except Exception:
            logger.warning("Failed to create manual punch audit log for %s", record_id, exc_info=True)

    @staticmethod
    def _build_meta(validated_data: dict, *, existing_meta: dict | None = None, actor=None) -> dict:
        meta = dict(existing_meta or {})
        if "manual_override_reason" in validated_data:
            meta["manual_override_reason"] = validated_data["manual_override_reason"]
        if "location_id" in validated_data:
            meta["location_id"] = str(validated_data["location_id"]) if validated_data["location_id"] else None
        if "ip_address" in validated_data:
            meta["ip_address"] = str(validated_data["ip_address"]) if validated_data["ip_address"] else None
        if "remarks" in validated_data:
            meta["remarks"] = validated_data["remarks"]
        if actor is not None:
            meta["manual_override_by"] = {
                "id": str(actor.id),
                "name": actor.full_name,
                "employee_code": actor.employee_code,
            }
        return meta

    @staticmethod
    def list_manual_punches(company_id, filters: dict):
        queryset = ManualPunchService._base_queryset(company_id)
        if filters.get("employee_id"):
            queryset = queryset.filter(employee_id=filters["employee_id"])
        if filters.get("punch_type"):
            queryset = queryset.filter(punch_type=filters["punch_type"])
        if filters.get("from_date"):
            queryset = queryset.filter(punch_time__date__gte=filters["from_date"])
        if filters.get("to_date"):
            queryset = queryset.filter(punch_time__date__lte=filters["to_date"])
        return queryset.order_by("-punch_time", "-created_at")

    @staticmethod
    def get_manual_punch(company_id, punch_id) -> PunchLog:
        punch = ManualPunchService._base_queryset(company_id).filter(id=punch_id).first()
        if punch is None:
            raise NotFound("Manual punch not found.")
        return punch

    @staticmethod
    def get_stats(company_id, filters: dict) -> dict:
        queryset = ManualPunchService.list_manual_punches(company_id, filters)
        by_type_counter = Counter(queryset.values_list("punch_type", flat=True))
        top_overriders = (
            queryset.filter(created_by_id__isnull=False)
            .values("created_by_id", "created_by__first_name", "created_by__last_name", "created_by__employee_code")
            .annotate(total=Count("id"))
            .order_by("-total", "created_by__first_name")[:5]
        )
        return {
            "total_manual_punches": queryset.count(),
            "by_type": [{"punch_type": key, "count": value} for key, value in by_type_counter.items()],
            "top_overriders": [
                {
                    "employee_id": str(item["created_by_id"]),
                    "employee_code": item["created_by__employee_code"],
                    "name": f'{item["created_by__first_name"]} {item["created_by__last_name"]}'.strip(),
                    "count": item["total"],
                }
                for item in top_overriders
            ],
        }

    @staticmethod
    def _validate_employee(company_id, employee_id) -> Employee:
        employee = Employee.objects.filter(id=employee_id, company_id=company_id, is_active=True).first()
        if employee is None:
            raise ValidationError({"employee_id": "Employee not found for this company."})
        return employee

    @staticmethod
    def _ensure_not_duplicate(*, company_id, employee_id, punch_time, punch_type, exclude_id=None):
        queryset = PunchLog.objects.filter(
            company_id=company_id,
            employee_id=employee_id,
            punch_source=PunchSource.MANUAL,
            punch_time__year=punch_time.year,
            punch_time__month=punch_time.month,
            punch_time__day=punch_time.day,
            punch_time__hour=punch_time.hour,
            punch_time__minute=punch_time.minute,
            punch_type=punch_type,
        ).exclude(meta_data__is_deleted=True)
        if exclude_id is not None:
            queryset = queryset.exclude(id=exclude_id)
        if queryset.exists():
            raise ValidationError(
                {"non_field_errors": ["A manual punch with this type and time already exists for this employee."]}
            )

    @staticmethod
    def _trigger_recompute(employee_id, punch_time):
        logger.info(
            "Manual punch recompute placeholder invoked",
            extra={"employee_id": str(employee_id), "attendance_date": punch_time.date().isoformat()},
        )
        return True

    @staticmethod
    @transaction.atomic
    def create_manual_punch(user, validated_data):
        try:
            actor = ManualPunchService._actor_employee(user)
            employee = ManualPunchService._validate_employee(validated_data["company_id"], validated_data["employee_id"])
            ManualPunchValidator.validate_creation(
                {
                    "company_id": validated_data["company_id"],
                    "employee_id": validated_data["employee_id"],
                    "punch_time": validated_data["punch_time"],
                    "punch_type": validated_data["punch_type"],
                }
            )

            punch_log = PunchLog.objects.create(
                company_id=validated_data["company_id"],
                employee=employee,
                punch_time=validated_data["punch_time"],
                punch_type=validated_data["punch_type"],
                punch_source=PunchSource.MANUAL,
                source="HR_PORTAL",
                device_id=validated_data.get("device_id"),
                is_trusted=True,
                created_by=actor,
                raw_payload={
                    "company_id": str(validated_data["company_id"]),
                    "employee_id": str(validated_data["employee_id"]),
                    "punch_time": validated_data["punch_time"].isoformat(),
                    "punch_type": validated_data["punch_type"],
                    "device_id": validated_data.get("device_id"),
                    "location_id": str(validated_data["location_id"]) if validated_data.get("location_id") else None,
                    "ip_address": validated_data.get("ip_address"),
                    "remarks": validated_data.get("remarks"),
                    "manual_override_reason": validated_data.get("manual_override_reason"),
                },
                meta_data=ManualPunchService._build_meta(validated_data, actor=actor),
            )

            ManualPunchService._create_audit_log(
                company_id=validated_data["company_id"],
                record_id=punch_log.id,
                action=AuditActionType.INSERT,
                changed_by_id=getattr(actor, "id", None),
                new_data={
                    "employee_id": str(employee.id),
                    "punch_time": punch_log.punch_time.isoformat(),
                    "punch_type": punch_log.punch_type,
                    "meta_data": punch_log.meta_data,
                    "raw_payload": punch_log.raw_payload,
                },
            )
            ManualPunchService._trigger_recompute(punch_log.employee_id, punch_log.punch_time)
            return punch_log
        except Exception:
            logger.exception(
                "Failed to create manual punch",
                extra={
                    "company_id": str(validated_data.get("company_id")),
                    "employee_id": str(validated_data.get("employee_id")),
                    "punch_type": validated_data.get("punch_type"),
                },
            )
            raise

    @staticmethod
    @transaction.atomic
    def update_manual_punch(user, punch_log: PunchLog, validated_data):
        actor = ManualPunchService._actor_employee(user)
        old_data = {
            "punch_time": punch_log.punch_time.isoformat(),
            "punch_type": punch_log.punch_type,
            "device_id": punch_log.device_id,
            "meta_data": dict(punch_log.meta_data or {}),
        }

        if "punch_time" in validated_data:
            if validated_data["punch_time"] > timezone.now():
                raise ValidationError({"punch_time": "Punch time cannot be in the future."})
            punch_log.punch_time = validated_data["punch_time"]
        if "punch_type" in validated_data:
            punch_log.punch_type = validated_data["punch_type"]
        if "device_id" in validated_data:
            punch_log.device_id = validated_data["device_id"]

        ManualPunchService._ensure_not_duplicate(
            company_id=punch_log.company_id,
            employee_id=punch_log.employee_id,
            punch_time=punch_log.punch_time,
            punch_type=punch_log.punch_type,
            exclude_id=punch_log.id,
        )

        punch_log.meta_data = ManualPunchService._build_meta(
            validated_data,
            existing_meta=punch_log.meta_data,
            actor=actor,
        )
        punch_log.meta_data["updated_at"] = timezone.now().isoformat()
        punch_log.meta_data["updated_by"] = str(actor.id) if actor else None
        punch_log.save(update_fields=["punch_time", "punch_type", "device_id", "meta_data"])

        ManualPunchService._create_audit_log(
            company_id=punch_log.company_id,
            record_id=punch_log.id,
            action=AuditActionType.UPDATE,
            changed_by_id=getattr(actor, "id", None),
            old_data=old_data,
            new_data={
                "punch_time": punch_log.punch_time.isoformat(),
                "punch_type": punch_log.punch_type,
                "device_id": punch_log.device_id,
                "meta_data": punch_log.meta_data,
            },
        )
        ManualPunchService._trigger_recompute(punch_log.employee_id, punch_log.punch_time)
        return punch_log

    @staticmethod
    @transaction.atomic
    def delete_manual_punch(user, punch_log: PunchLog, reason: str):
        actor = ManualPunchService._actor_employee(user)
        old_data = {"meta_data": dict(punch_log.meta_data or {})}
        punch_log.meta_data = dict(punch_log.meta_data or {})
        punch_log.meta_data["is_deleted"] = True
        punch_log.meta_data["deletion_reason"] = reason
        punch_log.meta_data["deleted_by"] = str(actor.id) if actor else None
        punch_log.meta_data["deleted_at"] = timezone.now().isoformat()
        punch_log.save(update_fields=["meta_data"])

        ManualPunchService._create_audit_log(
            company_id=punch_log.company_id,
            record_id=punch_log.id,
            action=AuditActionType.DELETE,
            changed_by_id=getattr(actor, "id", None),
            old_data=old_data,
            new_data={"meta_data": punch_log.meta_data},
        )
        ManualPunchService._trigger_recompute(punch_log.employee_id, punch_log.punch_time)
        return True

    @staticmethod
    def _read_bulk_rows(file_obj):
        if file_obj.name.lower().endswith(".csv"):
            decoded = file_obj.read().decode("utf-8-sig")
            return list(csv.DictReader(io.StringIO(decoded)))
        dataframe = pd.read_excel(file_obj)
        return dataframe.fillna("").to_dict(orient="records")

    @staticmethod
    @transaction.atomic
    def bulk_import(user, company_id, file, dry_run=False):
        rows = ManualPunchService._read_bulk_rows(file)
        results = {
            "total_rows": len(rows),
            "valid_rows": 0,
            "invalid_rows": 0,
            "created_rows": 0,
            "dry_run": dry_run,
            "errors": [],
        }

        for index, row in enumerate(rows, start=2):
            try:
                payload = {
                    "company_id": company_id,
                    "employee_id": row.get("employee_id"),
                    "punch_time": row.get("punch_time"),
                    "punch_type": row.get("punch_type"),
                    "device_id": row.get("device_id") or None,
                    "manual_override_reason": row.get("manual_override_reason") or row.get("reason") or "Bulk import",
                    "location_id": row.get("location_id") or None,
                    "ip_address": row.get("ip_address") or None,
                    "remarks": row.get("remarks") or None,
                }
                serializer = ManualPunchCreateSerializer(
                    data=payload,
                    context={"request": type("Req", (), {"user": user})()},
                )
                serializer.is_valid(raise_exception=True)
                results["valid_rows"] += 1
                if not dry_run:
                    ManualPunchService.create_manual_punch(user, serializer.validated_data)
                    results["created_rows"] += 1
            except Exception as exc:
                results["invalid_rows"] += 1
                results["errors"].append({"row": index, "reason": str(exc)})

        if dry_run:
            transaction.set_rollback(True)
        return results
