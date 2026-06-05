import uuid
from django.db import models
from django.http import FileResponse, Http404
from django.utils.dateparse import parse_date
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter

from apps.employees.models.employee import Employee
from apps.employees.models import Company
from apps.employees.models.masters.organization import Department
from apps.attendance.models.requests import AttendanceRequest, RegularizationRequest
from apps.attendance.serializers.admin.requests import (
    EmployeeRequestSerializer,
    AttendanceRequestSerializer,
    AttendanceRequestCreateSerializer,
)
from apps.attendance.services.admin.requests import AttendanceRequestsService
from apps.attendance.services.admin.requests.unified_requests import (
    user_has_company_wide_requests_access,
)
from apps.attendance.services.workflow_engine import WorkflowEngineError

class AttendanceRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = [
        'employee__first_name',
        'employee__last_name',
        'employee__employee_code',
        'reason'
    ]

    def get_queryset(self):
        user = self.request.user
        qs = AttendanceRequestsService.get_requests_queryset(user)

        company_id = self.request.query_params.get("company_id")
        if company_id:
            try:
                uuid.UUID(company_id)
                qs = qs.filter(employee__company_id=company_id)
            except ValueError:
                pass

        # Apply Query Parameter Filters
        request_type = self.request.query_params.get('request_type')
        if request_type:
            qs = qs.filter(request_type=request_type)
            
        department = self.request.query_params.get('department')
        if department:
            try:
                uuid.UUID(department)
                qs = qs.filter(employee__employment_details__department__id=department)
            except ValueError:
                qs = qs.filter(employee__employment_details__department__name__icontains=department)
                
        status_filter = self.request.query_params.get('status')
        if status_filter:
            if status_filter == 'pending':
                qs = qs.filter(manager_status='pending')
            elif status_filter == 'approved':
                qs = qs.filter(manager_status='approved')
            elif status_filter == 'rejected':
                qs = qs.filter(final_status='rejected')
            elif status_filter == 'fully_approved':
                qs = qs.filter(final_status='fully_approved')
                
        manager_status = self.request.query_params.get('manager_status')
        if manager_status:
            qs = qs.filter(manager_status=manager_status)
            
        final_status = self.request.query_params.get('final_status')
        if final_status:
            qs = qs.filter(final_status=final_status)
            
        date_from = self.request.query_params.get('date_from')
        if date_from:
            parsed = parse_date(date_from)
            if parsed:
                qs = qs.filter(date__gte=parsed)
                
        date_to = self.request.query_params.get('date_to')
        if date_to:
            parsed = parse_date(date_to)
            if parsed:
                qs = qs.filter(date__lte=parsed)
                
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return AttendanceRequestCreateSerializer
        return AttendanceRequestSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = AttendanceRequestsService.list_unified_requests(
            request.user,
            request.query_params,
            queryset,
            http_request=request,
        )
        return Response(data, status=status.HTTP_200_OK)

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        pk = self.kwargs[lookup_url_kwarg]

        reg = AttendanceRequestsService.try_resolve_regularization(pk)
        if reg is not None:
            return reg

        queryset = self.filter_queryset(self.get_queryset())
        
        if isinstance(pk, str) and pk.startswith("REQ-"):
            try:
                parsed_pk = int(pk.split("-")[-1])
                obj = queryset.filter(id=parsed_pk).first()
                if obj:
                    return obj
            except ValueError:
                pass
        else:
            try:
                obj = queryset.filter(id=int(pk)).first()
                if obj:
                    return obj
            except ValueError:
                pass
                
        raise Http404("No AttendanceRequest matches the given query.")

    @action(detail=False, methods=['get'])
    def stats(self, request):
        stats_data = AttendanceRequestsService.get_dashboard_stats(
            request.user,
            company_id=request.query_params.get("company_id"),
            query_params=request.query_params,
        )
        return Response(stats_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        obj = self.get_object()
        comment = request.data.get('comment', '')
        stage = request.data.get('stage')
        
        try:
            if isinstance(obj, RegularizationRequest):
                from apps.attendance.services.admin.requests.unified_requests import (
                    regularization_to_request_dict,
                )
                updated = AttendanceRequestsService.approve_regularization(
                    request.user, obj, comment=comment
                )
                return Response(
                    regularization_to_request_dict(updated),
                    status=status.HTTP_200_OK,
                )
            updated_obj = AttendanceRequestsService.approve_request(
                user=request.user,
                request_obj=obj,
                comment=comment,
                stage=stage
            )
            serializer = AttendanceRequestSerializer(updated_obj, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except WorkflowEngineError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        obj = self.get_object()
        comment = request.data.get('comment', '')
        stage = request.data.get('stage')
        
        try:
            if isinstance(obj, RegularizationRequest):
                from apps.attendance.services.admin.requests.unified_requests import (
                    regularization_to_request_dict,
                )
                updated = AttendanceRequestsService.reject_regularization(
                    request.user, obj, comment=comment
                )
                return Response(
                    regularization_to_request_dict(updated),
                    status=status.HTTP_200_OK,
                )
            updated_obj = AttendanceRequestsService.reject_request(
                user=request.user,
                request_obj=obj,
                comment=comment,
                stage=stage
            )
            serializer = AttendanceRequestSerializer(updated_obj, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except WorkflowEngineError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def document(self, request, pk=None):
        obj = self.get_object()
        if not obj.supporting_document:
            return Response({'error': 'No document attached'}, status=status.HTTP_404_NOT_FOUND)
            
        file_handle = obj.supporting_document.open()
        return FileResponse(file_handle, as_attachment=True)


class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeRequestSerializer

    def get_queryset(self):
        user = self.request.user
        employee = getattr(user, 'employee_profile', None)
        if not employee:
            return Employee.objects.none()
            
        qs = Employee.objects.filter(company=employee.company)
        
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(employee_code__icontains=search)
            )
            
        department = self.request.query_params.get('department')
        if department:
            try:
                uuid.UUID(department)
                qs = qs.filter(employment_details__department__id=department)
            except ValueError:
                qs = qs.filter(employment_details__department__name__icontains=department)
                
        return qs

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        val = self.kwargs[lookup_url_kwarg]
        
        obj = queryset.filter(employee_code=val).first()
        if obj:
            return obj
            
        try:
            uuid.UUID(val)
            obj = queryset.filter(id=val).first()
            if obj:
                return obj
        except ValueError:
            pass
            
        raise Http404("No employee matches the given query.")


class DepartmentListView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company_id = request.query_params.get("company_id")
        company = None
        if company_id:
            try:
                company = Company.objects.filter(id=uuid.UUID(company_id)).first()
            except ValueError:
                pass
        if not company:
            employee = getattr(request.user, "employee_profile", None)
            if employee:
                company = employee.company
        if not company and user_has_company_wide_requests_access(request.user):
            company = Company.objects.first()
        if not company:
            return Response([], status=status.HTTP_200_OK)

        depts = Department.objects.filter(company=company)
        data = [{"id": str(d.id), "name": d.name} for d in depts]
        return Response(data, status=status.HTTP_200_OK)


class RequestTypeListView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = [
            {"value": "missing_punch", "label": "Missing Punch Request"},
            {"value": "late_login", "label": "Late Login Justification"},
            {"value": "wfh", "label": "Work From Home Attendance Adjustment"},
            {"value": "half_day", "label": "Half-Day Attendance Correction"},
            {"value": "regularization", "label": "Attendance Regularization"}
        ]
        return Response(data, status=status.HTTP_200_OK)
