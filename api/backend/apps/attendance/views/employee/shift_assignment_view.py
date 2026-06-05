"""Views for single shift assignment CRUD operations."""

import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.attendance.models import EmployeeShiftRoster
from apps.attendance.serializers.employee.shift_assignment_serializer import (
    ShiftAssignmentListSerializer,
    ShiftAssignmentDetailSerializer,
    ShiftAssignmentCreateSerializer,
    ShiftAssignmentUpdateSerializer,
    ShiftAssignmentBulkReadSerializer,
    ShiftAssignmentFilterSerializer,
)
from apps.attendance.services.employee.shift_assignment_service import (
    ShiftAssignmentService,
)

logger = logging.getLogger(__name__)


class ShiftAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for single shift assignment CRUD operations.
    
    Endpoints:
    - GET /api/v1/shift-assignments - List assignments
    - POST /api/v1/shift-assignments - Create assignment
    - GET /api/v1/shift-assignments/{id} - Retrieve assignment
    - PUT /api/v1/shift-assignments/{id} - Update assignment (full replacement)
    - PATCH /api/v1/shift-assignments/{id} - Partial update
    - DELETE /api/v1/shift-assignments/{id} - Delete assignment
    - GET /api/v1/shift-assignments/filters - Get filter options
    """

    queryset = EmployeeShiftRoster.objects.filter(deleted_at__isnull=True)
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee_id', 'shift_id', 'cycle_id', 'is_week_off']
    search_fields = [
        'employee__employee_code',
        'employee__first_name',
        'employee__last_name',
        'shift__code',
    ]
    ordering_fields = ['roster_date', 'created_at', 'updated_at']
    ordering = ['-roster_date']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ShiftAssignmentListSerializer
        elif self.action == 'retrieve':
            return ShiftAssignmentDetailSerializer
        elif self.action == 'create':
            return ShiftAssignmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ShiftAssignmentUpdateSerializer
        return ShiftAssignmentListSerializer

    def get_queryset(self):
        """Optimize queryset with select_related and prefetch_related."""
        queryset = super().get_queryset().select_related(
            'employee',
            'employee__company',
            'employee__department',
            'shift',
            'cycle',
            'company',
        )

        # Apply date range filter if provided
        roster_date_from = self.request.query_params.get('roster_date_from')
        roster_date_to = self.request.query_params.get('roster_date_to')

        if roster_date_from:
            queryset = queryset.filter(roster_date__gte=roster_date_from)
        if roster_date_to:
            queryset = queryset.filter(roster_date__lte=roster_date_to)

        # Filter by company if in user context
        if hasattr(self.request.user, 'company_id'):
            queryset = queryset.filter(company_id=self.request.user.company_id)

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new shift assignment."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Use service to create assignment with business logic
        service = ShiftAssignmentService(
            company_id=getattr(request.user, 'company_id', None),
            user=request.user,
        )

        success, assignment, errors = service.create_assignment(
            employee_id=serializer.validated_data['employee_id'],
            shift_id=serializer.validated_data['shift_id'],
            roster_date=serializer.validated_data['roster_date'],
            cycle_id=serializer.validated_data['cycle_id'],
            is_week_off=serializer.validated_data.get('is_week_off', False),
            override_reason=serializer.validated_data.get('override_reason'),
        )

        if not success:
            return Response(
                {
                    "detail": "Failed to create shift assignment.",
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = ShiftAssignmentDetailSerializer(assignment)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """Update (full replacement) a shift assignment."""
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Use service to update assignment
        service = ShiftAssignmentService(
            company_id=getattr(request.user, 'company_id', None),
            user=request.user,
        )

        success, assignment, errors = service.update_assignment(
            assignment_id=instance.id,
            shift_id=serializer.validated_data.get('shift_id'),
            roster_date=serializer.validated_data.get('roster_date'),
            is_week_off=serializer.validated_data.get('is_week_off'),
            override_reason=serializer.validated_data.get('override_reason'),
        )

        if not success:
            return Response(
                {
                    "detail": "Failed to update shift assignment.",
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = ShiftAssignmentDetailSerializer(assignment)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """Partial update a shift assignment (PATCH)."""
        instance = self.get_object()

        # Use service to update assignment
        service = ShiftAssignmentService(
            company_id=getattr(request.user, 'company_id', None),
            user=request.user,
        )

        success, assignment, errors = service.update_assignment(
            assignment_id=instance.id,
            shift_id=request.data.get('shift_id'),
            roster_date=request.data.get('roster_date'),
            is_week_off=request.data.get('is_week_off'),
            override_reason=request.data.get('override_reason'),
        )

        if not success:
            return Response(
                {
                    "detail": "Failed to update shift assignment.",
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = ShiftAssignmentDetailSerializer(assignment)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Soft delete a shift assignment."""
        instance = self.get_object()

        # Use service to delete assignment
        service = ShiftAssignmentService(
            company_id=getattr(request.user, 'company_id', None),
            user=request.user,
        )

        success, errors = service.delete_assignment(instance.id)

        if not success:
            return Response(
                {
                    "detail": "Failed to delete shift assignment.",
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Shift assignment deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def filters(self, request):
        """
        Get available filter options for shift assignments.
        
        GET /api/v1/shift-assignments/filters
        """
        serializer = ShiftAssignmentFilterSerializer({})
        return Response(
            {
                "status": "success",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def details(self, request, pk=None):
        """
        Get detailed information for a shift assignment.
        
        GET /api/v1/shift-assignments/{id}/details
        """
        assignment = self.get_object()
        serializer = ShiftAssignmentDetailSerializer(assignment)
        return Response(
            {
                "status": "success",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def bulk_read(self, request):
        """
        List assignments with advanced filtering and pagination.
        
        POST /api/v1/shift-assignments/bulk_read
        """
        serializer = ShiftAssignmentBulkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Use service to list with filters
        service = ShiftAssignmentService(
            company_id=getattr(request.user, 'company_id', None),
            user=request.user,
        )

        success, assignments, errors = service.list_assignments(
            employee_id=serializer.validated_data.get('employee_id'),
            shift_id=serializer.validated_data.get('shift_id'),
            cycle_id=serializer.validated_data.get('cycle_id'),
            roster_date_from=serializer.validated_data.get('roster_date_from'),
            roster_date_to=serializer.validated_data.get('roster_date_to'),
            is_week_off=serializer.validated_data.get('is_week_off'),
            department_id=serializer.validated_data.get('department_id'),
            company_id=serializer.validated_data.get('company_id'),
            search=serializer.validated_data.get('search'),
        )

        if not success:
            return Response(
                {
                    "detail": "Failed to retrieve assignments.",
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = ShiftAssignmentListSerializer(assignments, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
