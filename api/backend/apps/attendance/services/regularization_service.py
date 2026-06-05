"""
RegularizationRequestService — thin domain service over WorkflowEngine.

Handles:
  - Employee: create / list own requests
  - Manager : list pending where they are current approver, approve/reject
  - Admin   : list all, approve/reject (admin is just another workflow step)

All approval logic is delegated to WorkflowEngine — no role hardcoding here.
"""

import uuid

from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.attendance.models.enums import (
    RequestWorkflowStatus,
    WorkflowTemplateType,
)
from apps.attendance.models.requests import RegularizationRequest
from apps.attendance.models.workflow import ApprovalRequestAction
from apps.attendance.services.workflow_engine import WorkflowEngine, WorkflowEngineError
from apps.employees.models.reporting import EmployeeReportingRelationship


class RegularizationRequestService:

    REQUEST_TYPE = WorkflowTemplateType.REGULARIZATION

    # ------------------------------------------------------------------
    # Employee — create
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create(employee, validated_data: dict) -> RegularizationRequest:
        """
        Employee submits a regularization request.
        Generates workflow_txn_id and kicks off the workflow engine.
        """
        txn_id = uuid.uuid4()

        reg_request = RegularizationRequest.objects.create(
            employee=employee,
            company=employee.company,
            workflow_txn_id=txn_id,
            status=RequestWorkflowStatus.PENDING,
            **validated_data,
        )
        reg_request.request_number = f"REG-{reg_request.id:04d}"
        reg_request.save(update_fields=["request_number"])

        engine = WorkflowEngine(
            request_type=WorkflowTemplateType.REGULARIZATION,
            request_id=txn_id,
            company_id=employee.company_id,
            employee=employee,
        )
        engine.initiate()

        return reg_request

    # ------------------------------------------------------------------
    # Querysets — RBAC
    # ------------------------------------------------------------------

    @staticmethod
    def get_queryset_for_employee(employee) -> QuerySet:
        """Employee sees only their own requests."""
        return (
            RegularizationRequest.objects
            .filter(employee=employee)
            .select_related("employee", "attendance", "reason_option")
            .order_by("-created_at")
        )

    @staticmethod
    def get_queryset_for_manager(manager_employee) -> QuerySet:
        """
        Manager sees requests where they are/were an approver.
        Resolved dynamically via ApprovalRequestAction.
        """
        # Include current pending approvals and requests already acted on by
        # this manager so approved/rejected history remains visible.
        manager_txn_ids = ApprovalRequestAction.objects.filter(
            request_type=WorkflowTemplateType.REGULARIZATION,
            approver=manager_employee,
        ).values_list("request_id", flat=True)

        return (
            RegularizationRequest.objects
            .filter(workflow_txn_id__in=manager_txn_ids)
            .select_related("employee", "attendance", "reason_option")
            .order_by("-created_at")
        )

    @staticmethod
    def get_queryset_for_admin(company_id) -> QuerySet:
        """Admin sees all requests in their company."""
        return (
            RegularizationRequest.objects
            .filter(company_id=company_id)
            .select_related("employee", "attendance", "reason_option")
            .order_by("-created_at")
        )

    # ------------------------------------------------------------------
    # Approve / Reject — same for manager and admin (engine decides)
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def approve(acting_employee, reg_request: RegularizationRequest, remarks: str = "") -> RegularizationRequest:
        """
        Any approver calls this. WorkflowEngine validates they are
        the correct person for the current step.
        """
        engine = WorkflowEngine(
            request_type=WorkflowTemplateType.REGULARIZATION,
            request_id=reg_request.workflow_txn_id,
            company_id=reg_request.company_id,
            employee=reg_request.employee,
        )

        new_status = engine.approve(acting_employee, remarks=remarks)
        reg_request.status = new_status
        reg_request.save(update_fields=["status", "updated_at"])
        return reg_request

    @staticmethod
    @transaction.atomic
    def reject(acting_employee, reg_request: RegularizationRequest, remarks: str = "") -> RegularizationRequest:
        engine = WorkflowEngine(
            request_type=WorkflowTemplateType.REGULARIZATION,
            request_id=reg_request.workflow_txn_id,
            company_id=reg_request.company_id,
            employee=reg_request.employee,
        )

        new_status = engine.reject(acting_employee, remarks=remarks)
        reg_request.status = new_status
        reg_request.save(update_fields=["status", "updated_at"])
        return reg_request

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    @staticmethod
    def get_timeline(reg_request: RegularizationRequest) -> list:
        engine = WorkflowEngine(
            request_type=WorkflowTemplateType.REGULARIZATION,
            request_id=reg_request.workflow_txn_id,
            company_id=reg_request.company_id,
            employee=reg_request.employee,
        )
        return engine.get_timeline()
