"""
API Views for Shift Rotation, Weekly Off, and Weekend Override.

Three separate ViewSets following REST conventions.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import FilterSet, CharFilter, DjangoFilterBackend
from datetime import date
from uuid import UUID

from apps.attendance.models import (
    ShiftRotationRule,
    WeeklyOff,
    EmployeeWeekendOverride,
)
from apps.attendance.serializers.employee import (
    ShiftRotationListSerializer,
    ShiftRotationDetailSerializer,
    ShiftRotationCreateSerializer,
    ShiftRotationUpdateSerializer,
    ShiftRotationPreviewSerializer,
    ShiftRotationApplySerializer,
    WeeklyOffListSerializer,
    WeeklyOffDetailSerializer,
    WeeklyOffCreateSerializer,
    WeeklyOffUpdateSerializer,
    WeeklyOffBulkCreateSerializer,
    WeekendOverrideListSerializer,
    WeekendOverrideDetailSerializer,
    WeekendOverrideCreateSerializer,
    WeekendOverrideUpdateSerializer,
    WeekendOverrideBulkCreateSerializer,
    WeekendOverrideFilterSerializer,
)
from apps.attendance.services.employee.rotation_weekly_off_service import (
    ShiftRotationService,
    WeeklyOffService,
    WeekendOverrideService,
)


# ==================== Filters ====================

class ShiftRotationRuleFilter(FilterSet):
    """Filter for shift rotation rules."""
    class Meta:
        model = ShiftRotationRule
        fields = ["is_active", "rotation_type", "priority", "is_default"]


class WeeklyOffFilter(FilterSet):
    """Filter for weekly off."""
    week_day = CharFilter(field_name="week_day")
    
    class Meta:
        model = WeeklyOff
        fields = ["week_day", "is_active"]


# ==================== Shift Rotation ViewSet ====================

class ShiftRotationRuleViewSet(viewsets.ModelViewSet):
    """
    API endpoints for shift rotation rules.
    
    CRUD operations for shift rotation patterns.
    """
    
    queryset = ShiftRotationRule.objects.filter(deleted_at__isnull=True).select_related(
        'company',
        'employee',
        'employee__department',
        'department',
        'location',
        'created_by',
        'updated_by',
    )
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ShiftRotationRuleFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['rotation_type', 'employee__employee_code', 'department__code', 'location__code']
    ordering_fields = ['priority', 'rotation_start_date', 'created_at', 'updated_at']
    ordering = ['-priority', '-created_at']
    
    def get_serializer_class(self):
        """Select appropriate serializer based on action."""
        if self.action == 'list':
            return ShiftRotationListSerializer
        elif self.action == 'retrieve':
            return ShiftRotationDetailSerializer
        elif self.action == 'create':
            return ShiftRotationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ShiftRotationUpdateSerializer
        elif self.action == 'preview':
            return ShiftRotationPreviewSerializer
        elif self.action == 'apply':
            return ShiftRotationApplySerializer
        return ShiftRotationListSerializer
    
    def get_queryset(self):
        """Filter queryset by company and date range."""
        queryset = super().get_queryset()
        
        # Filter by company if available from request context
        if hasattr(self.request.user, 'company_id'):
            queryset = queryset.filter(company_id=self.request.user.company_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create new rotation rule."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        company_id = getattr(request.user, 'company_id', None)
        service = ShiftRotationService(company_id=company_id, user=getattr(request.user, 'employee_profile', None))
        
        success, rule, errors = service.create_rule(serializer.validated_data)
        
        if not success:
            return Response(
                {"detail": "Validation error", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        output_serializer = ShiftRotationDetailSerializer(rule)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update rotation rule (full update)."""
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        company_id = getattr(request.user, 'company_id', None)
        service = ShiftRotationService(company_id=company_id, user=getattr(request.user, 'employee_profile', None))
        
        success, rule, errors = service.update_rule(instance.id, serializer.validated_data)
        
        if not success:
            return Response(
                {"detail": "Update failed", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        output_serializer = ShiftRotationDetailSerializer(rule)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update (PATCH)."""
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete rotation rule (soft delete)."""
        instance = self.get_object()
        
        company_id = getattr(request.user, 'company_id', None)
        service = ShiftRotationService(company_id=company_id, user=getattr(request.user, 'employee_profile', None))
        
        success, errors = service.delete_rule(instance.id)
        
        if not success:
            return Response(
                {"detail": "Delete failed", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Get preview of rotation for a month.
        
        Query params: month (1-12), year
        """
        serializer = ShiftRotationPreviewSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        company_id = getattr(request.user, 'company_id', None)
        service = ShiftRotationService(company_id=company_id)
        
        result = service.get_rotation_preview(
            pk,
            serializer.validated_data['month'],
            serializer.validated_data['year'],
        )
        
        if "error" in result:
            return Response(
                {"detail": result["error"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        return Response(result, status=status.HTTP_200_OK)


# ==================== Weekly Off ViewSet ====================

class WeeklyOffViewSet(viewsets.ModelViewSet):
    """
    API endpoints for weekly off patterns.
    
    CRUD operations for weekly off definitions.
    """
    
    queryset = WeeklyOff.objects.filter(deleted_at__isnull=True).select_related(
        'company',
        'employee',
        'employee__department',
        'department',
        'location',
        'created_by',
        'updated_by',
    )
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = WeeklyOffFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['week_day', 'reason', 'employee__employee_code', 'department__code']
    ordering_fields = ['week_day', 'effective_from', 'created_at']
    ordering = ['week_day', '-effective_from']
    
    def get_serializer_class(self):
        """Select appropriate serializer."""
        if self.action == 'list':
            return WeeklyOffListSerializer
        elif self.action == 'retrieve':
            return WeeklyOffDetailSerializer
        elif self.action == 'create':
            return WeeklyOffCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return WeeklyOffUpdateSerializer
        return WeeklyOffListSerializer
    
    def get_queryset(self):
        """Filter by company."""
        queryset = super().get_queryset()
        
        if hasattr(self.request.user, 'company_id'):
            queryset = queryset.filter(company_id=self.request.user.company_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create new weekly off."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        company_id = getattr(request.user, 'company_id', None)
        service = WeeklyOffService(company_id=company_id, user=getattr(request.user, 'employee_profile', None))
        
        success, weekly_off, errors = service.create_weekly_off(serializer.validated_data)
        
        if not success:
            return Response(
                {"detail": "Validation error", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        output_serializer = WeeklyOffDetailSerializer(weekly_off)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update weekly off."""
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        company_id = getattr(request.user, 'company_id', None)
        service = WeeklyOffService(company_id=company_id, user=getattr(request.user, 'employee_profile', None))
        
        success, weekly_off, errors = service.update_weekly_off(instance.id, serializer.validated_data)
        
        if not success:
            return Response(
                {"detail": "Update failed", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        output_serializer = WeeklyOffDetailSerializer(weekly_off)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update."""
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete weekly off."""
        instance = self.get_object()
        
        company_id = getattr(request.user, 'company_id', None)
        service = WeeklyOffService(company_id=company_id, user=getattr(request.user, 'employee_profile', None))
        
        success, errors = service.delete_weekly_off(instance.id)
        
        if not success:
            return Response(
                {"detail": "Delete failed", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


# ==================== Weekend Override ViewSet ====================

class WeekendOverrideViewSet(viewsets.ModelViewSet):
    """
    API endpoints for weekend overrides.
    
    CRUD operations for employee weekend and weekday overrides.
    """
    
    queryset = EmployeeWeekendOverride.objects.filter(deleted_at__isnull=True).select_related(
        'company',
        'employee',
        'employee__department',
        'shift',
        'created_by',
        'updated_by',
    )
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee_id', 'override_type']
    search_fields = ['employee__employee_code', 'employee__first_name', 'reason']
    ordering_fields = ['override_date', 'created_at']
    ordering = ['-override_date']
    
    def get_serializer_class(self):
        """Select appropriate serializer."""
        if self.action == 'list':
            return WeekendOverrideListSerializer
        elif self.action == 'retrieve':
            return WeekendOverrideDetailSerializer
        elif self.action == 'create':
            return WeekendOverrideCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return WeekendOverrideUpdateSerializer
        return WeekendOverrideListSerializer
    
    def get_queryset(self):
        """Filter by company."""
        queryset = super().get_queryset()
        
        if hasattr(self.request.user, 'company_id'):
            queryset = queryset.filter(company_id=self.request.user.company_id)
        
        # Filter by date range if provided
        override_date_from = self.request.query_params.get('override_date_from')
        override_date_to = self.request.query_params.get('override_date_to')
        
        if override_date_from:
            queryset = queryset.filter(override_date__gte=override_date_from)
        if override_date_to:
            queryset = queryset.filter(override_date__lte=override_date_to)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create new weekend override."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        company_id = getattr(request.user, 'company_id', None)
        service = WeekendOverrideService(company_id=company_id, user=getattr(request.user, 'employee_profile', None))
        
        success, override, errors = service.create_override(serializer.validated_data)
        
        if not success:
            return Response(
                {"detail": "Validation error", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        output_serializer = WeekendOverrideDetailSerializer(override)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update weekend override."""
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        company_id = getattr(request.user, 'company_id', None)
        service = WeekendOverrideService(company_id=company_id, user=getattr(request.user, 'employee_profile', None))
        
        success, override, errors = service.update_override(instance.id, serializer.validated_data)
        
        if not success:
            return Response(
                {"detail": "Update failed", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        output_serializer = WeekendOverrideDetailSerializer(override)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        """Partial update."""
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Delete weekend override."""
        instance = self.get_object()
        
        company_id = getattr(request.user, 'company_id', None)
        service = WeekendOverrideService(company_id=company_id, user=getattr(request.user, 'employee_profile', None))
        
        success, errors = service.delete_override(instance.id)
        
        if not success:
            return Response(
                {"detail": "Delete failed", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)


__all__ = [
    "ShiftRotationRuleViewSet",
    "WeeklyOffViewSet",
    "WeekendOverrideViewSet",
]
