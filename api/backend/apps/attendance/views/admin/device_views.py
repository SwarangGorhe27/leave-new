"""
attendance/views/admin/device_views.py

REST API Views for Attendance Device & Swipe Intelligence.

Endpoints:
- GET    /api/v1/devices/                              - List all devices
- POST   /api/v1/devices/                              - Register device
- GET    /api/v1/devices/<device_id>/                  - Device detail
- PATCH  /api/v1/devices/<device_id>/                  - Update device
- DELETE /api/v1/devices/<device_id>/                  - Soft-delete device
- GET    /api/v1/devices/<device_id>/swipe-logs/       - Device swipe logs
- GET    /api/v1/devices/<device_id>/stats/            - Device statistics
- GET    /api/v1/devices/locations/                    - Location list w/ device counts
- GET    /api/v1/devices/locations/<loc_id>/devices/   - Devices at a location

- GET    /api/v1/swipe-logs/sources/                   - Supported source types
- GET    /api/v1/swipe-logs/sync/status/live/          - Live sync status
- POST   /api/v1/swipe-logs/sync/trigger/<device_id>/  - Trigger per-device sync
- GET    /api/v1/swipe-logs/<id>/swipe-intelligence/   - Swipe intelligence for a punch
"""

import logging
from uuid import UUID

from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.attendance.models.device import AttendanceDevice
from apps.attendance.models.enums import DeviceSourceType, DeviceStatus, DeviceSyncStatus
from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.serializers.device_serializers import (
    AttendanceDeviceDetailSerializer,
    AttendanceDeviceSerializer,
    DeviceLocationSummarySerializer,
    DeviceStatsSerializer,
    SwipeIntelligenceSerializer,
)
from apps.attendance.serializers.swipe_logs.swipe_log_serializer import SwipeLogListSerializer
from apps.attendance.services.device_service import DeviceService

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_company_id(request):
    """Return company_id from authenticated user."""
    user = request.user
    if hasattr(user, "employee") and user.employee:
        return user.employee.company_id
    if hasattr(user, "employee_profile") and user.employee_profile:
        return user.employee_profile.company_id
    return None


def _get_employee_id(request):
    """Return employee UUID from authenticated user."""
    user = request.user
    if hasattr(user, "employee") and user.employee:
        return user.employee.id
    if hasattr(user, "employee_profile") and user.employee_profile:
        return user.employee_profile.id
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Device List / Create
# ─────────────────────────────────────────────────────────────────────────────

class DeviceListCreateView(APIView):
    """
    GET  /api/v1/devices/  - List all devices for the authenticated company.
    POST /api/v1/devices/  - Register a new attendance device.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List attendance devices",
        description=(
            "Returns paginated list of attendance devices scoped to the "
            "authenticated user's company. Supports filtering, searching, "
            "and ordering."
        ),
        parameters=[
            OpenApiParameter("search", str, description="Search by name/code/serial"),
            OpenApiParameter("status", str, description="Filter by status (ONLINE/OFFLINE/MAINTENANCE)"),
            OpenApiParameter("source_type", str, description="Filter by source type"),
            OpenApiParameter("location_id", int, description="Filter by location ID"),
            OpenApiParameter("is_active", bool, description="Filter active/inactive devices"),
            OpenApiParameter("ordering", str, description="Field to order by (prefix - for desc)"),
            OpenApiParameter("page", int, description="Page number (default 1)"),
            OpenApiParameter("page_size", int, description="Page size (default 20, max 100)"),
        ],
        responses={200: AttendanceDeviceSerializer(many=True)},
        tags=["Devices"],
    )
    def get(self, request):
        """List all registered attendance devices."""
        company_id = _get_company_id(request)
        if not company_id:
            return Response(
                {"detail": "Company context not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = DeviceService.get_device_queryset(company_id, active_only=False)

        # ── Filtering ──────────────────────────────────────────────
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(device_name__icontains=search)
                | Q(device_code__icontains=search)
                | Q(serial_number__icontains=search)
                | Q(model__icontains=search)
            )

        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter.upper())

        source_type = request.query_params.get("source_type")
        if source_type:
            qs = qs.filter(source_type=source_type.upper())

        location_id = request.query_params.get("location_id")
        if location_id:
            qs = qs.filter(location_id=location_id)

        is_active_str = request.query_params.get("is_active")
        if is_active_str is not None:
            qs = qs.filter(is_active=is_active_str.lower() == "true")

        # ── Ordering ───────────────────────────────────────────────
        ordering = request.query_params.get("ordering", "-created_at")
        allowed_orderings = {
            "device_name", "-device_name",
            "created_at", "-created_at",
            "last_sync_at", "-last_sync_at",
            "status", "-status",
        }
        if ordering not in allowed_orderings:
            ordering = "-created_at"
        qs = qs.order_by(ordering)

        # ── Pagination ─────────────────────────────────────────────
        try:
            page_size = min(int(request.query_params.get("page_size", 20)), 100)
            page_num = int(request.query_params.get("page", 1))
        except (TypeError, ValueError):
            page_size, page_num = 20, 1

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page_num)

        serializer = AttendanceDeviceSerializer(page_obj.object_list, many=True)
        return Response(
            {
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "page": page_num,
                "page_size": page_size,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Register a new attendance device",
        request=AttendanceDeviceSerializer,
        responses={201: AttendanceDeviceSerializer},
        tags=["Devices"],
    )
    def post(self, request):
        """Register a new attendance device for this company."""
        company_id = _get_company_id(request)
        if not company_id:
            return Response(
                {"detail": "Company context not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AttendanceDeviceSerializer(
            data=request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        data.pop("company", None)  # company set by backend

        device = DeviceService.create_device(
            company_id=company_id,
            validated_data=data,
            created_by=_get_employee_id(request),
        )
        return Response(
            AttendanceDeviceSerializer(device).data,
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Device Retrieve / Update / Delete
# ─────────────────────────────────────────────────────────────────────────────

class DeviceDetailView(APIView):
    """
    GET    /api/v1/devices/<device_id>/  - Device detail with health metrics
    PATCH  /api/v1/devices/<device_id>/  - Update device fields
    DELETE /api/v1/devices/<device_id>/  - Soft delete
    """

    permission_classes = [IsAuthenticated]

    def _get_device(self, device_id, company_id):
        try:
            return DeviceService.get_device(UUID(device_id), company_id)
        except (AttendanceDevice.DoesNotExist, ValueError):
            return None

    @extend_schema(
        summary="Get device details",
        responses={200: AttendanceDeviceDetailSerializer},
        tags=["Devices"],
    )
    def get(self, request, device_id):
        company_id = _get_company_id(request)
        if not company_id:
            return Response({"detail": "Company context not found."}, status=status.HTTP_400_BAD_REQUEST)

        device = self._get_device(device_id, company_id)
        if not device:
            return Response({"detail": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AttendanceDeviceDetailSerializer(device)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update device configuration",
        request=AttendanceDeviceSerializer,
        responses={200: AttendanceDeviceSerializer},
        tags=["Devices"],
    )
    def patch(self, request, device_id):
        company_id = _get_company_id(request)
        if not company_id:
            return Response({"detail": "Company context not found."}, status=status.HTTP_400_BAD_REQUEST)

        device = self._get_device(device_id, company_id)
        if not device:
            return Response({"detail": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AttendanceDeviceSerializer(
            device,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        data.pop("company", None)

        updated = DeviceService.update_device(
            device=device,
            validated_data=data,
            updated_by=_get_employee_id(request),
        )
        return Response(AttendanceDeviceSerializer(updated).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Soft-delete a device",
        description=(
            "Marks the device as deleted (soft delete). "
            "Historical swipe logs are preserved."
        ),
        responses={204: OpenApiResponse(description="Device deleted.")},
        tags=["Devices"],
    )
    def delete(self, request, device_id):
        company_id = _get_company_id(request)
        if not company_id:
            return Response({"detail": "Company context not found."}, status=status.HTTP_400_BAD_REQUEST)

        device = self._get_device(device_id, company_id)
        if not device:
            return Response({"detail": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        DeviceService.soft_delete_device(
            device=device,
            deleted_by=_get_employee_id(request),
        )
        return Response(
            {"detail": "Device deleted successfully. Swipe history preserved."},
            status=status.HTTP_204_NO_CONTENT,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Device Swipe Logs
# ─────────────────────────────────────────────────────────────────────────────

class DeviceSwipeLogsView(APIView):
    """
    GET /api/v1/devices/<device_id>/swipe-logs/

    Return paginated swipe logs for a specific device with filters.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get swipe logs for a device",
        parameters=[
            OpenApiParameter("from_date", str, description="From datetime (ISO format)"),
            OpenApiParameter("to_date", str, description="To datetime (ISO format)"),
            OpenApiParameter("employee_id", str, description="Filter by employee UUID"),
            OpenApiParameter("punch_type", str, description="Filter by punch type (IN/OUT/etc)"),
            OpenApiParameter("page", int, description="Page number"),
            OpenApiParameter("page_size", int, description="Page size (max 100)"),
        ],
        responses={200: SwipeLogListSerializer(many=True)},
        tags=["Devices"],
    )
    def get(self, request, device_id):
        company_id = _get_company_id(request)
        if not company_id:
            return Response({"detail": "Company context not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate device
        try:
            device = DeviceService.get_device(UUID(device_id), company_id)
        except (AttendanceDevice.DoesNotExist, ValueError):
            return Response({"detail": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        qs = PunchLog.objects.filter(
            company_id=company_id,
            device=device,
        ).select_related("employee", "device").order_by("-punch_time")

        # ── Filters ────────────────────────────────────────────────
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        employee_id = request.query_params.get("employee_id")
        punch_type = request.query_params.get("punch_type")

        if from_date:
            try:
                from_dt = timezone.datetime.fromisoformat(from_date.replace("Z", "+00:00"))
                qs = qs.filter(punch_time__gte=from_dt)
            except ValueError:
                return Response({"detail": "Invalid from_date format."}, status=status.HTTP_400_BAD_REQUEST)

        if to_date:
            try:
                to_dt = timezone.datetime.fromisoformat(to_date.replace("Z", "+00:00"))
                qs = qs.filter(punch_time__lte=to_dt)
            except ValueError:
                return Response({"detail": "Invalid to_date format."}, status=status.HTTP_400_BAD_REQUEST)

        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        if punch_type:
            qs = qs.filter(punch_type=punch_type.upper())

        # ── Pagination ─────────────────────────────────────────────
        try:
            page_size = min(int(request.query_params.get("page_size", 20)), 100)
            page_num = int(request.query_params.get("page", 1))
        except (TypeError, ValueError):
            page_size, page_num = 20, 1

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page_num)

        serializer = SwipeLogListSerializer(page_obj.object_list, many=True)
        return Response(
            {
                "device": {
                    "id": str(device.id),
                    "device_name": device.device_name,
                    "device_code": device.device_code,
                },
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "page": page_num,
                "page_size": page_size,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Device Statistics
# ─────────────────────────────────────────────────────────────────────────────

class DeviceStatsView(APIView):
    """
    GET /api/v1/devices/<device_id>/stats/

    Return aggregated statistics for a device.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get device statistics",
        responses={200: DeviceStatsSerializer},
        tags=["Devices"],
    )
    def get(self, request, device_id):
        company_id = _get_company_id(request)
        if not company_id:
            return Response({"detail": "Company context not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = DeviceService.get_device(UUID(device_id), company_id)
        except (AttendanceDevice.DoesNotExist, ValueError):
            return Response({"detail": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        stats = DeviceService.get_device_stats(device)
        serializer = DeviceStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# Swipe Sources
# ─────────────────────────────────────────────────────────────────────────────

class SwipeLogSourcesView(APIView):
    """
    GET /api/v1/swipe-logs/sources/

    Return all supported swipe log source types dynamically from enums.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get supported swipe log source types",
        tags=["Swipe Logs"],
    )
    def get(self, request):
        sources = [
            {"value": choice[0], "label": choice[1]}
            for choice in DeviceSourceType.choices
        ]
        return Response(
            {"sources": sources},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Live Sync Status
# ─────────────────────────────────────────────────────────────────────────────

class LiveSyncStatusView(APIView):
    """
    GET /api/v1/swipe-logs/sync/status/live/

    Return real-time sync status across all devices in the company.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get live sync status",
        description=(
            "Returns the current live sync status including active/failed "
            "device counts and running batch info."
        ),
        tags=["Swipe Logs - Sync"],
    )
    def get(self, request):
        company_id = _get_company_id(request)
        if not company_id:
            return Response({"detail": "Company context not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            live_status = DeviceService.get_live_sync_status(company_id)
            return Response(live_status, status=status.HTTP_200_OK)
        except Exception as exc:
            logger.exception(f"Error in live sync status: {exc}")
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─────────────────────────────────────────────────────────────────────────────
# Per-Device Sync Trigger
# ─────────────────────────────────────────────────────────────────────────────

class DeviceSyncTriggerView(APIView):
    """
    POST /api/v1/swipe-logs/sync/trigger/<device_id>/

    Trigger synchronization for a single specific device.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="trigger_device_sync_single",
        summary="Trigger sync for a single device",
        description=(
            "Queues a sync batch for a single device only. "
            "Does not affect global sync execution."
        ),
        responses={202: OpenApiResponse(description="Sync queued.")},
        tags=["Swipe Logs - Sync"],
    )
    def post(self, request, device_id):
        company_id = _get_company_id(request)
        if not company_id:
            return Response({"detail": "Company context not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = DeviceService.get_device(UUID(device_id), company_id)
        except (AttendanceDevice.DoesNotExist, ValueError):
            return Response({"detail": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        if not device.is_active:
            return Response(
                {"detail": "Cannot trigger sync for an inactive device."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = DeviceService.trigger_single_device_sync(
                device=device,
                triggered_by=_get_employee_id(request),
            )
            return Response(result, status=status.HTTP_202_ACCEPTED)
        except Exception as exc:
            logger.exception(f"Error triggering device sync: {exc}")
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─────────────────────────────────────────────────────────────────────────────
# Swipe Intelligence
# ─────────────────────────────────────────────────────────────────────────────

class SwipeIntelligenceView(APIView):
    """
    GET /api/v1/swipe-logs/<id>/swipe-intelligence/

    Return fraud/intelligence analysis for a specific punch log.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get swipe intelligence for a punch log",
        description=(
            "Returns confidence score, anomaly flag, spoof probability, "
            "device trust score, and risk level for a specific swipe/punch log."
        ),
        responses={200: SwipeIntelligenceSerializer},
        tags=["Swipe Logs"],
    )
    def get(self, request, id):
        company_id = _get_company_id(request)
        if not company_id:
            return Response({"detail": "Company context not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            punch_log = PunchLog.objects.select_related("device", "employee").get(
                id=id,
                company_id=company_id,
            )
        except PunchLog.DoesNotExist:
            return Response({"detail": "Swipe log not found."}, status=status.HTTP_404_NOT_FOUND)

        intelligence = DeviceService.get_swipe_intelligence(punch_log)
        serializer = SwipeIntelligenceSerializer(intelligence)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# Device Locations
# ─────────────────────────────────────────────────────────────────────────────

class DeviceLocationListView(APIView):
    """
    GET /api/v1/devices/locations/

    Return all office locations that have at least one device,
    including device count and active device count.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List device locations",
        description="Returns locations with registered device counts.",
        tags=["Devices"],
    )
    def get(self, request):
        company_id = _get_company_id(request)
        if not company_id:
            return Response({"detail": "Company context not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            locations = DeviceService.get_location_device_summary(company_id)
            return Response(
                {"count": len(locations), "results": locations},
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            logger.exception(f"Error getting location device summary: {exc}")
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceLocationDevicesView(APIView):
    """
    GET /api/v1/devices/locations/<location_id>/devices/

    Return all devices installed at a specific office location.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get devices at a location",
        responses={200: AttendanceDeviceSerializer(many=True)},
        tags=["Devices"],
    )
    def get(self, request, location_id):
        company_id = _get_company_id(request)
        if not company_id:
            return Response({"detail": "Company context not found."}, status=status.HTTP_400_BAD_REQUEST)

        qs = DeviceService.get_device_queryset(company_id, active_only=False).filter(
            location_id=location_id,
        )

        serializer = AttendanceDeviceSerializer(qs, many=True)
        return Response(
            {
                "location_id": location_id,
                "count": qs.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
