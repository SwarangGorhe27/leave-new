"""
Other Leave Request Types Service
Handles special leave request types: CompOff, ShortLeave, GatePass, OutDuty, WFH, WeeklyOffShuffle, Overtime
"""
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime, date, timedelta
from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound
from ..models.request_modules.comp_off import CompOffRequest
from ..models.request_modules.short_leave_requests import ShortLeaveRequest
from ..models.request_modules.gate_pass_requests import GatePassRequest
from ..models.request_modules.out_duty_requests import OutDutyRequest
from ..models.request_modules.wfh_requests import WFHRequest
from ..models.request_modules.week_off_shuffle_requests import WeeklyOffShuffleRequest
from ..models.request_modules.overtime_requests import OvertimeRequest
from .base_service import BaseLeaveService


class OtherRequestTypesService(BaseLeaveService):
    """
    Service for managing other leave request types.
    """

    # ========================
    # COMP-OFF SERVICE
    # ========================

    @staticmethod
    def create_compoff_request(employee_id: str, data: Dict[str, Any]) -> CompOffRequest:
        """
        Create a comp-off request.
        
        Args:
            employee_id: UUID of employee
            data: Dictionary containing
                - comp_date (required): Date worked extra hours
                - hours_worked (required): Extra hours worked
                - off_date_requested (optional): Preferred comp-off date
                - reason (optional): Reason
                
        Returns:
            Created CompOffRequest object
        """
        required_fields = ['comp_date', 'hours_worked']
        BaseLeaveService.validate_required_fields(data, required_fields)
        
        try:
            compoff_request = CompOffRequest.objects.create(
                employee_id=employee_id,
                comp_date=data['comp_date'],
                hours_worked=float(data['hours_worked']),
                off_date_requested=data.get('off_date_requested'),
                reason=data.get('reason'),
                status='pending',
                created_by=uuid.UUID(employee_id)
            )
            return compoff_request
        except Exception as e:
            raise ValidationError(f"Error creating comp-off request: {str(e)}")

    @staticmethod
    def get_compoff_balance(employee_id: str) -> Dict[str, Any]:
        """
        Get comp-off balance for employee.
        
        Args:
            employee_id: UUID of employee
            
        Returns:
            Dictionary with balance details
        """
        approved_comps = CompOffRequest.objects.filter(
            employee_id=employee_id,
            status='approved'
        )
        
        total_hours = sum(float(comp.hours_worked) for comp in approved_comps)
        used_hours = sum(float(comp.hours_used or 0) for comp in approved_comps if comp.off_date_taken)
        available_hours = total_hours - used_hours
        
        return {
            'employee_id': employee_id,
            'total_hours_earned': total_hours,
            'hours_used': used_hours,
            'hours_available': available_hours
        }

    @staticmethod
    def approve_compoff_request(request_id: str, approved_by_id: str) -> CompOffRequest:
        """Approve a comp-off request."""
        try:
            request = CompOffRequest.objects.get(id=request_id)
            request.status = 'approved'
            request.approved_at = datetime.now()
            request.approved_by_id = approved_by_id
            request.save()
            return request
        except CompOffRequest.DoesNotExist:
            raise NotFound(f"Comp-off request {request_id} not found.")

    # ========================
    # SHORT LEAVE SERVICE
    # ========================

    @staticmethod
    def create_short_leave_request(employee_id: str, data: Dict[str, Any]) -> ShortLeaveRequest:
        """
        Create a short leave request (early departure/late coming).
        
        Args:
            employee_id: UUID of employee
            data: Dictionary containing
                - leave_date (required): Date of short leave
                - type (required): early_departure, late_coming
                - hours (required): Number of hours
                - reason (optional): Reason
                
        Returns:
            Created ShortLeaveRequest object
        """
        required_fields = ['leave_date', 'type', 'hours']
        BaseLeaveService.validate_required_fields(data, required_fields)
        
        if data['type'] not in ['early_departure', 'late_coming']:
            raise ValidationError({'type': 'Invalid short leave type.'})
        
        try:
            short_leave = ShortLeaveRequest.objects.create(
                employee_id=employee_id,
                leave_date=data['leave_date'],
                type=data['type'],
                hours=float(data['hours']),
                reason=data.get('reason'),
                status='pending',
                created_by=uuid.UUID(employee_id)
            )
            return short_leave
        except Exception as e:
            raise ValidationError(f"Error creating short leave: {str(e)}")

    @staticmethod
    def approve_short_leave(request_id: str, approved_by_id: str) -> ShortLeaveRequest:
        """Approve a short leave request."""
        try:
            request = ShortLeaveRequest.objects.get(id=request_id)
            request.status = 'approved'
            request.approved_at = datetime.now()
            request.approved_by_id = approved_by_id
            request.save()
            return request
        except ShortLeaveRequest.DoesNotExist:
            raise NotFound(f"Short leave request {request_id} not found.")

    # ========================
    # GATE PASS SERVICE
    # ========================

    @staticmethod
    def create_gate_pass_request(employee_id: str, data: Dict[str, Any]) -> GatePassRequest:
        """
        Create a gate pass request (office departure with intent to return).
        
        Args:
            employee_id: UUID of employee
            data: Dictionary containing
                - out_date (required): Date going out
                - out_time (required): Time going out
                - expected_return_time (required): Expected return time
                - reason (required): Reason for going out
                - destination (optional): Where going
                
        Returns:
            Created GatePassRequest object
        """
        required_fields = ['out_date', 'out_time', 'expected_return_time', 'reason']
        BaseLeaveService.validate_required_fields(data, required_fields)
        
        try:
            gate_pass = GatePassRequest.objects.create(
                employee_id=employee_id,
                out_date=data['out_date'],
                out_time=data['out_time'],
                expected_return_time=data['expected_return_time'],
                reason=data['reason'],
                destination=data.get('destination'),
                status='pending',
                created_by=uuid.UUID(employee_id)
            )
            return gate_pass
        except Exception as e:
            raise ValidationError(f"Error creating gate pass: {str(e)}")

    @staticmethod
    def approve_gate_pass(request_id: str, approved_by_id: str) -> GatePassRequest:
        """Approve a gate pass request."""
        try:
            request = GatePassRequest.objects.get(id=request_id)
            request.status = 'approved'
            request.approved_at = datetime.now()
            request.approved_by_id = approved_by_id
            request.save()
            return request
        except GatePassRequest.DoesNotExist:
            raise NotFound(f"Gate pass request {request_id} not found.")

    # ========================
    # OUT DUTY SERVICE
    # ========================

    @staticmethod
    def create_out_duty_request(employee_id: str, data: Dict[str, Any]) -> OutDutyRequest:
        """
        Create an out-of-duty request (official work outside office).
        
        Args:
            employee_id: UUID of employee
            data: Dictionary containing
                - out_date (required): Start date
                - return_date (required): Return date
                - location (required): Location for duty
                - purpose (required): Purpose of duty
                - contact_number (optional): Contact during duty
                
        Returns:
            Created OutDutyRequest object
        """
        required_fields = ['out_date', 'return_date', 'location', 'purpose']
        BaseLeaveService.validate_required_fields(data, required_fields)
        
        BaseLeaveService.validate_date_range(data['out_date'], data['return_date'], allow_same_day=True)
        
        try:
            out_duty = OutDutyRequest.objects.create(
                employee_id=employee_id,
                out_date=data['out_date'],
                return_date=data['return_date'],
                location=data['location'],
                purpose=data['purpose'],
                contact_number=data.get('contact_number'),
                status='pending',
                created_by=uuid.UUID(employee_id)
            )
            return out_duty
        except Exception as e:
            raise ValidationError(f"Error creating out-duty request: {str(e)}")

    @staticmethod
    def approve_out_duty(request_id: str, approved_by_id: str) -> OutDutyRequest:
        """Approve an out-duty request."""
        try:
            request = OutDutyRequest.objects.get(id=request_id)
            request.status = 'approved'
            request.approved_at = datetime.now()
            request.approved_by_id = approved_by_id
            request.save()
            return request
        except OutDutyRequest.DoesNotExist:
            raise NotFound(f"Out-duty request {request_id} not found.")

    # ========================
    # WFH (WORK FROM HOME) SERVICE
    # ========================

    @staticmethod
    def create_wfh_request(employee_id: str, data: Dict[str, Any]) -> WFHRequest:
        """
        Create a WFH (Work From Home) request.
        
        Args:
            employee_id: UUID of employee
            data: Dictionary containing
                - wfh_date (required): Date for WFH
                - reason (optional): Reason for WFH
                
        Returns:
            Created WFHRequest object
        """
        required_fields = ['wfh_date']
        BaseLeaveService.validate_required_fields(data, required_fields)
        
        try:
            wfh = WFHRequest.objects.create(
                employee_id=employee_id,
                wfh_date=data['wfh_date'],
                reason=data.get('reason'),
                status='pending',
                created_by=uuid.UUID(employee_id)
            )
            return wfh
        except Exception as e:
            raise ValidationError(f"Error creating WFH request: {str(e)}")

    @staticmethod
    def approve_wfh(request_id: str, approved_by_id: str) -> WFHRequest:
        """Approve a WFH request."""
        try:
            request = WFHRequest.objects.get(id=request_id)
            request.status = 'approved'
            request.approved_at = datetime.now()
            request.approved_by_id = approved_by_id
            request.save()
            return request
        except WFHRequest.DoesNotExist:
            raise NotFound(f"WFH request {request_id} not found.")

    # ========================
    # WEEKLY OFF SHUFFLE SERVICE
    # ========================

    @staticmethod
    def create_weekly_off_shuffle(employee_id: str, data: Dict[str, Any]) -> WeeklyOffShuffleRequest:
        """
        Create a weekly off shuffle request.
        
        Args:
            employee_id: UUID of employee
            data: Dictionary containing
                - from_date (required): Period start
                - to_date (required): Period end
                - requested_off_day (required): Requested day off
                - alternative_working_day (required): Day to work instead
                - reason (optional): Reason
                
        Returns:
            Created WeeklyOffShuffleRequest object
        """
        required_fields = ['from_date', 'to_date', 'requested_off_day', 'alternative_working_day']
        BaseLeaveService.validate_required_fields(data, required_fields)
        
        try:
            shuffle = WeeklyOffShuffleRequest.objects.create(
                employee_id=employee_id,
                from_date=data['from_date'],
                to_date=data['to_date'],
                requested_off_day=data['requested_off_day'],
                alternative_working_day=data['alternative_working_day'],
                reason=data.get('reason'),
                status='pending',
                created_by=uuid.UUID(employee_id)
            )
            return shuffle
        except Exception as e:
            raise ValidationError(f"Error creating weekly off shuffle: {str(e)}")

    @staticmethod
    def approve_weekly_off_shuffle(request_id: str, approved_by_id: str) -> WeeklyOffShuffleRequest:
        """Approve a weekly off shuffle request."""
        try:
            request = WeeklyOffShuffleRequest.objects.get(id=request_id)
            request.status = 'approved'
            request.approved_at = datetime.now()
            request.approved_by_id = approved_by_id
            request.save()
            return request
        except WeeklyOffShuffleRequest.DoesNotExist:
            raise NotFound(f"Weekly off shuffle request {request_id} not found.")

    # ========================
    # OVERTIME SERVICE
    # ========================

    @staticmethod
    def create_overtime_request(employee_id: str, data: Dict[str, Any]) -> OvertimeRequest:
        """
        Create an overtime request.
        
        Args:
            employee_id: UUID of employee
            data: Dictionary containing
                - overtime_date (required): Date of overtime
                - hours_required (required): Hours of overtime
                - reason (required): Reason for overtime
                - project_code (optional): Project code
                
        Returns:
            Created OvertimeRequest object
        """
        required_fields = ['overtime_date', 'hours_required', 'reason']
        BaseLeaveService.validate_required_fields(data, required_fields)
        
        if float(data['hours_required']) <= 0:
            raise ValidationError({'hours_required': 'Hours must be greater than zero.'})
        
        try:
            overtime = OvertimeRequest.objects.create(
                employee_id=employee_id,
                overtime_date=data['overtime_date'],
                hours_required=float(data['hours_required']),
                reason=data['reason'],
                project_code=data.get('project_code'),
                status='pending',
                created_by=uuid.UUID(employee_id)
            )
            return overtime
        except Exception as e:
            raise ValidationError(f"Error creating overtime request: {str(e)}")

    @staticmethod
    def approve_overtime(request_id: str, approved_by_id: str) -> OvertimeRequest:
        """Approve an overtime request."""
        try:
            request = OvertimeRequest.objects.get(id=request_id)
            request.status = 'approved'
            request.approved_at = datetime.now()
            request.approved_by_id = approved_by_id
            request.save()
            return request
        except OvertimeRequest.DoesNotExist:
            raise NotFound(f"Overtime request {request_id} not found.")
