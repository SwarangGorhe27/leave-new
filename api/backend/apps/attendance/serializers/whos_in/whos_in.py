from rest_framework import serializers
from django.utils import timezone
from apps.attendance.models.enums import PunchSource, PunchType, WorkMode
from apps.attendance.utils.employee_relations import employee_team_label

WHO_IS_IN_STATUSES = (
    ("NOT_IN", "Not yet in"),
    ("LATE", "Late arrivals"),
    ("ON_TIME", "On time"),
    ("OUT_OF_OFFICE", "Out of office"),
)

class WhoIsInQuerySerializer(serializers.Serializer):
    date = serializers.DateField(required=True)
    company_id = serializers.UUIDField(required=True)
    shift_id = serializers.UUIDField(required=False)
    department_id = serializers.UUIDField(required=False)
    designation_id = serializers.UUIDField(required=False)
    work_mode_id = serializers.ChoiceField(choices=WorkMode.choices, required=False)
    team_id = serializers.UUIDField(required=False)
    search = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )

class WhoIsInEmployeesQuerySerializer(WhoIsInQuerySerializer):
    status = serializers.ChoiceField(choices=WHO_IS_IN_STATUSES, required=True)
    page = serializers.IntegerField(min_value=1, default=1, required=False)
    limit = serializers.IntegerField(min_value=1, max_value=100, default=20, required=False)

# --- Response Serializers ---

class WhoIsInSummaryDataSerializer(serializers.Serializer):
    not_yet_in = serializers.IntegerField()
    late_arrivals = serializers.IntegerField()
    on_time = serializers.IntegerField()
    out_of_office = serializers.IntegerField()
    total_employees = serializers.IntegerField()

class WhoIsInSummaryResponseSerializer(serializers.Serializer):
    date = serializers.DateField()
    company_id = serializers.UUIDField()
    summary = WhoIsInSummaryDataSerializer()
    last_refreshed = serializers.DateTimeField()

class WhoIsInEmployeeCardSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    employee_code = serializers.CharField(allow_null=True)
    name = serializers.CharField()
    designation = serializers.CharField(allow_null=True)
    department = serializers.CharField(allow_null=True)
    team = serializers.CharField(allow_null=True)
    avatar_initials = serializers.CharField()
    avatar_color = serializers.CharField()
    profile_photo_url = serializers.CharField(allow_null=True)
    login_time = serializers.DateTimeField(allow_null=True)
    shift = serializers.CharField(allow_null=True)
    work_status_code = serializers.CharField(allow_null=True)
    work_status_label = serializers.CharField(allow_null=True)
    work_mode = serializers.CharField(allow_null=True)
    is_late = serializers.BooleanField()
    presence_state = serializers.CharField()

    def to_representation(self, instance):
        """
        Custom mapping to handle both RealtimePresence records and Employee objects.
        """
        if hasattr(instance, 'first_name'):
            employee = instance
            # Try to get the presence record from the context (set by service)
            presence_map = self.context.get('presence_map', {})
            record = presence_map.get(employee.id)
            
            # Do not use employee.realtime_presence — it is OneToOne per employee, not per date.
        else:
            record = instance
            employee = record.employee

        employment = getattr(employee, "employment_details", None)
        full_name = f"{employee.first_name} {employee.last_name}"
        if hasattr(employee, 'full_name'):
             full_name = employee.full_name
        
        initials = "".join([p[0].upper() for p in full_name.split() if p])[:2]

        data = {
            "employee_id": str(employee.id),
            "employee_code": getattr(employee, "employee_code", None),
            "name": full_name,
            "designation": (
                employment.designation.title
                if employment and getattr(employment, "designation", None)
                else None
            ),
            "department": (
                employment.department.name
                if employment and getattr(employment, "department", None)
                else None
            ),
            "team": employee_team_label(employee),
            "avatar_initials": initials,
            "avatar_color": getattr(employee, "avatar_color", "#2563EB"),
            "profile_photo_url": getattr(employee, "profile_picture_url", None),
            "login_time": None,
            "shift": None,
            "work_status_code": None,
            "work_status_label": None,
            "work_mode": None,
            "is_late": False,
            "presence_state": "OUT",
        }

        if record:
            data["login_time"] = record.first_in.isoformat() if record.first_in else None
            data["shift"] = record.shift.name if record.shift else None
            # Handle missing status on RealtimePresence by falling back or adding it
            data["work_status_code"] = getattr(record.status, "code", None) if hasattr(record, 'status') and record.status else None
            data["work_status_label"] = getattr(record.status, "name", None) if hasattr(record, 'status') and record.status else None
            data["work_mode"] = record.work_mode
            data["is_late"] = record.is_late
            data["presence_state"] = record.presence_state

        return data

class WhoIsInEmployeeListResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    date = serializers.DateField()
    total = serializers.IntegerField()
    page = serializers.IntegerField()
    limit = serializers.IntegerField()
    employees = WhoIsInEmployeeCardSerializer(many=True)

class WhoIsInLiveSnapshotResponseSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    date = serializers.DateField()
    last_refreshed = serializers.DateTimeField()
    summary = WhoIsInSummaryDataSerializer()
    employees = serializers.ListField(child=serializers.DictField())

class PunchSessionSerializer(serializers.Serializer):
    punch_time = serializers.DateTimeField()
    punch_type = serializers.CharField()
    punch_source = serializers.CharField()
    location = serializers.CharField()

class EmployeeDailySummaryResponseSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    date = serializers.DateField()
    status = serializers.DictField()
    is_late = serializers.BooleanField()
    grace_applied = serializers.BooleanField()
    first_in = serializers.DateTimeField(allow_null=True)
    last_out = serializers.DateTimeField(allow_null=True)
    work_minutes = serializers.IntegerField()
    overtime_minutes = serializers.IntegerField()
    late_in_minutes = serializers.IntegerField()
    early_exit_minutes = serializers.IntegerField()
    work_mode = serializers.CharField(allow_null=True)
    shift = serializers.DictField(allow_null=True)
    punch_sessions = PunchSessionSerializer(many=True)

    def to_representation(self, instance):
        # instance here is a DailyAttendance record
        data = {
            "employee_id": str(instance.employee_id),
            "date": instance.attendance_date.isoformat(),
            "status": {
                "code": getattr(instance.status, "code", None) if instance.status else None,
                "label": getattr(instance.status, "name", None) if instance.status else None,
            },
            "is_late": bool(instance.is_late),
            "grace_applied": bool(instance.is_grace),
            "first_in": instance.first_in.isoformat() if instance.first_in else None,
            "last_out": instance.last_out.isoformat() if instance.last_out else None,
            "work_minutes": getattr(instance, "actual_work_mins", 0),
            "overtime_minutes": getattr(instance, "ot_mins", 0),
            "late_in_minutes": getattr(instance, "late_in_mins", 0),
            "early_exit_minutes": getattr(instance, "early_exit_mins", 0),
            "work_mode": instance.work_mode,
            "shift": {
                "id": str(instance.shift.id),
                "name": instance.shift.name,
                "start": str(instance.shift.start_time),
                "end": str(instance.shift.end_time),
            } if instance.shift else None,
            "punch_sessions": instance.punch_sessions if hasattr(instance, 'punch_sessions') else []
        }
        return data

# --- Request Serializers ---

class ManualPunchRequestSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    punch_type = serializers.ChoiceField(
        choices=[
            (PunchType.IN, "In"),
            (PunchType.OUT, "Out"),
        ]
    )
    punch_source = serializers.ChoiceField(
        choices=PunchSource.choices,
        default=PunchSource.WEB,
        required=False,
    )
    punch_time = serializers.DateTimeField()
    location_id = serializers.UUIDField(required=False, allow_null=True)
    ip_address = serializers.IPAddressField(required=False, allow_null=True)
    remarks = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    company_id = serializers.UUIDField(required=False)

    def validate_punch_time(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Punch time cannot be in the future.")
        return value
