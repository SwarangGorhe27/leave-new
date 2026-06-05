"""
Leave Reports & Analytics Service
Handles report generation and analytics for leave data.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db.models import Count, Sum, Q, F
from rest_framework.exceptions import ValidationError
from ..models.transactions.leave_requests import LeaveRequest, LeaveStatusChoices
from ..models.transactions.leave_balances import LeaveBalance
from ..models.masters.leave_types import LeaveType
from .base_service import BaseLeaveService
from .leave_balance_service import LeaveBalanceService


class LeaveReportService(BaseLeaveService):
    """
    Service for generating leave reports and analytics.
    
    Reports:
    - Leave summary report
    - Team availability report
    - Leave encashment report
    - Approval turnaround time report
    - Leave patterns analytics
    """

    @staticmethod
    def get_leave_summary_report(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate leave summary report.
        
        Args:
            filters: Optional filters
                - start_date: Report start date
                - end_date: Report end date
                - employee_id: Specific employee
                - leave_type_id: Specific leave type
                - department_id: Specific department
                
        Returns:
            Dictionary with summary report data
        """
        queryset = LeaveRequest.objects.filter(deleted_at__isnull=True)
        
        # Apply filters
        if filters:
            if 'start_date' in filters:
                queryset = queryset.filter(from_date__gte=filters['start_date'])
            if 'end_date' in filters:
                queryset = queryset.filter(to_date__lte=filters['end_date'])
            if 'employee_id' in filters:
                queryset = queryset.filter(employee_id=filters['employee_id'])
            if 'leave_type_id' in filters:
                queryset = queryset.filter(leave_type_id=filters['leave_type_id'])
        
        # Aggregate statistics
        total_requests = queryset.count()
        
        summary = {
            'report_type': 'leave_summary',
            'generated_at': datetime.now().isoformat(),
            'filters': filters or {},
            'total_requests': total_requests,
            'by_status': {},
            'by_leave_type': {},
            'by_employee': {},
            'statistics': {}
        }
        
        # By status
        for status in LeaveStatusChoices.choices:
            count = queryset.filter(status=status[0]).count()
            total_days = queryset.filter(status=status[0]).aggregate(
                total=Sum('total_days')
            )['total'] or Decimal('0')
            summary['by_status'][status[1]] = {
                'count': count,
                'total_days': float(total_days)
            }
        
        # By leave type
        by_type = queryset.values('leave_type__name').annotate(
            count=Count('id'),
            total_days=Sum('total_days')
        )
        for item in by_type:
            summary['by_leave_type'][item['leave_type__name']] = {
                'count': item['count'],
                'total_days': float(item['total_days'] or 0)
            }
        
        # Statistics
        summary['statistics'] = {
            'average_duration': float(
                queryset.aggregate(avg=Sum('total_days') / Count('id'))['avg'] or 0
            ),
            'approval_rate': LeaveReportService._calculate_approval_rate(queryset),
            'rejection_rate': LeaveReportService._calculate_rejection_rate(queryset)
        }
        
        return summary

    @staticmethod
    def get_team_availability_report(department_id: str, 
                                    start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Generate team availability report showing who's on leave during date range.
        
        Args:
            department_id: Department UUID
            start_date: Report period start
            end_date: Report period end
            
        Returns:
            Dictionary with availability data
        """
        # Get all approved leaves in date range
        leaves = LeaveRequest.objects.filter(
            status=LeaveStatusChoices.APPROVED,
            from_date__lte=end_date,
            to_date__gte=start_date,
            deleted_at__isnull=True
        ).select_related('employee', 'leave_type')
        
        report = {
            'report_type': 'team_availability',
            'department_id': department_id,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_working_days': LeaveReportService._count_working_days(start_date, end_date),
            'on_leave': [],
            'availability_summary': {}
        }
        
        # Group by employee
        leaves_by_employee = {}
        for leave in leaves:
            emp_id = str(leave.employee_id)
            if emp_id not in leaves_by_employee:
                leaves_by_employee[emp_id] = {
                    'employee_name': str(leave.employee),
                    'leaves': []
                }
            leaves_by_employee[emp_id]['leaves'].append({
                'leave_type': leave.leave_type.name,
                'from_date': leave.from_date.isoformat(),
                'to_date': leave.to_date.isoformat(),
                'duration': float(leave.total_days)
            })
        
        report['on_leave'] = list(leaves_by_employee.values())
        report['availability_summary'] = {
            'employees_on_leave': len(leaves_by_employee),
            'total_person_days_lost': float(
                leaves.aggregate(total=Sum('total_days'))['total'] or 0
            )
        }
        
        return report

    @staticmethod
    def get_leave_encashment_report(employee_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate leave encashment report.
        
        Args:
            employee_id: Optional - specific employee (None for all)
            
        Returns:
            Dictionary with encashment data
        """
        from ..models.transactions.leave_encashment_requests import LeaveEncashmentRequest
        
        queryset = LeaveEncashmentRequest.objects.all()
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        report = {
            'report_type': 'leave_encashment',
            'generated_at': datetime.now().isoformat(),
            'total_encashments': queryset.count(),
            'total_amount': float(
                queryset.aggregate(total=Sum('amount'))['total'] or 0
            ),
            'by_leave_type': {},
            'pending': 0,
            'approved': 0,
            'rejected': 0,
            'details': []
        }
        
        # By leave type
        by_type = queryset.values('leave_type__name').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        for item in by_type:
            report['by_leave_type'][item['leave_type__name']] = {
                'count': item['count'],
                'total_amount': float(item['total_amount'] or 0)
            }
        
        # Status breakdown
        report['pending'] = queryset.filter(status='pending').count()
        report['approved'] = queryset.filter(status='approved').count()
        report['rejected'] = queryset.filter(status='rejected').count()
        
        # Details
        for encashment in queryset[:100]:  # Limit to 100 for performance
            report['details'].append({
                'employee_id': str(encashment.employee_id),
                'leave_type': encashment.leave_type.name,
                'days_encashed': float(encashment.days_encashed),
                'amount': float(encashment.amount),
                'status': encashment.status,
                'requested_date': encashment.created_at.isoformat()
            })
        
        return report

    @staticmethod
    def get_approval_tat_report(start_date: Optional[date] = None,
                               end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Generate approval turnaround time (TAT) report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Dictionary with TAT analysis
        """
        from ..models.transactions.leave_approvals import LeaveApproval
        
        queryset = LeaveApproval.objects.filter(
            status__in=['approved', 'rejected']
        ).select_related('leave_request')
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        # Calculate TAT
        tats = []
        for approval in queryset:
            if approval.approved_at:
                tat = (approval.approved_at - approval.created_at).days
                tats.append(tat)
            elif approval.rejected_at:
                tat = (approval.rejected_at - approval.created_at).days
                tats.append(tat)
        
        report = {
            'report_type': 'approval_tat',
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
            'total_approvals': len(tats),
            'average_tat_days': round(sum(tats) / len(tats), 2) if tats else 0,
            'min_tat_days': min(tats) if tats else 0,
            'max_tat_days': max(tats) if tats else 0,
            'approvals_within_3_days': len([t for t in tats if t <= 3]),
            'approvals_within_7_days': len([t for t in tats if t <= 7])
        }
        
        return report

    @staticmethod
    def get_leave_patterns(employee_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get leave pattern analytics.
        
        Args:
            employee_id: Optional specific employee
            
        Returns:
            Dictionary with pattern analysis
        """
        queryset = LeaveRequest.objects.filter(
            status=LeaveStatusChoices.APPROVED,
            deleted_at__isnull=True
        )
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # By day of week
        patterns = {
            'report_type': 'leave_patterns',
            'generated_at': datetime.now().isoformat(),
            'by_day_of_week': {},
            'by_month': {},
            'by_leave_type': {}
        }
        
        # Day of week analysis
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, day in enumerate(days):
            count = sum(1 for leave in queryset if leave.from_date.weekday() == i)
            patterns['by_day_of_week'][day] = count
        
        # Monthly analysis
        for leave in queryset:
            month = leave.from_date.strftime('%Y-%m')
            patterns['by_month'][month] = patterns['by_month'].get(month, 0) + 1
        
        # By leave type
        by_type = queryset.values('leave_type__name').annotate(count=Count('id'))
        for item in by_type:
            patterns['by_leave_type'][item['leave_type__name']] = item['count']
        
        return patterns

    @staticmethod
    def _calculate_approval_rate(queryset) -> float:
        """Calculate approval rate percentage."""
        total = queryset.count()
        if total == 0:
            return 0.0
        approved = queryset.filter(status=LeaveStatusChoices.APPROVED).count()
        return round((approved / total) * 100, 2)

    @staticmethod
    def _calculate_rejection_rate(queryset) -> float:
        """Calculate rejection rate percentage."""
        total = queryset.count()
        if total == 0:
            return 0.0
        rejected = queryset.filter(status=LeaveStatusChoices.REJECTED).count()
        return round((rejected / total) * 100, 2)

    @staticmethod
    def _count_working_days(start_date: date, end_date: date) -> int:
        """Count working days (Mon-Fri) in date range."""
        count = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:  # 0-4 are weekdays
                count += 1
            current += timedelta(days=1)
        return count
