"""
ViewSet for Shift Swap Request CRUD Operations.

Endpoints:
- POST /api/attendance/shift-swap/ - Create swap request
- GET /api/attendance/shift-swap/ - List swap requests
- GET /api/attendance/shift-swap/{id}/ - Get swap details
- PATCH /api/attendance/shift-swap/{id}/ - Update swap (pending only)
- DELETE /api/attendance/shift-swap/{id}/ - Cancel swap
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from uuid import UUID
from datetime import date

from apps.attendance.models import EmpShiftSwapRequest, ShiftSwapStatus
from apps.attendance.serializers.employee import (
    ShiftSwapListSerializer,
    ShiftSwapDetailSerializer,
    ShiftSwapCreateSerializer,
    ShiftSwapUpdateSerializer,
)
from apps.attendance.services.shift_swap_service import ShiftSwapService


class ShiftSwapViewSet(viewsets.ModelViewSet):
    """ViewSet for shift swap request operations."""

    queryset = EmpShiftSwapRequest.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "status",
        "requester_id",
        "target_id",
        "swap_date",
    ]
    search_fields = [
        "requester__employee_code",
        "requester__first_name",
        "target__employee_code",
        "target__first_name",
    ]
    ordering_fields = ["swap_date", "created_at", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return ShiftSwapListSerializer
        elif self.action == "retrieve":
            return ShiftSwapDetailSerializer
        elif self.action == "create":
            return ShiftSwapCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ShiftSwapUpdateSerializer
        return ShiftSwapDetailSerializer

    def get_queryset(self):
        """Filter by company from X-Tenant-Schema header."""
        queryset = super().get_queryset()
        company_id = self.request.headers.get("X-Company-ID")
        if company_id:
            try:
                queryset = queryset.filter(company_id=UUID(company_id))
            except (ValueError, TypeError):
                pass
        return queryset.select_related(
            "requester",
            "target",
            "requester_shift",
            "target_shift",
            "approved_by",
            "rejected_by",
        )

    def create(self, request, *args, **kwargs):
        """Create a new shift swap request."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Get current user's employee ID (from request user object or JWT)
            user_employee_id = getattr(request.user, "id", None)
            if not user_employee_id:
                return Response(
                    {"error": "Unable to determine current employee"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            swap_data = ShiftSwapService.create_swap_request(
                request_data=serializer.validated_data,
                requester_user_id=user_employee_id,
            )

            response_serializer = ShiftSwapDetailSerializer(
                EmpShiftSwapRequest.objects.get(id=swap_data.id)
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to create swap: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        """Get shift swap details."""
        try:
            company_id = request.headers.get("X-Company-ID")
            swap_id = kwargs.get("pk")

            swap_data = ShiftSwapService.get_swap_detail(
                swap_id=UUID(swap_id),
                company_id=UUID(company_id),
            )

            return Response(swap_data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        """List shift swap requests with filtering."""
        try:
            company_id = request.headers.get("X-Company-ID")
            requester_id = request.query_params.get("requester_id")
            target_id = request.query_params.get("target_id")
            status_filter = request.query_params.get("status")
            date_from = request.query_params.get("date_from")
            date_to = request.query_params.get("date_to")

            swaps = ShiftSwapService.get_swap_requests(
                company_id=UUID(company_id),
                requester_id=UUID(requester_id) if requester_id else None,
                target_id=UUID(target_id) if target_id else None,
                status=status_filter,
                date_from=date_from,
                date_to=date_to,
            )

            return Response(swaps, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def partial_update(self, request, *args, **kwargs):
        """Update swap request (pending requests only)."""
        try:
            swap_id = UUID(kwargs.get("pk"))
            company_id = UUID(request.headers.get("X-Company-ID"))
            user_employee_id = getattr(request.user, "id", None)

            swap = EmpShiftSwapRequest.objects.get(
                id=swap_id, company_id=company_id, deleted_at__isnull=True
            )

            if swap.status != ShiftSwapStatus.PENDING_APPROVAL:
                return Response(
                    {"error": "Can only update pending requests"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(swap, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            # Update reason if provided
            if "reason" in request.data:
                swap.reason = request.data["reason"]
                swap.updated_by_id = user_employee_id
                swap.save(update_fields=["reason", "updated_by_id", "updated_at"])

            return Response(ShiftSwapDetailSerializer(swap).data)

        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except EmpShiftSwapRequest.DoesNotExist:
            return Response(
                {"error": "Shift swap not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        """Soft delete (cancel) a shift swap request."""
        try:
            swap_id = UUID(kwargs.get("pk"))
            company_id = UUID(request.headers.get("X-Company-ID"))
            user_employee_id = getattr(request.user, "id", None)

            ShiftSwapService.delete_swap_request(
                swap_id=swap_id,
                company_id=company_id,
                user_id=user_employee_id,
            )

            return Response(status=status.HTTP_204_NO_CONTENT)

        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
