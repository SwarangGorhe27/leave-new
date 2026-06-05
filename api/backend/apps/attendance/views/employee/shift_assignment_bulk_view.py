"""Views for bulk shift assignment operations."""

import logging
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.attendance.serializers.employee.shift_assignment_bulk_serializer import (
    BulkAssignmentCreateSerializer,
    BulkAssignmentValidationSerializer,
    BulkAssignmentValidationResultSerializer,
    BulkAssignmentJobStatusSerializer,
)
from apps.attendance.services.employee.shift_assignment_bulk_service import (
    BulkShiftAssignmentService,
)

logger = logging.getLogger(__name__)


class BulkShiftAssignmentCreateView(APIView):
    """
    Create bulk shift assignments.
    
    Supports multiple assignment types and async processing.
    
    Endpoints:
    - POST /api/v1/shift-assignments/bulk - Create bulk assignment job
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Create a bulk shift assignment job.
        
        Request body:
        {
            "assignment_type": "date_range",  # single_date, date_range, recurring
            "cycle_id": "uuid",
            "company_id": "uuid (optional)",
            "date_from": "2024-01-01",
            "date_to": "2024-01-31",
            "recurring_days": [0, 1, 2, 3, 4],  # for recurring type
            "assignments": [
                {"employee_id": "uuid", "shift_id": "uuid", "is_week_off": false},
                ...
            ],
            "skip_duplicates": true,
            "skip_overlapping": true,
            "skip_inactive_employees": true,
            "async_mode": true,
            "notify_employees": false
        }
        """
        serializer = BulkAssignmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Use service to create bulk job
        service = BulkShiftAssignmentService(
            company_id=getattr(request.user, 'company_id', None),
            user=request.user,
        )

        success, job, errors = service.create_bulk_job(
            cycle_id=serializer.validated_data['cycle_id'],
            assignments=serializer.validated_data['assignments'],
            assignment_type=serializer.validated_data.get('assignment_type', 'single_date'),
            date_from=serializer.validated_data.get('date_from'),
            date_to=serializer.validated_data.get('date_to'),
            recurring_days=serializer.validated_data.get('recurring_days'),
            skip_duplicates=serializer.validated_data.get('skip_duplicates', True),
            skip_overlapping=serializer.validated_data.get('skip_overlapping', True),
            skip_inactive=serializer.validated_data.get('skip_inactive_employees', True),
            notify_employees=serializer.validated_data.get('notify_employees', False),
        )

        if not success:
            return Response(
                {
                    "detail": "Failed to create bulk assignment job.",
                    "errors": errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if async_mode is requested
        async_mode = serializer.validated_data.get('async_mode', True)

        if not async_mode:
            # Process synchronously (for testing/small batches)
            success, summary, processed_items = service.process_bulk_assignment(job.id)

            if success:
                return Response(
                    {
                        "status": "completed",
                        "job_id": str(job.id),
                        "summary": {
                            "total_items": summary.total_items,
                            "successful_count": summary.successful_count,
                            "failed_count": summary.failed_count,
                            "skipped_count": summary.skipped_count,
                            "success_rate": summary.success_rate,
                        },
                        "processed_items": [
                            {
                                "index": item.index,
                                "employee_id": str(item.employee_id),
                                "shift_id": str(item.shift_id),
                                "success": item.success,
                                "assignment_id": str(item.assignment_id) if item.assignment_id else None,
                                "error": item.error,
                            }
                            for item in processed_items
                        ],
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "detail": "Failed to process bulk assignment.",
                        "job_id": str(job.id),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # Return job ID for async processing
            return Response(
                {
                    "status": "pending",
                    "job_id": str(job.id),
                    "message": "Bulk assignment job created and queued for processing.",
                },
                status=status.HTTP_202_ACCEPTED,
            )


class BulkShiftAssignmentValidateView(APIView):
    """
    Validate bulk shift assignments before actual processing.
    
    Endpoints:
    - POST /api/v1/shift-assignments/bulk/validate - Validate bulk data
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Pre-validate bulk assignment data.
        
        Request body:
        {
            "cycle_id": "uuid",
            "company_id": "uuid (optional)",
            "date_from": "2024-01-01",
            "date_to": "2024-01-31",
            "assignments": [...],
            "check_duplicates": true,
            "check_overlapping": true,
            "check_inactive": true
        }
        """
        serializer = BulkAssignmentValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Use service to validate
        service = BulkShiftAssignmentService(
            company_id=getattr(request.user, 'company_id', None),
            user=request.user,
        )

        can_proceed, validation_result = service.validate_bulk_assignment(
            cycle_id=serializer.validated_data['cycle_id'],
            date_from=serializer.validated_data['date_from'],
            date_to=serializer.validated_data['date_to'],
            assignments=serializer.validated_data['assignments'],
            check_duplicates=serializer.validated_data.get('check_duplicates', True),
            check_overlapping=serializer.validated_data.get('check_overlapping', True),
            check_inactive=serializer.validated_data.get('check_inactive', True),
        )

        return Response(
            {
                "can_proceed": can_proceed,
                "total_items": validation_result.get("total_items", 0),
                "valid_count": validation_result.get("valid_count", 0),
                "invalid_count": validation_result.get("invalid_count", 0),
                "duplicate_count": validation_result.get("duplicate_count", 0),
                "inactive_count": validation_result.get("inactive_count", 0),
                "warnings": validation_result.get("warnings", []),
                "errors": validation_result.get("errors", []),
                "invalid_items": validation_result.get("invalid_items", [])[:10],  # Show first 10
            },
            status=status.HTTP_200_OK,
        )


class BulkShiftAssignmentStatusView(APIView):
    """
    Check status of bulk shift assignment job.
    
    Endpoints:
    - GET /api/v1/shift-assignments/bulk/{job_id}/status - Get job status
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, job_id):
        """
        Get status of a bulk assignment job.
        
        Returns job progress, item counts, and current status.
        """
        service = BulkShiftAssignmentService(
            company_id=getattr(request.user, 'company_id', None),
            user=request.user,
        )

        success, job_status, errors = service.get_job_status(job_id)

        if not success:
            return Response(
                {
                    "detail": "Failed to get job status.",
                    "errors": errors,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "status": "success",
                "data": job_status,
            },
            status=status.HTTP_200_OK,
        )


class BulkShiftAssignmentRetryView(APIView):
    """
    Retry a failed bulk shift assignment job.
    
    Endpoints:
    - POST /api/v1/shift-assignments/bulk/{job_id}/retry - Retry job
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        """
        Retry a failed bulk assignment job.
        """
        service = BulkShiftAssignmentService(
            company_id=getattr(request.user, 'company_id', None),
            user=request.user,
        )

        # Get job and check status
        success, job_status, errors = service.get_job_status(job_id)

        if not success:
            return Response(
                {
                    "detail": "Job not found.",
                    "errors": errors,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if job_status['status'] != 'FAILED':
            return Response(
                {
                    "detail": f"Cannot retry job with status '{job_status['status']}'.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reset and reprocess
        success, summary, processed_items = service.process_bulk_assignment(job_id)

        if success:
            return Response(
                {
                    "status": "success",
                    "message": "Job reprocessed successfully.",
                    "job_id": str(job_id),
                    "summary": {
                        "total_items": summary.total_items,
                        "successful_count": summary.successful_count,
                        "failed_count": summary.failed_count,
                        "skipped_count": summary.skipped_count,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "detail": "Failed to reprocess job.",
                    "job_id": str(job_id),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
