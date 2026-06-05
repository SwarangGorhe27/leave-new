from rest_framework import serializers
from apps.employees.models.employee import Employee
from apps.attendance.models.requests import AttendanceRequest, ApprovalWorkflow

class EmployeeRequestSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='employee_code')
    name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'name', 'department', 'designation']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_department(self, obj):
        details = getattr(obj, 'employment_details', None)
        if details and details.department:
            return details.department.name
        return ""

    def get_designation(self, obj):
        details = getattr(obj, 'employment_details', None)
        if details and details.designation:
            return details.designation.title
        return ""


class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    approver = EmployeeRequestSerializer(read_only=True)
    actioned_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)

    class Meta:
        model = ApprovalWorkflow
        fields = ['id', 'approver', 'stage', 'status', 'comment', 'actioned_at']


class AttendanceRequestSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    employee = EmployeeRequestSerializer(read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    attendance = serializers.SerializerMethodField()
    supporting_document_url = serializers.SerializerMethodField()
    approval_workflow = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", read_only=True)

    class Meta:
        model = AttendanceRequest
        fields = [
            'id', 'employee', 'request_type', 'request_type_display', 'date', 
            'attendance', 'supporting_document_url', 'approval_workflow', 
            'manager_status', 'final_status', 'created_at', 'reason'
        ]

    def get_id(self, obj):
        return f"REQ-{obj.id:03d}"

    def get_attendance(self, obj):
        return {
            'date': obj.date.strftime("%Y-%m-%d") if obj.date else None,
            'shift_time': obj.shift_time or "",
            'punch_in': obj.punch_in.strftime("%I:%M %p") if obj.punch_in else "--",
            'punch_out': obj.punch_out.strftime("%I:%M %p") if obj.punch_out else "--",
            'working_hours': obj.working_hours or ""
        }

    def get_supporting_document_url(self, obj):
        if obj.supporting_document:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/api/v1/attendance/requests/{obj.id}/document/")
            return f"/api/v1/attendance/requests/{obj.id}/document/"
        return None

    def get_approval_workflow(self, obj):
        stages = obj.approval_workflow.all().order_by('actioned_at')
        return ApprovalWorkflowSerializer(stages, many=True, context=self.context).data


class AttendanceRequestCreateSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(required=False, write_only=True)
    date = serializers.DateField(required=True)
    reason = serializers.CharField(required=True)
    request_type = serializers.CharField(required=True)
    punch_in = serializers.TimeField(required=False, allow_null=True)
    punch_out = serializers.TimeField(required=False, allow_null=True)

    class Meta:
        model = AttendanceRequest
        fields = [
            'employee_id', 'request_type', 'date', 'shift_time', 
            'punch_in', 'punch_out', 'working_hours', 'reason', 
            'supporting_document'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        from apps.attendance.services.admin.requests import AttendanceRequestsService
        return AttendanceRequestsService.create_request(request.user, validated_data)
