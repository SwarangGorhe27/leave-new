# apps/attendance/services/admin/whos_in/who_is_in_service.py

import logging
import re
from datetime import date
from django.db import transaction
from django.utils import timezone
from django.db.models import Q

from apps.attendance.utils.company_access import assert_company_access

from .exceptions import InvalidFilterError
from .types import WhoIsInFilters

logger = logging.getLogger(__name__)


class WhoIsInService:
    """
    Service layer for the Who's In dashboard.
    Handles business logic for summary counts, employee listings, and manual punches.
    """

    MAX_SEARCH_LENGTH = 100
    MAX_LIMIT = 100

    SEARCH_PATTERN = re.compile(r"^[a-zA-Z0-9\s._-]*$")

    def __init__(self, user, filters: WhoIsInFilters):
        self.user = user
        self.filters = filters

        self._validate_access()
        self._validate_filters()

    def _validate_access(self):
        """Ensure user can access the requested company (strict or dev HR/admin)."""
        logger.debug(
            "who_is_in_access_check user=%s requested_company=%s",
            getattr(self.user, "id", None),
            self.filters.company_id,
        )
        assert_company_access(
            self.user,
            self.filters.company_id,
            endpoint="who-is-in",
        )

    def _team_department_id(self):
        if not self.filters.team_id:
            return None
        from apps.employees.models.masters.organization import Team

        team = Team.objects.filter(
            id=self.filters.team_id,
            company_id=self.filters.company_id,
            is_active=True,
        ).first()
        return team.department_id if team else None

    def _apply_employee_list_filters(self, qs):
        if self.filters.search:
            search_term = self.filters.search.strip()
            qs = qs.filter(
                Q(first_name__icontains=search_term)
                | Q(last_name__icontains=search_term)
                | Q(employee_code__icontains=search_term)
            )
        if self.filters.department_id:
            qs = qs.filter(employment_details__department_id=self.filters.department_id)
        if self.filters.designation_id:
            qs = qs.filter(employment_details__designation_id=self.filters.designation_id)
        team_department_id = self._team_department_id()
        if team_department_id:
            qs = qs.filter(employment_details__department_id=team_department_id)
        return qs

    def _validate_filters(self):
        """Validate incoming filters."""
        if not isinstance(self.filters.attendance_date, date):
            raise InvalidFilterError("attendance_date must be a valid date object.")

        if self.filters.search:
            search = self.filters.search.strip()
            if len(search) > self.MAX_SEARCH_LENGTH:
                raise InvalidFilterError(f"search cannot exceed {self.MAX_SEARCH_LENGTH} characters.")
            if not self.SEARCH_PATTERN.fullmatch(search):
                raise InvalidFilterError("search contains invalid characters.")

    def _get_base_queryset(self):
        """
        Build common filtered queryset for RealtimePresence.
        """
        from apps.attendance.models import RealtimePresence

        from apps.attendance.utils.employee_relations import defer_employment_team

        qs = defer_employment_team(
            RealtimePresence.objects.select_related(
                "employee",
                "employee__employment_details",
                "employee__employment_details__department",
                "employee__employment_details__designation",
                "shift",
            ).filter(
                company_id=self.filters.company_id,
                attendance_date=self.filters.attendance_date,
            )
        )

        if self.filters.shift_id:
            qs = qs.filter(shift_id=self.filters.shift_id)

        if self.filters.department_id:
            qs = qs.filter(employee__employment_details__department_id=self.filters.department_id)

        if self.filters.work_mode_id:
            qs = qs.filter(work_mode=self.filters.work_mode_id)

        if self.filters.designation_id:
            qs = qs.filter(employee__employment_details__designation_id=self.filters.designation_id)

        team_department_id = self._team_department_id()
        if team_department_id:
            qs = qs.filter(
                employee__employment_details__department_id=team_department_id
            )

        if self.filters.search:
            search_term = self.filters.search.strip()
            qs = qs.filter(
                Q(employee__first_name__icontains=search_term) |
                Q(employee__last_name__icontains=search_term) |
                Q(employee__employee_code__icontains=search_term)
            )

        return qs

    def get_summary(self):
        """Return counts for dashboard summary tiles."""
        from apps.attendance.models.enums import WorkMode
        from apps.leave.models.transactions.leave_requests import LeaveRequestDay, LeaveStatusChoices
        from apps.employees.models import Employee

        base_qs = self._get_base_queryset()

        # 1. In-Office (WFO) counts
        # LATE: is_late = TRUE and presence_state = IN and work_mode = OFFICE
        late_arrivals = base_qs.filter(
            presence_state="IN", 
            is_late=True,
            work_mode=WorkMode.OFFICE
        ).count()
        
        # ON_TIME: is_late = FALSE and presence_state = IN and work_mode = OFFICE
        on_time = base_qs.filter(
            presence_state="IN", 
            is_late=False,
            work_mode=WorkMode.OFFICE
        ).count()
        
        # 2. Out-of-Office (WFH/Remote or Leave or Punched Out)
        # WFH/Remote people who are IN
        wfh_in_count = base_qs.filter(
            presence_state="IN",
            work_mode__in=[WorkMode.REMOTE, WorkMode.CLIENT_SITE]
        ).count()

        # People who punched in then out
        out_with_punch = base_qs.filter(
            presence_state="OUT", 
            first_in__isnull=False
        ).count()

        # Approved Leaves
        on_leave_count = LeaveRequestDay.objects.filter(
            leave_date=self.filters.attendance_date,
            leave_request__status=LeaveStatusChoices.APPROVED,
            leave_request__employee__company_id=self.filters.company_id
        ).values('leave_request__employee_id').distinct().count()

        out_of_office_count = wfh_in_count + out_with_punch + on_leave_count

        # 3. Total active employees
        total_employees = Employee.objects.filter(
            company_id=self.filters.company_id, 
            is_active=True
        ).count()

        # 4. Not Yet In
        # Not Yet In = Total - (Late + OnTime) - (Out of Office)
        in_office_count = late_arrivals + on_time
        not_yet_in_count = max(0, total_employees - in_office_count - out_of_office_count)

        return {
            "date": self.filters.attendance_date,
            "company_id": self.filters.company_id,
            "summary": {
                "not_yet_in": not_yet_in_count,
                "late_arrivals": late_arrivals,
                "on_time": on_time,
                "out_of_office": out_of_office_count,
                "total_employees": total_employees,
            },
            "last_refreshed": timezone.now(),
        }

    def get_employees(self, status: str, page: int = 1, limit: int = 20):
        """Return paginated employee cards based on status."""
        from apps.attendance.models import RealtimePresence
        from apps.employees.models import Employee
        from apps.leave.models.transactions.leave_requests import LeaveRequestDay, LeaveStatusChoices
        from apps.attendance.models.enums import WorkMode

        # 1. Helper to get base employee IDs for different statuses
        
        # Approved Leaves
        on_leave_ids = LeaveRequestDay.objects.filter(
            leave_date=self.filters.attendance_date,
            leave_request__status=LeaveStatusChoices.APPROVED,
            leave_request__employee__company_id=self.filters.company_id
        ).values_list('leave_request__employee_id', flat=True)

        # Realtime Presence records for today
        punched_qs = RealtimePresence.objects.filter(
            company_id=self.filters.company_id,
            attendance_date=self.filters.attendance_date
        )

        if status == "LATE":
            # LATE: is_late = TRUE and presence_state = IN and work_mode = OFFICE
            qs = self._get_base_queryset().filter(
                presence_state="IN", 
                is_late=True,
                work_mode=WorkMode.OFFICE
            )
        
        elif status == "ON_TIME":
            # ON_TIME: is_late = FALSE and presence_state = IN and work_mode = OFFICE
            qs = self._get_base_queryset().filter(
                presence_state="IN", 
                is_late=False,
                work_mode=WorkMode.OFFICE
            )
        
        elif status == "OUT_OF_OFFICE":
            # OUT_OF_OFFICE: Approved leave OR WFH/Remote (IN) OR Punched OUT
            wfh_in_ids = punched_qs.filter(
                presence_state="IN",
                work_mode__in=[WorkMode.REMOTE, WorkMode.CLIENT_SITE]
            ).values_list('employee_id', flat=True)

            punched_out_ids = punched_qs.filter(
                presence_state="OUT", 
                first_in__isnull=False
            ).values_list('employee_id', flat=True)
            
            target_ids = set(on_leave_ids) | set(wfh_in_ids) | set(punched_out_ids)
            
            qs = Employee.objects.filter(
                id__in=target_ids,
                company_id=self.filters.company_id,
                is_active=True
            )
            from apps.attendance.utils.employee_relations import with_employee_org

            qs = with_employee_org(qs)
            qs = self._apply_employee_list_filters(qs)

        elif status == "NOT_IN":
            # NOT_IN: No punch today; not on leave
            # We exclude everyone who is either IN (WFO/WFH) or OUT (Punched Out) or ON LEAVE
            all_involved_ids = set(on_leave_ids) | set(punched_qs.values_list('employee_id', flat=True))
            
            qs = Employee.objects.filter(
                company_id=self.filters.company_id,
                is_active=True
            ).exclude(
                id__in=all_involved_ids
            )
            from apps.attendance.utils.employee_relations import with_employee_org

            qs = with_employee_org(qs)
            qs = self._apply_employee_list_filters(qs)
        else:
            raise InvalidFilterError("Invalid status value.")

        total = qs.count()
        offset = (page - 1) * limit
        records = qs[offset : offset + limit]

        # For records that came from Employee queryset, we need to attach RealtimePresence if it exists
        # so the serializer can show login_time etc.
        presence_map = {}
        if status in ["NOT_IN", "OUT_OF_OFFICE"] and records:
            presence_map = {
                rp.employee_id: rp
                for rp in RealtimePresence.objects.filter(
                    employee_id__in=[r.id for r in records],
                    attendance_date=self.filters.attendance_date,
                ).select_related("shift")
            }

        return {
            "status": status,
            "date": self.filters.attendance_date,
            "total": total,
            "page": page,
            "limit": limit,
            "employees": records,
            "presence_map": presence_map,
        }

    def get_live_snapshot(self):
        """Return full dashboard snapshot for polling or SSE."""
        summary = self.get_summary()
        base_qs = self._get_base_queryset()
        return {
            "company_id": self.filters.company_id,
            "date": self.filters.attendance_date,
            "last_refreshed": summary["last_refreshed"],
            "summary": summary["summary"],
            "employees": list(base_qs), # Serializer will handle this
        }

    def get_employee_daily_summary(self, employee_id, date_obj):
        """Return detailed attendance for one employee on a specific day."""
        from apps.attendance.models import DailyAttendance, PunchLog

        record = DailyAttendance.objects.filter(
            employee_id=employee_id, 
            attendance_date=date_obj
        ).select_related('employee', 'shift', 'status').first()

        if not record:
            raise InvalidFilterError("Daily attendance record not found.")

        punches = PunchLog.objects.filter(
            employee_id=employee_id,
            punch_time__date=date_obj
        ).order_by('punch_time')

        punches = PunchLog.objects.filter(
            employee_id=employee_id,
            punch_time__date=date_obj
        ).order_by('punch_time')

        record.punch_sessions = [
            {
                "punch_time": p.punch_time,
                "punch_type": p.punch_type,
                "punch_source": p.punch_source,
                "location": "N/A" 
            } for p in punches
        ]
        return record

    @transaction.atomic
    def create_manual_punch(self, payload: dict):
        """Create a manual punch and update realtime presence."""
        from apps.attendance.models import PunchLog, DailyAttendance, RealtimePresence
        from apps.employees.models import Employee

        employee_id = payload.get("employee_id")
        punch_type = payload.get("punch_type")
        punch_time = payload.get("punch_time")
        punch_source = payload.get("punch_source", "WEB")

        employee = Employee.objects.get(id=employee_id)
        
        # 1. Create Punch Log
        punch = PunchLog.objects.create(
            company_id=employee.company_id,
            employee=employee,
            punch_type=punch_type,
            punch_source=punch_source,
            punch_time=punch_time,
            location_id=payload.get("location_id"),
            ip_address=payload.get("ip_address"),
            remarks=payload.get("remarks"),
            created_by=self.user
        )

        # 2. Upsert Realtime Presence
        attendance_date = punch_time.date()
        presence, created = RealtimePresence.objects.get_or_create(
            employee=employee,
            attendance_date=attendance_date,
            defaults={'company_id': employee.company_id}
        )
        
        presence.last_punch_time = punch_time
        presence.last_punch_type = punch_type
        presence.presence_state = "IN" if punch_type == "IN" else "OUT"
        
        if punch_type == "IN" and not presence.first_in:
            presence.first_in = punch_time
            # logic for is_late would go here based on shift
        
        presence.save()

        # 3. Update Daily Attendance (basic sync)
        daily, _ = DailyAttendance.objects.get_or_create(
            employee=employee,
            attendance_date=attendance_date,
            defaults={'company_id': employee.company_id}
        )
        if punch_type == "IN" and not daily.first_in:
            daily.first_in = punch_time
        elif punch_type == "OUT":
            daily.last_out = punch_time
        
        daily.is_currently_in = (presence.presence_state == "IN")
        daily.last_punch_time = punch_time
        daily.last_punch_type = punch_type
        daily.save()

        return {
            "punch_log_id": str(punch.id),
            "employee_id": str(employee_id),
            "punch_type": punch_type,
            "punch_time": punch_time.isoformat(),
            "punch_source": punch_source,
            "is_late": presence.is_late,
            "daily_attendance_updated": True,
            "realtime_presence_upserted": True
        }
