"""
Views for Shift Swap Workflow Operations.

Endpoints:
- POST /api/attendance/shift-swap/{id}/accept/ - Accept by target
- POST /api/attendance/shift-swap/{id}/approve/ - Approve by manager
- POST /api/attendance/shift-swap/{id}/reject/ - Reject by manager
- POST /api/attendance/shift-swap/{id}/cancel/ - Cancel by requester
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from uuid import UUID

from apps.attendance.models import EmpShiftSwapRequest
from apps.attendance.serializers.employee import (
    ShiftSwapAcceptSerializer,
    ShiftSwapApproveSerializer,
    ShiftSwapRejectSerializer,
    ShiftSwapCancelSerializer,
    ShiftSwapWorkflowResponseSerializer,
)
from apps.attendance.services.shift_swap_workflow_service import (
    ShiftSwapWorkflowService,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_shift_swap(request, pk):
    """Accept shift swap by target employee."""
    try:
        swap_id = UUID(pk)
        company_id = UUID(request.headers.get("X-Company-ID", ""))
        user_employee_id = getattr(request.user, "id", None)

        if not user_employee_id:
            return Response(
                {"error": "Unable to determine current employee"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get swap to validate
        swap = EmpShiftSwapRequest.objects.get(
            id=swap_id, company_id=company_id, deleted_at__isnull=True
        )

        # Validate request data
        serializer = ShiftSwapAcceptSerializer(
            data=request.data, context={"swap_request": swap}
        )
        serializer.is_valid(raise_exception=True)

        # Process acceptance
        response = ShiftSwapWorkflowService.accept_swap(
            swap_id=swap_id,
            company_id=company_id,
            accepted_by_employee_id=user_employee_id,
            note=serializer.validated_data.get("note"),
        )

        # Return updated swap details
        updated_swap = EmpShiftSwapRequest.objects.get(id=swap_id)
        return Response(
            {
                "status": "success",
                "message": response.message,
                "data": ShiftSwapWorkflowResponseSerializer(updated_swap).data,
            },
            status=status.HTTP_200_OK,
        )

    except EmpShiftSwapRequest.DoesNotExist:
        return Response(
            {"error": "Shift swap not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ValueError as e:
        return Response(
            {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to accept swap: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_shift_swap(request, pk):
    """Approve shift swap by manager/HR."""
    try:
        swap_id = UUID(pk)
        company_id = UUID(request.headers.get("X-Company-ID", ""))
        user_employee_id = getattr(request.user, "id", None)

        if not user_employee_id:
            return Response(
                {"error": "Unable to determine current employee"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get swap to validate
        swap = EmpShiftSwapRequest.objects.get(
            id=swap_id, company_id=company_id, deleted_at__isnull=True
        )

        # Validate request data
        serializer = ShiftSwapApproveSerializer(
            data=request.data, context={"swap_request": swap}
        )
        serializer.is_valid(raise_exception=True)

        # Process approval
        response = ShiftSwapWorkflowService.approve_swap(
            swap_id=swap_id,
            company_id=company_id,
            approved_by_employee_id=serializer.validated_data["approved_by"].id,
            note=serializer.validated_data.get("approval_note"),
        )

        # Return updated swap details
        updated_swap = EmpShiftSwapRequest.objects.get(id=swap_id)
        return Response(
            {
                "status": "success",
                "message": response.message,
                "data": ShiftSwapWorkflowResponseSerializer(updated_swap).data,
            },
            status=status.HTTP_200_OK,
        )

    except EmpShiftSwapRequest.DoesNotExist:
        return Response(
            {"error": "Shift swap not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ValueError as e:
        return Response(
            {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to approve swap: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_shift_swap(request, pk):
    """Reject shift swap by manager/HR."""
    try:
        swap_id = UUID(pk)
        company_id = UUID(request.headers.get("X-Company-ID", ""))
        user_employee_id = getattr(request.user, "id", None)

        if not user_employee_id:
            return Response(
                {"error": "Unable to determine current employee"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get swap to validate
        swap = EmpShiftSwapRequest.objects.get(
            id=swap_id, company_id=company_id, deleted_at__isnull=True
        )

        # Validate request data
        serializer = ShiftSwapRejectSerializer(
            data=request.data, context={"swap_request": swap}
        )
        serializer.is_valid(raise_exception=True)

        # Process rejection
        response = ShiftSwapWorkflowService.reject_swap(
            swap_id=swap_id,
            company_id=company_id,
            rejected_by_employee_id=serializer.validated_data["rejected_by"].id,
            note=serializer.validated_data.get("rejection_note"),
        )

        # Return updated swap details
        updated_swap = EmpShiftSwapRequest.objects.get(id=swap_id)
        return Response(
            {
                "status": "success",
                "message": response.message,
                "data": ShiftSwapWorkflowResponseSerializer(updated_swap).data,
            },
            status=status.HTTP_200_OK,
        )

    except EmpShiftSwapRequest.DoesNotExist:
        return Response(
            {"error": "Shift swap not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ValueError as e:
        return Response(
            {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to reject swap: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_shift_swap(request, pk):
    """Cancel shift swap by requester."""
    try:
        swap_id = UUID(pk)
        company_id = UUID(request.headers.get("X-Company-ID", ""))
        user_employee_id = getattr(request.user, "id", None)

        if not user_employee_id:
            return Response(
                {"error": "Unable to determine current employee"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get swap to validate
        swap = EmpShiftSwapRequest.objects.get(
            id=swap_id, company_id=company_id, deleted_at__isnull=True
        )

        # Validate request data
        serializer = ShiftSwapCancelSerializer(
            data=request.data, context={"swap_request": swap}
        )
        serializer.is_valid(raise_exception=True)

        # Process cancellation
        response = ShiftSwapWorkflowService.cancel_swap(
            swap_id=swap_id,
            company_id=company_id,
            cancelled_by_employee_id=user_employee_id,
            note=serializer.validated_data.get("note"),
        )

        # Return updated swap details
        updated_swap = EmpShiftSwapRequest.objects.get(id=swap_id)
        return Response(
            {
                "status": "success",
                "message": response.message,
                "data": ShiftSwapWorkflowResponseSerializer(updated_swap).data,
            },
            status=status.HTTP_200_OK,
        )

    except EmpShiftSwapRequest.DoesNotExist:
        return Response(
            {"error": "Shift swap not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except ValueError as e:
        return Response(
            {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to cancel swap: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
