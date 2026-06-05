from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse, FileResponse
import os

from apps.attendance.serializers.swipe_logs.export_import_serializers import (
    SwipeLogExportRequestSerializer,
    SwipeLogExportJobSerializer,
    SwipeLogImportRequestSerializer,
    SwipeLogScheduledExportSerializer
)
from apps.attendance.services.swipe_logs.export_service import queue_export_job, schedule_auto_export
from apps.attendance.services.swipe_logs.import_service import process_import_job, get_csv_template_content
from apps.attendance.selectors.swipe_logs.export_import_selectors import get_export_job, get_import_job
from apps.attendance.models.swipe_log_import_job import SwipeLogImportJob


class SwipeLogExportView(APIView):
    """
    POST /api/v1/swipe-logs/export
    Async export swipe logs to file.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SwipeLogExportRequestSerializer(data=request.data)
        if serializer.is_valid():
            job = queue_export_job(
                company_id=request.user.employee_profile.company_id,
                employee_id=request.user.employee_profile.id,
                filters=serializer.validated_data
            )
            return Response({
                "job_id": job.id,
                "status": job.status,
                "estimated_secs": 60,
                "message": "Export job queued successfully."
            }, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SwipeLogExportStatusView(APIView):
    """
    GET /api/v1/swipe-logs/export/{job_id}/status
    Poll export job status.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = get_export_job(job_id=job_id, company_id=request.user.employee_profile.company_id)
        if not job:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SwipeLogExportJobSerializer(job)
        return Response(serializer.data)


class SwipeLogExportDownloadView(APIView):
    """
    GET /api/v1/swipe-logs/export/{job_id}/download
    Download completed export file.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = get_export_job(job_id=job_id, company_id=request.user.employee_profile.company_id)
        if not job:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
            
        if job.status != "COMPLETED":
            return Response({"error": "File not ready"}, status=status.HTTP_400_BAD_REQUEST)

        if not job.file_path or not os.path.exists(job.file_path):
            return Response({"error": "Export file missing"}, status=status.HTTP_404_NOT_FOUND)

        file_ext = job.file_path.rsplit(".", 1)[-1].lower()
        content_type = {
            "csv": "text/csv",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "pdf": "application/pdf",
        }.get(file_ext, "application/octet-stream")

        file_handle = open(job.file_path, "rb")
        response = FileResponse(file_handle, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="export_{job.id}.{file_ext}"'
        return response


class SwipeLogImportView(APIView):
    """
    POST /api/v1/swipe-logs/import
    Bulk import punch logs from ESSL device CSV/XLSX.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SwipeLogImportRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                job = process_import_job(
                    company_id=request.user.employee_profile.company_id,
                    employee_id=request.user.employee_profile.id,
                    file_obj=request.FILES['file'],
                    device_id=serializer.validated_data.get('device_id'),
                    import_mode=serializer.validated_data.get('import_mode'),
                    dry_run=serializer.validated_data.get('dry_run')
                )
                return Response({
                    "import_id": job.id,
                    "total_rows": job.total_rows,
                    "accepted": job.accepted,
                    "rejected": job.rejected,
                    "duplicate_detected": job.duplicate_detected,
                    "errors": job.errors
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SwipeLogImportDetailView(APIView):
    """
    GET /api/v1/swipe-logs/import/{import_id}
    Get import job result detail.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, import_id):
        job = get_import_job(import_id=import_id, company_id=request.user.employee_profile.company_id)
        if not job:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            "import_id": job.id,
            "status": job.status,
            "total_rows": job.total_rows,
            "accepted": job.accepted,
            "rejected": job.rejected,
            "created_at": job.created_at,
            "errors": job.errors
        })


class SwipeLogExportTemplateView(APIView):
    """
    GET /api/v1/swipe-logs/export/templates/csv
    Download blank CSV import template.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = get_csv_template_content()
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="import_template.csv"'
        return response


class SwipeLogScheduledExportView(APIView):
    """
    POST /api/v1/swipe-logs/export/scheduled
    Configure scheduled auto-export (daily/weekly/monthly).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SwipeLogScheduledExportSerializer(data=request.data)
        if serializer.is_valid():
            result = schedule_auto_export(
                company_id=request.user.employee_profile.company_id,
                employee_id=request.user.employee_profile.id,
                payload=serializer.validated_data
            )
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
