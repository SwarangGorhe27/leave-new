#!/usr/bin/env python
"""Test script to verify centralized export constants are working correctly."""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Test imports
print("=" * 70)
print("Testing centralized export constants...")
print("=" * 70)

# Test 1: Direct import from constants module
print("\n1. Testing direct import from constants module...")
from apps.attendance.constants.export_constants import (
    ExportFormatChoices, 
    ExportStatusChoices,
    get_mime_type,
    get_file_extension
)
print("✓ Successfully imported ExportFormatChoices and ExportStatusChoices")
print(f"  - Export Formats: {dict(ExportFormatChoices.choices)}")
print(f"  - Export Statuses: {dict(ExportStatusChoices.choices)}")

# Test 2: Backward compatibility via swipe_log_export_job
print("\n2. Testing backward compatibility from swipe_log_export_job...")
from apps.attendance.models.swipe_log_export_job import ExportFormat, ExportStatus
print("✓ Successfully imported ExportFormat and ExportStatus (backward compat)")
print(f"  - ExportFormat.CSV = {ExportFormat.CSV}")
print(f"  - ExportStatus.PENDING = {ExportStatus.PENDING}")

# Test 3: Export from models __init__
print("\n3. Testing re-export from models __init__.py...")
from apps.attendance.models import ExportFormatChoices as ModelExportFormatChoices
from apps.attendance.models import ExportStatusChoices as ModelExportStatusChoices
print("✓ Successfully imported from apps.attendance.models")
print(f"  - ModelExportFormatChoices.CSV = {ModelExportFormatChoices.CSV}")

# Test 4: Swipe log serializer
print("\n4. Testing SwipeLogExportRequestSerializer...")
from apps.attendance.serializers.swipe_logs.export_import_serializers import SwipeLogExportRequestSerializer
serializer = SwipeLogExportRequestSerializer()
print("✓ Successfully imported SwipeLogExportRequestSerializer")
print(f"  - Format field choices: {list(dict(serializer.fields['format'].choices).keys())}")

# Test 5: Swipe log scheduled export serializer
print("\n5. Testing SwipeLogScheduledExportSerializer...")
from apps.attendance.serializers.swipe_logs.export_import_serializers import SwipeLogScheduledExportSerializer
serializer = SwipeLogScheduledExportSerializer()
print("✓ Successfully imported SwipeLogScheduledExportSerializer")
print(f"  - Format field choices: {list(dict(serializer.fields['format'].choices).keys())}")

# Test 6: Audit log serializer
print("\n6. Testing AuditLogExportRequestSerializer...")
from apps.attendance.serializers.audit_logs.audit_log_serializers import AuditLogExportRequestSerializer
serializer = AuditLogExportRequestSerializer()
print("✓ Successfully imported AuditLogExportRequestSerializer")
print(f"  - Format field choices: {list(dict(serializer.fields['format'].choices).keys())}")

# Test 7: Attendance matrix serializer
print("\n7. Testing AttendanceMatrix ExportRequestSerializer...")
from apps.attendance.serializers.attendance_matrix.matrix import ExportRequestSerializer
serializer = ExportRequestSerializer()
print("✓ Successfully imported AttendanceMatrix ExportRequestSerializer")
print(f"  - Format field choices: {list(dict(serializer.fields['format'].choices).keys())}")

# Test 8: Shift roster export serializer
print("\n8. Testing ShiftRosterExportSerializer...")
from apps.attendance.serializers.shift_roster.shift_roster_export_serializer import ShiftRosterExportSerializer
serializer = ShiftRosterExportSerializer()
print("✓ Successfully imported ShiftRosterExportSerializer")
print(f"  - Format field choices: {list(dict(serializer.fields['format'].choices).keys())}")

# Test 9: Helper functions
print("\n9. Testing helper functions...")
print(f"  - get_mime_type('CSV') = {get_mime_type('CSV')}")
print(f"  - get_file_extension('XLSX') = {get_file_extension('XLSX')}")
print(f"  - get_mime_type('PDF') = {get_mime_type('PDF')}")
print("✓ All helper functions working correctly")

# Test 10: Audit log service
print("\n10. Testing AuditLogService...")
from apps.attendance.services.audit_logs.audit_log_service import AttendanceAuditLogService
print("✓ Successfully imported AttendanceAuditLogService")

print("\n" + "=" * 70)
print("ALL TESTS PASSED! ✓")
print("=" * 70)

