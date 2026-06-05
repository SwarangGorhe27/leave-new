"""Service layer for shift assignment operations."""

import logging
import uuid
from typing import List, Dict, Tuple, Optional
from datetime import date, datetime, timedelta
from dataclasses import dataclass

from django.db import transaction
from django.contrib.auth.models import User
from django.db.models import Q, F, Prefetch

from apps.attendance.models import (
    EmployeeShiftRoster,
    ShiftDefinition,
    AttendanceCycle,
    HRAttendanceAuditLog,
    AuditActionType,
    AuditActionSource,
)
from apps.employees.models import Employee, Company
from apps.attendance.validators.employee.shift_assignment_validator import (
    ShiftAssignmentValidator,
)

logger = logging.getLogger(__name__)


@dataclass
class AssignmentResult:
    """Result of a single assignment operation."""
    success: bool
    assignment_id: Optional[str] = None
    employee_id: Optional[str] = None
    shift_id: Optional[str] = None
    roster_date: Optional[date] = None
    error: Optional[str] = None
    warning: Optional[str] = None


class ShiftAssignmentService:
    """Service for managing shift assignments."""

    def __init__(self, company_id: uuid.UUID = None, user: User = None):
        """Initialize service with context."""
        self.company_id = company_id
        self.user = user
        self.validator = ShiftAssignmentValidator(company_id)

    def create_assignment(
        self,
        employee_id: uuid.UUID,
        shift_id: uuid.UUID,
        roster_date: date,
        cycle_id: uuid.UUID,
        is_week_off: bool = False,
        override_reason: str = None,
    ) -> Tuple[bool, Optional[EmployeeShiftRoster], List[str]]:
        """
        Create a single shift assignment.
        
        Returns:
            Tuple of (success, assignment_object_or_none, errors_list)
        """
        errors = []

        try:
            with transaction.atomic():
                # Validate all inputs
                is_valid, employee = self.validator.validate_employee(employee_id)
                if not is_valid:
                    errors.extend(self.validator.get_validation_errors())
                    self.validator.clear()
                    return False, None, errors

                is_valid, shift = self.validator.validate_shift(shift_id)
                if not is_valid:
                    errors.extend(self.validator.get_validation_errors())
                    self.validator.clear()
                    return False, None, errors

                is_valid, cycle = self.validator.validate_cycle(cycle_id)
                if not is_valid:
                    errors.extend(self.validator.get_validation_errors())
                    self.validator.clear()
                    return False, None, errors

                # Validate date in cycle
                if not self.validator.validate_roster_date_in_cycle(roster_date, cycle):
                    errors.extend(self.validator.get_validation_errors())
                    self.validator.clear()
                    return False, None, errors

                # Check for duplicates
                if self.validator.check_duplicate_assignment(employee_id, roster_date):
                    errors.extend(self.validator.get_validation_errors())
                    self.validator.clear()
                    return False, None, errors

                # Create assignment
                assignment = EmployeeShiftRoster.objects.create(
                    employee_id=employee_id,
                    shift_id=shift_id,
                    roster_date=roster_date,
                    cycle_id=cycle_id,
                    company_id=self.company_id or employee.company_id,
                    is_week_off=is_week_off,
                    override_reason=override_reason,
                )

                # Log audit
                self._log_audit(
                    action_type=AuditActionType.ASSIGN,
                    entity_type="EmployeeShiftRoster",
                    entity_id=str(assignment.id),
                    details={
                        "employee_id": str(employee_id),
                        "shift_id": str(shift_id),
                        "roster_date": str(roster_date),
                        "is_week_off": is_week_off,
                    },
                )

                warnings = self.validator.get_validation_warnings()
                self.validator.clear()

                logger.info(
                    f"Shift assignment created: {assignment.id} for "
                    f"employee {employee_id} on {roster_date}"
                )

                return True, assignment, warnings

        except Exception as e:
            logger.error(
                f"Error creating shift assignment: {str(e)}",
                exc_info=True,
                extra={
                    "employee_id": employee_id,
                    "shift_id": shift_id,
                    "roster_date": roster_date,
                },
            )
            errors.append(f"Failed to create assignment: {str(e)}")
            return False, None, errors

    def update_assignment(
        self,
        assignment_id: uuid.UUID,
        shift_id: uuid.UUID = None,
        roster_date: date = None,
        is_week_off: bool = None,
        override_reason: str = None,
    ) -> Tuple[bool, Optional[EmployeeShiftRoster], List[str]]:
        """
        Update a shift assignment.
        
        Returns:
            Tuple of (success, assignment_object_or_none, errors_list)
        """
        errors = []

        try:
            with transaction.atomic():
                # Get existing assignment
                try:
                    assignment = EmployeeShiftRoster.objects.get(
                        id=assignment_id,
                        deleted_at__isnull=True,
                    )
                except EmployeeShiftRoster.DoesNotExist:
                    return False, None, ["Assignment not found."]

                # Store original values for audit
                original_values = {
                    "shift_id": str(assignment.shift_id),
                    "roster_date": str(assignment.roster_date),
                    "is_week_off": assignment.is_week_off,
                }

                # Validate new shift if provided
                if shift_id and shift_id != assignment.shift_id:
                    is_valid, shift = self.validator.validate_shift(shift_id)
                    if not is_valid:
                        errors.extend(self.validator.get_validation_errors())
                        self.validator.clear()
                        return False, None, errors
                    assignment.shift_id = shift_id

                # Validate new roster_date if provided
                if roster_date and roster_date != assignment.roster_date:
                    is_valid, cycle = self.validator.validate_cycle(assignment.cycle_id)
                    if not is_valid:
                        errors.extend(self.validator.get_validation_errors())
                        self.validator.clear()
                        return False, None, errors

                    if not self.validator.validate_roster_date_in_cycle(roster_date, cycle):
                        errors.extend(self.validator.get_validation_errors())
                        self.validator.clear()
                        return False, None, errors

                    # Check for duplicates on new date
                    if self.validator.check_duplicate_assignment(
                        assignment.employee_id,
                        roster_date,
                        exclude_id=assignment_id,
                    ):
                        errors.extend(self.validator.get_validation_errors())
                        self.validator.clear()
                        return False, None, errors

                    assignment.roster_date = roster_date

                # Update other fields
                if is_week_off is not None:
                    assignment.is_week_off = is_week_off
                if override_reason is not None:
                    assignment.override_reason = override_reason

                # Save updates
                assignment.save(update_fields=[
                    "shift_id",
                    "roster_date",
                    "is_week_off",
                    "override_reason",
                    "updated_at",
                ])

                # Log audit
                self._log_audit(
                    action_type=AuditActionType.UPDATE,
                    entity_type="EmployeeShiftRoster",
                    entity_id=str(assignment.id),
                    details={
                        "employee_id": str(assignment.employee_id),
                        "original": original_values,
                        "updated": {
                            "shift_id": str(shift_id) if shift_id else original_values["shift_id"],
                            "roster_date": str(roster_date) if roster_date else original_values["roster_date"],
                            "is_week_off": is_week_off if is_week_off is not None else original_values["is_week_off"],
                        },
                    },
                )

                logger.info(f"Shift assignment updated: {assignment.id}")

                return True, assignment, []

        except Exception as e:
            logger.error(
                f"Error updating shift assignment: {str(e)}",
                exc_info=True,
                extra={"assignment_id": assignment_id},
            )
            errors.append(f"Failed to update assignment: {str(e)}")
            return False, None, errors

    def delete_assignment(
        self,
        assignment_id: uuid.UUID,
    ) -> Tuple[bool, List[str]]:
        """
        Soft delete a shift assignment.
        
        Returns:
            Tuple of (success, errors_list)
        """
        errors = []

        try:
            with transaction.atomic():
                # Get assignment
                try:
                    assignment = EmployeeShiftRoster.objects.get(
                        id=assignment_id,
                        deleted_at__isnull=True,
                    )
                except EmployeeShiftRoster.DoesNotExist:
                    return False, ["Assignment not found."]

                # Soft delete
                assignment.deleted_at = datetime.now()
                assignment.save(update_fields=["deleted_at", "updated_at"])

                # Log audit
                self._log_audit(
                    action_type=AuditActionType.DELETE,
                    entity_type="EmployeeShiftRoster",
                    entity_id=str(assignment.id),
                    details={
                        "employee_id": str(assignment.employee_id),
                        "shift_id": str(assignment.shift_id),
                        "roster_date": str(assignment.roster_date),
                    },
                )

                logger.info(f"Shift assignment deleted: {assignment.id}")

                return True, []

        except Exception as e:
            logger.error(
                f"Error deleting shift assignment: {str(e)}",
                exc_info=True,
                extra={"assignment_id": assignment_id},
            )
            errors.append(f"Failed to delete assignment: {str(e)}")
            return False, errors

    def list_assignments(
        self,
        employee_id: uuid.UUID = None,
        shift_id: uuid.UUID = None,
        cycle_id: uuid.UUID = None,
        roster_date_from: date = None,
        roster_date_to: date = None,
        is_week_off: bool = None,
        department_id: uuid.UUID = None,
        company_id: uuid.UUID = None,
        search: str = None,
    ) -> Tuple[bool, List[EmployeeShiftRoster], List[str]]:
        """
        List shift assignments with filters.
        
        Returns:
            Tuple of (success, assignments_list, errors_list)
        """
        try:
            queryset = EmployeeShiftRoster.objects.filter(
                deleted_at__isnull=True,
            ).select_related(
                "employee",
                "employee__company",
                "employee__department",
                "shift",
                "cycle",
                "company",
            )

            # Apply filters
            if employee_id:
                queryset = queryset.filter(employee_id=employee_id)

            if shift_id:
                queryset = queryset.filter(shift_id=shift_id)

            if cycle_id:
                queryset = queryset.filter(cycle_id=cycle_id)

            if roster_date_from:
                queryset = queryset.filter(roster_date__gte=roster_date_from)

            if roster_date_to:
                queryset = queryset.filter(roster_date__lte=roster_date_to)

            if is_week_off is not None:
                queryset = queryset.filter(is_week_off=is_week_off)

            if department_id:
                queryset = queryset.filter(employee__department_id=department_id)

            if company_id:
                queryset = queryset.filter(company_id=company_id)
            elif self.company_id:
                queryset = queryset.filter(company_id=self.company_id)

            # Search by employee code, name, or shift code
            if search:
                queryset = queryset.filter(
                    Q(employee__employee_code__icontains=search)
                    | Q(employee__first_name__icontains=search)
                    | Q(employee__last_name__icontains=search)
                    | Q(shift__code__icontains=search)
                )

            # Order by roster_date descending
            queryset = queryset.order_by("-roster_date", "-created_at")

            return True, list(queryset), []

        except Exception as e:
            logger.error(
                f"Error listing shift assignments: {str(e)}",
                exc_info=True,
            )
            return False, [], [f"Failed to list assignments: {str(e)}"]

    def get_assignment(
        self,
        assignment_id: uuid.UUID,
    ) -> Tuple[bool, Optional[EmployeeShiftRoster], List[str]]:
        """Get a single shift assignment with full details."""
        try:
            assignment = EmployeeShiftRoster.objects.select_related(
                "employee",
                "employee__company",
                "shift",
                "cycle",
                "company",
            ).get(
                id=assignment_id,
                deleted_at__isnull=True,
            )
            return True, assignment, []

        except EmployeeShiftRoster.DoesNotExist:
            return False, None, ["Assignment not found."]
        except Exception as e:
            logger.error(
                f"Error getting shift assignment: {str(e)}",
                exc_info=True,
                extra={"assignment_id": assignment_id},
            )
            return False, None, [f"Failed to get assignment: {str(e)}"]

    def _log_audit(
        self,
        action_type: str,
        entity_type: str,
        entity_id: str,
        details: Dict = None,
    ):
        """Log audit trail for assignment changes."""
        try:
            HRAttendanceAuditLog.objects.create(
                company_id=self.company_id,
                action_type=action_type,
                action_source=AuditActionSource.API,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details or {},
                created_by_id=self.user.id if self.user else None,
                created_by_system="SHIFT_ASSIGNMENT_API",
            )
        except Exception as e:
            logger.error(f"Failed to log audit trail: {str(e)}", exc_info=True)
