"""
OvertimeRequestService — mirrors RegularizationRequestService.
Uses WorkflowTemplateType.OT template from DB.
"""

import uuid

from django.db import transaction
from django.db.models import QuerySet

from apps.attendance.models.enums import (
    RequestWorkflowStatus,
    WorkflowTemplateType,
)
from apps.attendance.models.requests import OvertimeRequest
from apps.attendance.models.workflow import ApprovalRequestAction
from apps.attendance.services.workflow_engine import WorkflowEngine


class OvertimeRequestService:

    REQUEST_TYPE = WorkflowTemplateType.OT

    @staticmethod
    @transaction.atomic
    def create(employee, validated_data: dict) -> OvertimeRequest:
        txn_id = uuid.uuid4()

        ot_request = OvertimeRequest.objects.create(
            employee=employee,
            company=employee.company,
            workflow_txn_id=txn_id,
            status=RequestWorkflowStatus.PENDING,
            **validated_data,
        )

        engine = WorkflowEngine(
            request_type=WorkflowTemplateType.OT,
            request_id=txn_id,
            company_id=employee.company_id,
            employee=employee,
        )
        engine.initiate()

        return ot_request

    @staticmethod
    def get_queryset_for_employee(employee) -> QuerySet:
        return (
            OvertimeRequest.objects
            .filter(employee=employee)
            .select_related("employee", "attendance")
            .order_by("-created_at")
        )

    @staticmethod
    def get_queryset_for_manager(manager_employee) -> QuerySet:
        manager_txn_ids = ApprovalRequestAction.objects.filter(
            request_type=WorkflowTemplateType.OT,
            approver=manager_employee,
        ).values_list("request_id", flat=True)

        return (
            OvertimeRequest.objects
            .filter(workflow_txn_id__in=manager_txn_ids)
            .select_related("employee", "attendance")
            .order_by("-created_at")
        )

    @staticmethod
    def get_queryset_for_admin(company_id) -> QuerySet:
        return (
            OvertimeRequest.objects
            .filter(company_id=company_id)
            .select_related("employee", "attendance")
            .order_by("-created_at")
        )

    @staticmethod
    @transaction.atomic
    def approve(acting_employee, ot_request: OvertimeRequest, remarks: str = "", approved_ot_mins: int = None) -> OvertimeRequest:
        engine = WorkflowEngine(
            request_type=WorkflowTemplateType.OT,
            request_id=ot_request.workflow_txn_id,
            company_id=ot_request.company_id,
            employee=ot_request.employee,
        )

        new_status = engine.approve(acting_employee, remarks=remarks)
        ot_request.status = new_status

        # Final approver sets the official approved minutes
        if new_status == RequestWorkflowStatus.APPROVED and approved_ot_mins is not None:
            ot_request.approved_ot_mins = approved_ot_mins
            ot_request.approved_by = acting_employee
            ot_request.approved_at = __import__('django.utils.timezone', fromlist=['timezone']).timezone.now()

        ot_request.save()
        return ot_request

    @staticmethod
    @transaction.atomic
    def reject(acting_employee, ot_request: OvertimeRequest, remarks: str = "") -> OvertimeRequest:
        engine = WorkflowEngine(
            request_type=WorkflowTemplateType.OT,
            request_id=ot_request.workflow_txn_id,
            company_id=ot_request.company_id,
            employee=ot_request.employee,
        )

        new_status = engine.reject(acting_employee, remarks=remarks)
        ot_request.status = new_status
        ot_request.save(update_fields=["status", "updated_at"])
        return ot_request

    @staticmethod
    def get_timeline(ot_request: OvertimeRequest) -> list:
        engine = WorkflowEngine(
            request_type=WorkflowTemplateType.OT,
            request_id=ot_request.workflow_txn_id,
            company_id=ot_request.company_id,
            employee=ot_request.employee,
        )
        return engine.get_timeline()
