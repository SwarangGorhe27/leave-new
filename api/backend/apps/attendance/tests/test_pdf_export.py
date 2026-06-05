"""
Test for PDF generation using xhtml2pdf and pymupdf in SwipeLogExportService.
"""
import os
from django.test import TestCase
from django.utils import timezone
from apps.attendance.models import SwipeLogExportJob
from apps.attendance.services.swipe_logs.swipe_log_export_service import SwipeLogExportService
import fitz  # PyMuPDF

class PDFExportTest(TestCase):
    def setUp(self):
        # Create a dummy export job
        self.export_job = SwipeLogExportJob.objects.create(
            company_id=1,
            from_date=timezone.now().date(),
            to_date=timezone.now().date(),
            employee_ids=[],
            department_ids=[],
            device_ids=[],
            include_verification_details=True,
            include_geofence_details=True,
            total_records=1
        )
        self.service = SwipeLogExportService()

    def test_pdf_generation(self):
        pdf_bytes = self.service.export_to_pdf(self.export_job.id)
        self.assertIsInstance(pdf_bytes, bytes)
        # Save PDF for manual inspection (optional)
        pdf_path = "test_swipe_log_export.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        # Use pymupdf to check PDF content
        doc = fitz.open(pdf_path)
        text = "".join(page.get_text() for page in doc)
        self.assertIn("Swipe Log Export Report", text)
        doc.close()
        os.remove(pdf_path)
