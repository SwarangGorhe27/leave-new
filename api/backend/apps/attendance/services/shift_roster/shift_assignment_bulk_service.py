"""Service layer for bulk shift assignment operations."""

import logging
import uuid
from typing import List, Dict, Tuple, Optional
from datetime import date, datetime, timedelta
from dataclasses import dataclass, asdict, field

from django.db import transaction
from django.contrib.auth.models import User

from apps.attendance.models import (
    EmployeeShiftRoster,
    AttendanceJob,
    AttendanceJobType,
    AttendanceJobStatus,
    HRAttendanceAuditLog,
    AuditActionType,
    AuditActionSource,
)
from apps.attendance.validators.employee.shift_assignment_validator import (
    ShiftAssignmentValidator,
)
from apps.attendance.services.shift_roster.shift_assignment_service import (
    ShiftAssignmentService,
)

logger = logging.getLogger(__name__)


@dataclass
class BulkAssignmentSummary:
    """Summary of bulk assignment results."""
    total_items: int = 0
    successful_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    duplicate_count: int = 0
    inactive_count: int = 0
    success_rate: float = 0.0


@dataclass
class BulkAssignmentItem:
    """Result of processing single item in bulk assignment."""
    index: int
    employee_id: uuid.UUID
    shift_id: uuid.UUID
    success: bool
    assignment_id: Optional[uuid.UUID] = None
    error: Optional[str] = None
    warning: Optional[str] = None


class BulkShiftAssignmentService:
    """Service for bulk shift assignment operations."""

    def __init__(self, company_id: uuid.UUID = None, user: User = None):
        """Initialize service with context."""
        self.company_id = company_id
        self.user = user
        self.validator = ShiftAssignmentValidator(company_id)
        self.assignment_service = ShiftAssignmentService(company_id, user)

    def validate_bulk_assignment(
        self,
        cycle_id: uuid.UUID,
        date_from: date,
        date_to: date,
        assignments: List[Dict],
        check_duplicates: bool = True,
        check_overlapping: bool = True,
        check_inactive: bool = True,
    ) -> Tuple[bool, Dict]:
        """
        Pre-validate bulk assignment data.
        
        Returns:
            Tuple of (can_proceed, validation_result)
        """
        result = {
            "valid_count": 0,
            "invalid_count": 0,
            "duplicate_count": 0,
            "inactive_count": 0,
            "warnings": [],
            "errors": [],
            "invalid_items": [],
        }

        try:
            # Validate date range
            if not self.validator.validate_date_range(date_from, date_to):
                result["errors"].extend(self.validator.get_validation_errors())
                self.validator.clear()
                return False, result

            # Validate cycle
            is_valid, cycle = self.validator.validate_cycle(cycle_id)
            if not is_valid:
                result["errors"].extend(self.validator.get_validation_errors())
                self.validator.clear()
                return False, result
            self.validator.clear()

            # Validate date range fits in cycle
            if not (cycle.start_date <= date_from and date_to <= cycle.end_date):
                result["errors"].append(
                    f"Date range ({date_from} - {date_to}) is outside cycle "
                    f"({cycle.start_date} - {cycle.end_date})."
                )
                return False, result

            # Validate each assignment
            duplicate_pairs = set()
            inactive_employees = set()

            for idx, assignment in enumerate(assignments):
                employee_id = assignment.get("employee_id")
                shift_id = assignment.get("shift_id")
                item_errors = []

                # Check for duplicate in this batch
                pair_key = f"{employee_id}_{shift_id}"
                if pair_key in duplicate_pairs:
                    result["invalid_items"].append({
                        "index": idx,
                        "employee_id": str(employee_id),
                        "shift_id": str(shift_id),
                        "error": "Duplicate employee-shift combination in batch.",
                    })
                    result["duplicate_count"] += 1
                    result["invalid_count"] += 1
                    continue

                duplicate_pairs.add(pair_key)

                # Validate employee
                is_valid, employee = self.validator.validate_employee(employee_id)
                if not is_valid:
                    item_errors.extend(self.validator.get_validation_errors())
                    self.validator.clear()
                    result["invalid_items"].append({
                        "index": idx,
                        "employee_id": str(employee_id),
                        "shift_id": str(shift_id),
                        "error": "; ".join(item_errors),
                    })
                    result["invalid_count"] += 1
                    continue

                # Check inactive employee
                if check_inactive and (not employee.is_active or employee.status != "ACTIVE"):
                    if check_inactive:
                        inactive_employees.add(employee_id)
                        result["inactive_count"] += 1
                        logger.warning(f"Employee {employee_id} is inactive - skipped.")
                        continue

                # Validate shift
                is_valid, shift = self.validator.validate_shift(shift_id)
                if not is_valid:
                    item_errors.extend(self.validator.get_validation_errors())
                    self.validator.clear()
                    result["invalid_items"].append({
                        "index": idx,
                        "employee_id": str(employee_id),
                        "shift_id": str(shift_id),
                        "error": "; ".join(item_errors),
                    })
                    result["invalid_count"] += 1
                    continue

                # Validate date range coverage
                if not (cycle.start_date <= date_from and date_to <= cycle.end_date):
                    item_errors.append("Date range is outside cycle.")
                    result["invalid_items"].append({
                        "index": idx,
                        "employee_id": str(employee_id),
                        "shift_id": str(shift_id),
                        "error": "; ".join(item_errors),
                    })
                    result["invalid_count"] += 1
                    continue

                # Check for existing assignments if checking duplicates
                if check_duplicates:
                    existing = self.validator.check_existing_assignments_in_range(
                        employee_id,
                        date_from,
                        date_to,
                    )
                    if existing:
                        result["warnings"].append(
                            f"Employee {employee_id} has {existing.count()} existing "
                            f"assignments in date range."
                        )

                result["valid_count"] += 1
                self.validator.clear()

            result["total_items"] = len(assignments)
            can_proceed = result["invalid_count"] == 0

            return can_proceed, result

        except Exception as e:
            logger.error(
                f"Error validating bulk assignment: {str(e)}",
                exc_info=True,
            )
            result["errors"].append(f"Validation failed: {str(e)}")
            return False, result

    def create_bulk_job(
        self,
        cycle_id: uuid.UUID,
        assignments: List[Dict],
        assignment_type: str = "single_date",
        date_from: date = None,
        date_to: date = None,
        recurring_days: List[int] = None,
        skip_duplicates: bool = True,
        skip_overlapping: bool = True,
        skip_inactive: bool = True,
        notify_employees: bool = False,
    ) -> Tuple[bool, Optional[AttendanceJob], List[str]]:
        """
        Create a bulk assignment job and store it for async processing.
        
        Returns:
            Tuple of (success, job_object, errors_list)
        """
        errors = []

        try:
            with transaction.atomic():
                # Validate inputs
                if assignment_type == "single_date" and not date_from:
                    return False, None, ["date_from is required for single_date assignment type."]

                if assignment_type == "date_range" and (not date_from or not date_to):
                    return False, None, ["date_from and date_to are required for date_range assignment type."]

                if assignment_type == "recurring" and not recurring_days:
                    return False, None, ["recurring_days is required for recurring assignment type."]

                # Create job record
                job_metadata = {
                    "cycle_id": str(cycle_id),
                    "assignment_type": assignment_type,
                    "date_from": str(date_from) if date_from else None,
                    "date_to": str(date_to) if date_to else None,
                    "recurring_days": recurring_days,
                    "assignments_count": len(assignments),
                    "skip_duplicates": skip_duplicates,
                    "skip_overlapping": skip_overlapping,
                    "skip_inactive": skip_inactive,
                    "notify_employees": notify_employees,
                }

                job = AttendanceJob.objects.create(
                    company_id=self.company_id,
                    job_type=AttendanceJobType.BULK_SHIFT_ASSIGNMENT,
                    status=AttendanceJobStatus.PENDING,
                    total_items=len(assignments),
                    processed_items=0,
                    success_count=0,
                    failure_count=0,
                    skip_count=0,
                    metadata=job_metadata,
                    extra_data={"assignments": assignments},
                    created_by_id=self.user.id if self.user else None,
                    created_by_system="SHIFT_ASSIGNMENT_API",
                )

                logger.info(
                    f"Bulk assignment job created: {job.id} with "
                    f"{len(assignments)} assignments"
                )

                return True, job, []

        except Exception as e:
            logger.error(
                f"Error creating bulk assignment job: {str(e)}",
                exc_info=True,
            )
            errors.append(f"Failed to create bulk job: {str(e)}")
            return False, None, errors

    def process_bulk_assignment(
        self,
        job_id: uuid.UUID,
    ) -> Tuple[bool, BulkAssignmentSummary, List[BulkAssignmentItem]]:
        """
        Process bulk assignment job synchronously (or called from async task).
        
        Returns:
            Tuple of (success, summary, processed_items)
        """
        processed_items: List[BulkAssignmentItem] = []
        summary = BulkAssignmentSummary()

        try:
            with transaction.atomic():
                # Get job
                try:
                    job = AttendanceJob.objects.get(id=job_id)
                except AttendanceJob.DoesNotExist:
                    logger.error(f"Bulk assignment job not found: {job_id}")
                    return False, summary, processed_items

                # Update job status
                job.status = AttendanceJobStatus.PROCESSING
                job.started_at = datetime.now()
                job.save(update_fields=["status", "started_at"])

                # Get assignment data
                assignments = job.extra_data.get("assignments", [])
                metadata = job.metadata

                cycle_id = uuid.UUID(metadata.get("cycle_id"))
                assignment_type = metadata.get("assignment_type", "single_date")
                date_from = datetime.fromisoformat(metadata.get("date_from")).date() if metadata.get("date_from") else None
                date_to = datetime.fromisoformat(metadata.get("date_to")).date() if metadata.get("date_to") else None
                recurring_days = metadata.get("recurring_days")
                skip_duplicates = metadata.get("skip_duplicates", True)
                skip_inactive = metadata.get("skip_inactive", True)

                summary.total_items = len(assignments)

                # Process each assignment
                for idx, assignment in enumerate(assignments):
                    employee_id = assignment.get("employee_id")
                    shift_id = assignment.get("shift_id")

                    try:
                        # Generate dates based on assignment type
                        dates = self.validator.generate_dates_for_bulk(
                            assignment_type,
                            date_from=date_from,
                            date_to=date_to,
                            recurring_days=recurring_days,
                            start_date=date_from,
                        )

                        item_success = False

                        for roster_date in dates:
                            # Create assignment
                            success, assignment_obj, warnings = self.assignment_service.create_assignment(
                                employee_id=uuid.UUID(str(employee_id)),
                                shift_id=uuid.UUID(str(shift_id)),
                                roster_date=roster_date,
                                cycle_id=cycle_id,
                                is_week_off=assignment.get("is_week_off", False),
                                override_reason=assignment.get("override_reason"),
                            )

                            if success:
                                item_success = True
                                summary.successful_count += 1
                            elif skip_duplicates and "Assignment already exists" in str(warnings):
                                summary.skipped_count += 1
                            else:
                                summary.failed_count += 1

                        if item_success:
                            processed_items.append(BulkAssignmentItem(
                                index=idx,
                                employee_id=employee_id,
                                shift_id=shift_id,
                                success=True,
                                assignment_id=uuid.UUID(str(assignment_obj.id)) if assignment_obj else None,
                            ))
                        else:
                            processed_items.append(BulkAssignmentItem(
                                index=idx,
                                employee_id=employee_id,
                                shift_id=shift_id,
                                success=False,
                                error="Failed to create assignments for all dates.",
                            ))

                    except Exception as e:
                        logger.error(
                            f"Error processing bulk assignment item {idx}: {str(e)}",
                            exc_info=True,
                        )
                        summary.failed_count += 1
                        processed_items.append(BulkAssignmentItem(
                            index=idx,
                            employee_id=employee_id,
                            shift_id=shift_id,
                            success=False,
                            error=str(e),
                        ))

                    # Update job progress
                    job.processed_items = idx + 1
                    job.success_count = summary.successful_count
                    job.failure_count = summary.failed_count
                    job.skip_count = summary.skipped_count
                    job.save(update_fields=[
                        "processed_items",
                        "success_count",
                        "failure_count",
                        "skip_count",
                    ])

                # Mark job as completed
                job.status = AttendanceJobStatus.COMPLETED
                job.completed_at = datetime.now()
                job.save(update_fields=["status", "completed_at"])

                # Log audit
                self._log_bulk_audit(job_id, summary, len(processed_items))

                logger.info(
                    f"Bulk assignment job completed: {job_id}. "
                    f"Success: {summary.successful_count}, "
                    f"Failed: {summary.failed_count}, "
                    f"Skipped: {summary.skipped_count}"
                )

                return True, summary, processed_items

        except Exception as e:
            logger.error(
                f"Error processing bulk assignment job: {str(e)}",
                exc_info=True,
                extra={"job_id": job_id},
            )
            # Mark job as failed
            try:
                job = AttendanceJob.objects.get(id=job_id)
                job.status = AttendanceJobStatus.FAILED
                job.completed_at = datetime.now()
                job.error_message = str(e)
                job.save(update_fields=["status", "completed_at", "error_message"])
            except Exception as save_error:
                logger.error(
                    "Failed to mark bulk assignment job as failed: %s",
                    save_error,
                    exc_info=True,
                    extra={"job_id": job_id},
                )

            return False, summary, processed_items

    def get_job_status(self, job_id: uuid.UUID) -> Tuple[bool, Dict, List[str]]:
        """Get status of a bulk assignment job."""
        try:
            job = AttendanceJob.objects.get(id=job_id)

            return True, {
                "job_id": str(job.id),
                "status": job.status,
                "progress": int((job.processed_items / job.total_items * 100) if job.total_items > 0 else 0),
                "total_items": job.total_items,
                "processed_items": job.processed_items,
                "success_count": job.success_count,
                "failure_count": job.failure_count,
                "skip_count": job.skip_count,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error_message": job.error_message,
            }, []

        except AttendanceJob.DoesNotExist:
            return False, {}, ["Job not found."]
        except Exception as e:
            logger.error(
                f"Error getting bulk assignment job status: {str(e)}",
                exc_info=True,
                extra={"job_id": job_id},
            )
            return False, {}, [f"Failed to get job status: {str(e)}"]

    def _log_bulk_audit(self, job_id: uuid.UUID, summary: BulkAssignmentSummary, item_count: int):
        """Log audit trail for bulk assignment."""
        try:
            HRAttendanceAuditLog.objects.create(
                company_id=self.company_id,
                action_type=AuditActionType.BULK_ASSIGN,
                action_source=AuditActionSource.API,
                entity_type="BulkShiftAssignment",
                entity_id=str(job_id),
                details={
                    "total_items": summary.total_items,
                    "successful": summary.successful_count,
                    "failed": summary.failed_count,
                    "skipped": summary.skipped_count,
                },
                created_by_id=self.user.id if self.user else None,
                created_by_system="BULK_ASSIGNMENT_API",
            )
        except Exception as e:
            logger.error(f"Failed to log bulk audit: {str(e)}", exc_info=True)
