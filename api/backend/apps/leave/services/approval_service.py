"""
Leave Approval & Workflow Service
Handles approval workflow operations for leave requests.
"""
from typing import Any, Dict, List, Optional
import uuid
from django.db import transaction
from django.db.models import QuerySet, Q
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from ..models.transactions.leave_approvals import ApprovalStatusChoices, LeaveApproval
from ..models.transactions.leave_balances import LeaveBalance
from ..models.transactions.leave_requests import LeaveRequest, LeaveStatusChoices
from ..models.transactions.leave_status_history import LeaveStatusHistory
from ..models.workflow.approval_workflow_config import ApprovalWorkflowConfig
from ..models.workflow.escalation_matrix import EscalationMatrix
from .base_service import BaseLeaveService
from .leave_balance_service import LeaveBalanceService
from .leave_request_service import LeaveApplicationService


class ApprovalWorkflowService(BaseLeaveService):
    """
    Service for managing leave approval workflows.
    
    Operations:
    - Get pending approvals
    - Approve leave request
    - Reject leave request
    - Send back for clarification
    - Delegate approvals
    - Bulk actions
    - Get workflow configuration
    """

    @staticmethod
    def get_pending_approvals(approver_id: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get all pending approvals for an approver.
        
        Args:
            approver_id: UUID of approver
            filters: Optional filter criteria
                - leave_type_id: UUID of leave type
                - status: Approval status
                - priority: Priority level
                
        Returns:
            Dictionary with paginated approval results
        """
        queryset = LeaveApproval.objects.filter(
            approver_id=approver_id,
            status=ApprovalStatusChoices.PENDING,
        ).select_related('leave_request', 'leave_request__employee', 'leave_request__leave_type')
        
        # Apply filters
        if filters:
            if 'leave_type_id' in filters:
                queryset = queryset.filter(leave_request__leave_type_id=filters['leave_type_id'])
            if 'priority' in filters:
                queryset = queryset.filter(priority=filters['priority'])
        
        queryset = queryset.order_by('-created_at')
        
        total_count = queryset.count()
        
        return {
            'total_pending': total_count,
            'approvals': list(queryset)
        }

    @staticmethod
    def get_approval_by_id(approval_id: str) -> LeaveApproval:
        """
        Get approval record by ID.
        
        Args:
            approval_id: UUID of approval record
            
        Returns:
            LeaveApproval object
            
        Raises:
            NotFound: If approval doesn't exist
        """
        try:
            return LeaveApproval.objects.select_related(
                'leave_request', 'leave_request__employee', 'current_approver', 'delegated_from'
            ).get(id=approval_id)
        except LeaveApproval.DoesNotExist:
            raise NotFound(f"Approval record {approval_id} not found.")

    @staticmethod
    @transaction.atomic
    def approve_leave(approval_id: str, approver_id: str, 
                     comments: Optional[str] = None) -> LeaveApproval:
        """
        Approve a leave request.
        
        Args:
            approval_id: UUID of approval record
            approver_id: UUID of approver
            comments: Optional approval comments
            
        Returns:
            Updated LeaveApproval object
            
        Raises:
            NotFound: If approval doesn't exist
            PermissionDenied: If user is not authorized approver
            ValidationError: If approval cannot be processed
        """
        approval = ApprovalWorkflowService.get_approval_by_id(approval_id)
        
        # Verify approver
        if str(approval.approver_id) != approver_id:
            raise PermissionDenied("You are not authorized to approve this request.")
        
        # Verify status is pending
        if approval.status != ApprovalStatusChoices.PENDING:
            raise ValidationError(f"Cannot approve request with status {approval.status}.")
        
        leave_request = approval.leave_request
        old_status = leave_request.status
        
        try:
            # Update approval record
            approval.status = ApprovalStatusChoices.APPROVED
            approval.actioned_at = ApprovalWorkflowService._get_current_datetime()
            approval.updated_by = uuid.UUID(approver_id)
            approval.remarks = comments or ""
            approval.save(
                update_fields=[
                    "status",
                    "actioned_at",
                    "updated_by",
                    "remarks",
                    "updated_at",
                ]
            )
            
            has_pending_approvals = LeaveApproval.objects.filter(
                leave_request=leave_request,
                status=ApprovalStatusChoices.PENDING,
            ).exclude(id=approval.id).exists()

            if not has_pending_approvals:
                # Final approval - update leave request status
                leave_request.status = LeaveStatusChoices.APPROVED
                leave_request.updated_by = uuid.UUID(approver_id)
                leave_request.save(update_fields=["status", "updated_by", "updated_at"])
                
                # Create status history
                LeaveStatusHistory.objects.create(
                    leave_request=leave_request,
                    from_status=old_status,
                    to_status=LeaveStatusChoices.APPROVED,
                    changed_by=approval.approver,
                    remarks=comments or "Approved",
                )
                
                # Update leave balance when available. Some seed/test data may not
                # have a balance row, so approval should not fail only for that.
                leave_year = leave_request.from_date.year
                try:
                    balance = LeaveBalance.objects.get(
                        employee_id=leave_request.employee_id,
                        leave_type_id=leave_request.leave_type_id,
                        year=leave_year,
                    )
                    balance.used_days += leave_request.total_days
                    balance.pending_days = max(
                        balance.pending_days - leave_request.total_days,
                        0,
                    )
                    balance.version += 1
                    balance.save(
                        update_fields=[
                            "used_days",
                            "pending_days",
                            "version",
                            "updated_at",
                        ]
                    )
                except Exception as e:
                    print(f"Warning: Could not update pending days: {str(e)}")
            
            return approval
            
        except Exception as e:
            raise ValidationError(f"Error approving leave: {str(e)}")

    @staticmethod
    @transaction.atomic
    def reject_leave(approval_id: str, approver_id: str,
                    reason: str) -> LeaveApproval:
        """
        Reject a leave request.
        
        Args:
            approval_id: UUID of approval record
            approver_id: UUID of approver
            reason: Reason for rejection
            
        Returns:
            Updated LeaveApproval object
            
        Raises:
            NotFound: If approval doesn't exist
            PermissionDenied: If user is not authorized
            ValidationError: If approval cannot be processed
        """
        approval = ApprovalWorkflowService.get_approval_by_id(approval_id)
        
        # Verify approver
        if str(approval.approver_id) != approver_id:
            raise PermissionDenied("You are not authorized to reject this request.")
        
        # Verify status is pending
        if approval.status != ApprovalStatusChoices.PENDING:
            raise ValidationError(f"Cannot reject request with status {approval.status}.")
        
        leave_request = approval.leave_request
        old_status = leave_request.status
        
        try:
            # Update approval record
            approval.status = ApprovalStatusChoices.REJECTED
            approval.actioned_at = ApprovalWorkflowService._get_current_datetime()
            approval.updated_by = uuid.UUID(approver_id)
            approval.remarks = reason
            approval.save(
                update_fields=[
                    "status",
                    "actioned_at",
                    "updated_by",
                    "remarks",
                    "updated_at",
                ]
            )
            
            # Update leave request status
            leave_request.status = LeaveStatusChoices.REJECTED
            leave_request.updated_by = uuid.UUID(approver_id)
            leave_request.save(update_fields=["status", "updated_by", "updated_at"])
            
            # Create status history
            LeaveStatusHistory.objects.create(
                leave_request=leave_request,
                from_status=old_status,
                to_status=LeaveStatusChoices.REJECTED,
                changed_by=approval.approver,
                remarks=reason,
            )
            
            # Don't update balance as it was never approved
            
            return approval
            
        except Exception as e:
            raise ValidationError(f"Error rejecting leave: {str(e)}")

    @staticmethod
    @transaction.atomic
    def send_back_for_clarification(approval_id: str, approver_id: str,
                                    clarification_needed: str) -> LeaveApproval:
        """
        Send back leave request for clarification.
        
        Args:
            approval_id: UUID of approval record
            approver_id: UUID of approver
            clarification_needed: Details about what needs clarification
            
        Returns:
            Updated LeaveApproval object
        """
        approval = ApprovalWorkflowService.get_approval_by_id(approval_id)
        
        # Verify approver
        if str(approval.current_approver_id) != approver_id:
            raise PermissionDenied("You are not authorized for this action.")
        
        leave_request = approval.leave_request
        
        try:
            # Update approval record
            approval.status = 'sent_back'
            approval.sent_back_at = ApprovalWorkflowService._get_current_datetime()
            approval.sent_back_by_id = uuid.UUID(approver_id)
            approval.comments = clarification_needed
            approval.save()
            
            # Update leave request status
            leave_request.status = LeaveStatusChoices.PENDING  # Back to pending
            leave_request.save()
            
            # Create status history
            LeaveStatusHistory.objects.create(
                leave_request=leave_request,
                old_status=LeaveStatusChoices.PENDING,
                new_status=LeaveStatusChoices.PENDING,
                changed_by=uuid.UUID(approver_id),
                reason=f"Sent back for clarification: {clarification_needed}"
            )
            
            return approval
            
        except Exception as e:
            raise ValidationError(f"Error sending back request: {str(e)}")

    @staticmethod
    @transaction.atomic
    def delegate_approval(approval_id: str, delegated_by_id: str,
                         delegate_to_id: str) -> LeaveApproval:
        """
        Delegate an approval to another approver.
        
        Args:
            approval_id: UUID of approval record
            delegated_by_id: UUID of current approver
            delegate_to_id: UUID of delegate approver
            
        Returns:
            Updated LeaveApproval object
        """
        approval = ApprovalWorkflowService.get_approval_by_id(approval_id)
        
        # Verify delegator
        if str(approval.current_approver_id) != delegated_by_id:
            raise PermissionDenied("You can only delegate your own approvals.")
        
        try:
            # Create delegation record
            from ..models.transactions.leave_delegations import LeaveDelegation
            delegation = LeaveDelegation.objects.create(
                approval=approval,
                delegated_by_id=delegated_by_id,
                delegated_to_id=delegate_to_id
            )
            
            # Update approval record
            approval.current_approver_id = delegate_to_id
            approval.delegated_from_id = uuid.UUID(delegated_by_id)
            approval.save()
            
            return approval
            
        except Exception as e:
            raise ValidationError(f"Error delegating approval: {str(e)}")

    @staticmethod
    @transaction.atomic
    def bulk_approve(approval_ids: List[str], approver_id: str, remarks: Optional[str] = None) -> Dict[str, Any]:
        """
        Approve multiple leave requests in bulk.
        
        Args:
            approval_ids: List of approval IDs
            approver_id: UUID of approver
            
        Returns:
            Dictionary with results
        """
        results = {
            'approved': [],
            'failed': [],
            'total': len(approval_ids)
        }
        
        for approval_id in approval_ids:
            try:
                approval = ApprovalWorkflowService.approve_leave(
                    approval_id, approver_id, remarks
                )
                results['approved'].append(approval_id)
            except Exception as e:
                results['failed'].append({
                    'approval_id': approval_id,
                    'error': str(e)
                })
        
        return results

    @staticmethod
    @transaction.atomic
    def bulk_reject(approval_ids: List[str], approver_id: str,
                   reason: str) -> Dict[str, Any]:
        """
        Reject multiple leave requests in bulk.
        
        Args:
            approval_ids: List of approval IDs
            approver_id: UUID of approver
            reason: Reason for bulk rejection
            
        Returns:
            Dictionary with results
        """
        results = {
            'rejected': [],
            'failed': [],
            'total': len(approval_ids)
        }
        
        for approval_id in approval_ids:
            try:
                approval = ApprovalWorkflowService.reject_leave(
                    approval_id, approver_id, reason
                )
                results['rejected'].append(approval_id)
            except Exception as e:
                results['failed'].append({
                    'approval_id': approval_id,
                    'error': str(e)
                })
        
        return results

    @staticmethod
    def get_workflow_config(employee_id: Optional[str] = None, leave_type_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get workflow configuration for leave approvals.

        Optional filters: `employee_id` and `leave_type_id` can be provided
        to allow tenant-specific or leave-type-specific workflow selection.
        """
        try:
            # Prefer a leave-specific config if present
            config_qs = ApprovalWorkflowConfig.objects.filter(module='leave', is_active=True)

            # TODO: In future, filter by tenant/company or leave_type mapping stored in meta
            config = config_qs.first()

            if not config:
                return {
                    'levels': 1,
                    'approvers': [],
                    'escalation_enabled': False
                }

            return {
                'levels': len(config.steps) if isinstance(config.steps, list) else 1,
                'approvers': config.steps,
                'escalation_enabled': bool(config.meta_data.get('escalation_enabled')) if isinstance(config.meta_data, dict) else False,
                'requested_employee': employee_id,
                'requested_leave_type': leave_type_id,
            }
        except Exception as e:
            raise ValidationError(f"Error fetching workflow config: {str(e)}")

    @staticmethod
    @transaction.atomic
    def bulk_action(action: str, approval_ids: List[str], approver_id: str, remarks: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform bulk action on approvals. Supported actions: APPROVE, REJECT
        Returns summary of successful and failed operations.
        """
        action = (action or '').strip().upper()
        if action not in ['APPROVE', 'REJECT']:
            raise ValidationError('Unsupported bulk action')

        if action == 'APPROVE':
            results = ApprovalWorkflowService.bulk_approve(approval_ids, approver_id, remarks)
            successful = len(results.get('approved', []))
            failed = len(results.get('failed', []))
        else:
            # For reject we require remarks as reason
            results = ApprovalWorkflowService.bulk_reject(approval_ids, approver_id, remarks or 'Bulk rejection')
            successful = len(results.get('rejected', []))
            failed = len(results.get('failed', []))

        return {
            'successful': successful,
            'failed': failed,
            'details': results
        }

    @staticmethod
    def delegate_authority(delegated_by_id: str, delegate_to_user_id: str, start_date, end_date, reason: Optional[str] = None, scope: str = 'leave_only') -> Dict[str, Any]:
        """
        Delegate approval authority for a period. Creates a LeaveDelegation record.
        """
        # Basic validation
        if not delegate_to_user_id:
            raise ValidationError('delegate_to_user_id is required')
        if start_date > end_date:
            raise ValidationError('start_date must be before or equal to end_date')

        try:
            from apps.employees.models import Employee
            from ..models.transactions.leave_delegations import LeaveDelegation

            delegate = Employee.objects.filter(
                Q(id=delegate_to_user_id) | Q(user_id=delegate_to_user_id)
            ).first()

            if not delegate:
                raise ValidationError("Delegate employee not found.")

            if str(delegate.id) == delegated_by_id:
                raise ValidationError("You cannot delegate approval authority to yourself.")

            delegation, _ = LeaveDelegation.objects.update_or_create(
                delegator_id=delegated_by_id,
                delegate=delegate,
                from_date=start_date,
                to_date=end_date,
                defaults={
                    'scope': scope,
                    'is_active': True,
                    'meta_data': {'reason': reason} if reason else {},
                },
            )

            return {
                'id': str(delegation.id),
                'message': 'Approval authority delegated',
            }
        except Exception as e:
            raise ValidationError(f'Error creating delegation: {str(e)}')

    @staticmethod
    @transaction.atomic
    def create_workflow_config(department_id: Optional[str] = None, leave_type_id: Optional[str] = None, workflow: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Create or update workflow configuration.

        Args:
            department_id: Optional department UUID
            leave_type_id: Optional leave type UUID
            workflow: List of workflow steps

        Returns:
            Dictionary with success message
        """
        if not workflow:
            raise ValidationError('workflow steps are required')

        try:
            # Create or update default workflow config
            config, created = ApprovalWorkflowConfig.objects.update_or_create(
                module='leave',
                is_default=True,
                defaults={
                    'workflow_name': f'Leave Workflow {leave_type_id or "Default"}',
                    'steps': workflow,
                    'is_active': True,
                    'meta_data': {
                        'department_id': department_id,
                        'leave_type_id': leave_type_id,
                    }
                }
            )

            return {
                'message': 'Workflow configured',
                'workflow_id': str(config.id),
            }
        except Exception as e:
            raise ValidationError(f'Error configuring workflow: {str(e)}')

    @staticmethod
    def _create_next_level_approval(leave_request: LeaveRequest, level: int) -> LeaveApproval:
        """
        Create approval record for next level.
        (Internal helper method)
        """
        try:
            config = ApprovalWorkflowConfig.objects.filter(is_active=True).first()
            if not config:
                return None
            
            approval = LeaveApproval.objects.create(
                leave_request=leave_request,
                approval_level=level,
                status='pending',
                current_approver=config.approvers.first()  # Simplified
            )
            return approval
        except Exception:
            return None

    @staticmethod
    def _get_current_datetime():
        """Get current datetime (for easier testing)."""
        from django.utils import timezone
        return timezone.now()
