"""
WorkflowEngine — generic, step-driven approval engine.

Supports any request type (REGULARIZATION, OT, COMP_OFF, LEAVE).
Resolves approvers at runtime from reporting relationships and roles.
No hardcoded manager/admin hierarchy anywhere.

Usage
-----
    engine = WorkflowEngine(
        request_type=WorkflowTemplateType.REGULARIZATION,
        request_id=reg_request.workflow_txn_id,
        company_id=reg_request.company_id,
        employee=reg_request.employee,          # the requester
    )
    engine.initiate()                           # call once on create
    engine.approve(acting_employee, remarks="")
    engine.reject(acting_employee, remarks="")
    engine.current_pending_step()               # returns step or None
    engine.get_current_approver()               # returns Employee or None
"""

import uuid
from typing import Optional

from django.db import transaction
from django.utils import timezone

from apps.attendance.models.enums import (
    ApprovalActionStatus,
    ApproverRoleKind,
    RequestWorkflowStatus,
    WorkflowTemplateType,
)
from apps.attendance.models.workflow import (
    ApprovalRequestAction,
    ApprovalWorkflowStep,
    ApprovalWorkflowTemplate,
)
from apps.employees.models.reporting import EmployeeReportingRelationship


class WorkflowEngineError(Exception):
    pass


class WorkflowEngine:
    """
    Stateless engine — instantiate per request, call methods as needed.

    Parameters
    ----------
    request_type : WorkflowTemplateType value
    request_id   : UUID — the workflow_txn_id stored on the domain model
    company_id   : UUID — used to look up the correct template
    employee     : Employee instance — the person who submitted the request
    """

    def __init__(
        self,
        request_type: str,
        request_id: uuid.UUID,
        company_id: uuid.UUID,
        employee,
    ):
        self.request_type = request_type
        self.request_id = request_id
        self.company_id = company_id
        self.employee = employee  # requester

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_template(self) -> ApprovalWorkflowTemplate:
        try:
            return ApprovalWorkflowTemplate.objects.get(
                company_id=self.company_id,
                workflow_type=self.request_type,
            )
        except ApprovalWorkflowTemplate.DoesNotExist:
            raise WorkflowEngineError(
                f"No approval workflow template configured for "
                f"'{self.request_type}' in this company. "
                f"Ask your admin to set it up."
            )

    def _get_steps(self) -> list[ApprovalWorkflowStep]:
        template = self._get_template()
        return list(
            template.steps.select_related("custom_approver")
            .order_by("step_order")
        )

    def _existing_actions(self) -> list[ApprovalRequestAction]:
        return list(
            ApprovalRequestAction.objects.filter(
                request_id=self.request_id,
                request_type=self.request_type,
            ).select_related("step", "approver")
            .order_by("step__step_order")
        )

    def _resolve_approver(self, step: ApprovalWorkflowStep):
        """
        Resolve the actual Employee who should approve this step.

        REPORTING_MANAGER → primary active manager of the requester
        DEPT_HEAD         → department head via reporting (FUNCTIONAL type)
        HR                → HR role lookup (company-level)
        CUSTOM            → step.custom_approver (stored directly)
        """
        kind = step.approver_type

        if kind == ApproverRoleKind.REPORTING_MANAGER:
            rel = (
                EmployeeReportingRelationship.objects.filter(
                    employee=self.employee,
                    relationship_type=EmployeeReportingRelationship.RelationshipType.PRIMARY,
                    is_active=True,
                    effective_to__isnull=True,
                )
                .select_related("reports_to_employee")
                .first()
            )
            if not rel:
                raise WorkflowEngineError(
                    f"Employee {self.employee} has no active primary reporting manager. "
                    f"Cannot route approval."
                )
            return rel.reports_to_employee

        if kind == ApproverRoleKind.DEPT_HEAD:
            rel = (
                EmployeeReportingRelationship.objects.filter(
                    employee=self.employee,
                    relationship_type=EmployeeReportingRelationship.RelationshipType.FUNCTIONAL,
                    is_active=True,
                    effective_to__isnull=True,
                )
                .select_related("reports_to_employee")
                .first()
            )
            if not rel:
                raise WorkflowEngineError(
                    f"Employee {self.employee} has no active functional/dept-head relationship."
                )
            return rel.reports_to_employee

        if kind == ApproverRoleKind.HR:
            # HR is any employee flagged as HR role in the same company.
            # Assumes Employee model has a role / is_hr field, or a group.
            # Adjust the filter to match your Employee model's HR designation.
            from apps.employees.models.employee import Employee  # local import to avoid circular

            hr_employee = (
                Employee.objects.filter(
                    company_id=self.company_id,
                    employment_details__designation__name__icontains="HR",
                    is_active=True,
                )
                .first()
            )
            if not hr_employee:
                raise WorkflowEngineError(
                    "No active HR employee found in this company to handle this step."
                )
            return hr_employee

        if kind == ApproverRoleKind.CUSTOM:
            if not step.custom_approver:
                raise WorkflowEngineError(
                    f"Step {step.step_order} is CUSTOM type but has no custom_approver set."
                )
            return step.custom_approver

        raise WorkflowEngineError(f"Unknown approver_type: {kind}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def current_pending_step(self) -> Optional[ApprovalWorkflowStep]:
        """Return the first step that has no APPROVED action yet."""
        steps = self._get_steps()
        actions = {a.step_id: a for a in self._existing_actions()}

        for step in steps:
            action = actions.get(step.id)
            if action is None or action.status == ApprovalActionStatus.PENDING:
                return step
        return None  # all steps done

    def get_current_approver(self):
        """Return the Employee who should act on the current pending step."""
        step = self.current_pending_step()
        if step is None:
            return None
        return self._resolve_approver(step)

    def can_act(self, acting_employee) -> bool:
        """Check whether acting_employee is the correct approver for current step."""
        current_approver = self.get_current_approver()
        if current_approver is None:
            return False
        return current_approver.id == acting_employee.id

    @transaction.atomic
    def initiate(self) -> ApprovalRequestAction:
        """
        Called when the employee submits a request.
        Creates the first pending action so the manager sees it immediately.
        """
        steps = self._get_steps()
        if not steps:
            raise WorkflowEngineError(
                "Workflow template has no steps configured."
            )

        first_step = steps[0]
        approver = self._resolve_approver(first_step)

        action = ApprovalRequestAction.objects.create(
            request_type=self.request_type,
            request_id=self.request_id,
            step=first_step,
            approver=approver,
            status=ApprovalActionStatus.PENDING,
            company_id=self.company_id,
        )
        return action

    @transaction.atomic
    def approve(self, acting_employee, remarks: str = "") -> str:
        """
        Approve the current pending step.

        Returns the new overall status:
          PENDING   — more steps remain
          APPROVED  — all steps done
        """
        step = self.current_pending_step()
        if step is None:
            raise WorkflowEngineError("All steps are already completed.")

        approver = self._resolve_approver(step)
        if approver.id != acting_employee.id:
            raise WorkflowEngineError(
                f"You are not the designated approver for this step. "
                f"Expected: {approver}."
            )

        # Mark current action approved
        ApprovalRequestAction.objects.filter(
            request_id=self.request_id,
            request_type=self.request_type,
            step=step,
        ).update(
            status=ApprovalActionStatus.APPROVED,
            acted_at=timezone.now(),
            remarks=remarks,
        )

        # Check if more steps remain
        steps = self._get_steps()
        current_index = next(i for i, s in enumerate(steps) if s.id == step.id)
        remaining = steps[current_index + 1:]

        if remaining:
            # Create pending action for next step
            next_step = remaining[0]
            next_approver = self._resolve_approver(next_step)
            ApprovalRequestAction.objects.create(
                request_type=self.request_type,
                request_id=self.request_id,
                step=next_step,
                approver=next_approver,
                status=ApprovalActionStatus.PENDING,
                company_id=self.company_id,
            )
            return RequestWorkflowStatus.PENDING  # still in flight

        return RequestWorkflowStatus.APPROVED  # final step done

    @transaction.atomic
    def reject(self, acting_employee, remarks: str = "") -> str:
        """
        Reject the current pending step. Terminates the workflow.
        Returns REJECTED status.
        """
        step = self.current_pending_step()
        if step is None:
            raise WorkflowEngineError("No pending step to reject.")

        approver = self._resolve_approver(step)
        if approver.id != acting_employee.id:
            raise WorkflowEngineError(
                f"You are not the designated approver for this step. "
                f"Expected: {approver}."
            )

        ApprovalRequestAction.objects.filter(
            request_id=self.request_id,
            request_type=self.request_type,
            step=step,
        ).update(
            status=ApprovalActionStatus.REJECTED,
            acted_at=timezone.now(),
            remarks=remarks,
        )

        return RequestWorkflowStatus.REJECTED

    def get_timeline(self) -> list[dict]:
        """
        Return full approval history for display on the frontend.
        """
        actions = self._existing_actions()
        steps = {s.id: s for s in self._get_steps()}

        timeline = []
        for action in actions:
            step = steps.get(action.step_id)
            timeline.append({
                "step_order": step.step_order if step else None,
                "approver_type": step.approver_type if step else None,
                "approver_name": str(action.approver) if action.approver else None,
                "status": action.status,
                "acted_at": action.acted_at,
                "remarks": action.remarks,
            })
        return timeline