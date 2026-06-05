#!/usr/bin/env python
"""
Fix all import paths in HRMS Attendance module after file reorganization.

This script applies all the import changes documented in IMPORT_MAPPING.md

Usage:
    python fix_attendance_imports.py --dry-run      # Show what would be changed
    python fix_attendance_imports.py --fix          # Apply all changes
    python fix_attendance_imports.py --file <path>  # Fix specific file
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Color codes for output
try:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BLUE = '\033[94m'
except:
    GREEN = RED = YELLOW = BLUE = RESET = ''

# Import mappings: (file_path, old_import, new_import)
IMPORT_FIXES: List[Tuple[str, str, str]] = [
    # ========== PRIORITY 1: __init__.py Files ==========
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.shift_service import ShiftService',
        'from apps.attendance.services.shift_roster.shift_service import ShiftService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.shift_rotation_preview_service import (\n    ShiftRotationPreviewService,\n)',
        'from apps.attendance.services.shift_roster.shift_rotation_preview_service import (\n    ShiftRotationPreviewService,\n)'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.shift_logging_service import ShiftLoggingService',
        'from apps.attendance.services.shift_roster.shift_logging_service import ShiftLoggingService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.shift_validation_service import ShiftValidationService',
        'from apps.attendance.services.shift_roster.shift_validation_service import ShiftValidationService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.roster_service import RosterService',
        'from apps.attendance.services.shift_roster.roster_service import RosterService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.roster_summary_service import RosterSummaryService',
        'from apps.attendance.services.shift_roster.roster_summary_service import RosterSummaryService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.roster_export_service import RosterExportService',
        'from apps.attendance.services.shift_roster.roster_export_service import RosterExportService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.matrix import AttendanceMatrixService',
        'from apps.attendance.services.attendance_matrix.matrix import AttendanceMatrixService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.swipe_logs.swipe_log_service import SwipeLogService',
        'from apps.attendance.services.swipe_logs.swipe_log_service import SwipeLogService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.swipe_logs.swipe_log_timeline_service import SwipeLogTimelineService',
        'from apps.attendance.services.swipe_logs.swipe_log_timeline_service import SwipeLogTimelineService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.swipe_logs.swipe_log_export_service import SwipeLogExportService',
        'from apps.attendance.services.swipe_logs.swipe_log_export_service import SwipeLogExportService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.swipe_logs.swipe_log_detection_service import SwipeLogDetectionService',
        'from apps.attendance.services.swipe_logs.swipe_log_detection_service import SwipeLogDetectionService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.swipe_logs.swipe_live_service import SwipeLiveService',
        'from apps.attendance.services.swipe_logs.swipe_live_service import SwipeLiveService'
    ),
    (
        'apps/attendance/services/__init__.py',
        'from apps.attendance.services.swipe_logs.swipe_sync_service import SwipeSyncService',
        'from apps.attendance.services.swipe_logs.swipe_sync_service import SwipeSyncService'
    ),

    # ========== Validators __init__.py ==========
    (
        'apps/attendance/validators/__init__.py',
        'from apps.attendance.validators.shift_validator import ShiftValidator',
        'from apps.attendance.validators.shift_roster.shift_validator import ShiftValidator'
    ),
    (
        'apps/attendance/validators/__init__.py',
        'from apps.attendance.validators.roster_validator import RosterValidator',
        'from apps.attendance.validators.shift_roster.roster_validator import RosterValidator'
    ),
    (
        'apps/attendance/validators/__init__.py',
        'from apps.attendance.validators.swipe_logs.swipe_log_validator import SwipeLogValidator',
        'from apps.attendance.validators.swipe_logs.swipe_log_validator import SwipeLogValidator'
    ),
    (
        'apps/attendance/validators/__init__.py',
        'from apps.attendance.validators.swipe_logs.swipe_live_sync_validators import (\n    SwipeLiveValidator,\n    SwipeSyncValidator,\n    WebSocketValidator,\n)',
        'from apps.attendance.validators.swipe_logs.swipe_live_sync_validators import (\n    SwipeLiveValidator,\n    SwipeSyncValidator,\n    WebSocketValidator,\n)'
    ),

    # ========== Serializers __init__.py ==========
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.shift_roster.shift_type_serializer import (',
        'from apps.attendance.serializers.shift_roster.shift_type_serializer import ('
    ),
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.shift_roster.shift_master_serializer import (',
        'from apps.attendance.serializers.shift_roster.shift_master_serializer import ('
    ),
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.shift_roster.shift_roster_serializer import (',
        'from apps.attendance.serializers.shift_roster.shift_roster_serializer import ('
    ),
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.shift_roster.shift_roster_summary_serializer import (',
        'from apps.attendance.serializers.shift_roster.shift_roster_summary_serializer import ('
    ),
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.shift_roster.shift_roster_export_serializer import (',
        'from apps.attendance.serializers.shift_roster.shift_roster_export_serializer import ('
    ),
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.swipe_logs.swipe_log_serializer import (',
        'from apps.attendance.serializers.swipe_logs.swipe_log_serializer import ('
    ),
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.swipe_logs.swipe_log_detail_serializer import SwipeLogDetailSerializer',
        'from apps.attendance.serializers.swipe_logs.swipe_log_detail_serializer import SwipeLogDetailSerializer'
    ),
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.swipe_logs.swipe_log_timeline_serializer import (',
        'from apps.attendance.serializers.swipe_logs.swipe_log_timeline_serializer import ('
    ),
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.swipe_logs.swipe_log_export_serializer import (',
        'from apps.attendance.serializers.swipe_logs.swipe_log_export_serializer import ('
    ),
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.swipe_logs.swipe_log_bulk_serializer import (',
        'from apps.attendance.serializers.swipe_logs.swipe_log_bulk_serializer import ('
    ),
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.swipe_logs.swipe_live_serializers import (',
        'from apps.attendance.serializers.swipe_logs.swipe_live_serializers import ('
    ),
    (
        'apps/attendance/serializers/__init__.py',
        'from apps.attendance.serializers.swipe_logs.swipe_sync_serializers import (',
        'from apps.attendance.serializers.swipe_logs.swipe_sync_serializers import ('
    ),

    # ========== Views __init__.py ==========
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.admin.shift_roster.shift_master_view import ShiftMasterViewSet',
        'from apps.attendance.views.admin.shift_roster.shift_master_view import ShiftMasterViewSet'
    ),
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.admin.shift_roster.shift_type_view import ShiftTypeViewSet',
        'from apps.attendance.views.admin.shift_roster.shift_type_view import ShiftTypeViewSet'
    ),
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.admin.shift_roster.shift_roster_view import ShiftRosterViewSet',
        'from apps.attendance.views.admin.shift_roster.shift_roster_view import ShiftRosterViewSet'
    ),
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.admin.shift_roster.shift_roster_summary_view import ShiftRosterSummaryViewSet',
        'from apps.attendance.views.admin.shift_roster.shift_roster_summary_view import ShiftRosterSummaryViewSet'
    ),
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.admin.shift_roster.shift_roster_export_view import ShiftRosterExportViewSet',
        'from apps.attendance.views.admin.shift_roster.shift_roster_export_view import ShiftRosterExportViewSet'
    ),
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.matrix import (MatrixCycleBoundsView, MatrixDepartmentsView, MatrixLiveView, MatrixGridView, MatrixSummaryView,\n                                          MatrixImportView, EmployeeDayDetailView,\n                                          EmployeeMonthlySummaryView)',
        'from apps.attendance.views.admin.attendance_matrix.matrix import (MatrixCycleBoundsView, MatrixDepartmentsView, MatrixLiveView, MatrixGridView, MatrixSummaryView,\n                                          MatrixImportView, EmployeeDayDetailView,\n                                          EmployeeMonthlySummaryView)'
    ),
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_view import SwipeLogViewSet',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_view import SwipeLogViewSet'
    ),
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_timeline_view import SwipeLogTimelineAPI',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_timeline_view import SwipeLogTimelineAPI'
    ),
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_bulk_view import SwipeLogBulkAPI',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_bulk_view import SwipeLogBulkAPI'
    ),
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_export_view import SwipeLogExportAPI',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_export_view import SwipeLogExportAPI'
    ),
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.admin.swipe_logs.swipe_live_view import SwipeLiveView',
        'from apps.attendance.views.admin.swipe_logs.swipe_live_view import SwipeLiveView'
    ),
    (
        'apps/attendance/views/__init__.py',
        'from apps.attendance.views.admin.swipe_logs.swipe_sync_view import SwipeSyncView',
        'from apps.attendance.views.admin.swipe_logs.swipe_sync_view import SwipeSyncView'
    ),

    # ========== PRIORITY 2-3: Service Cross-Imports ==========
    (
        'apps/attendance/services/admin/swipe_logs/swipe_log_detection_service.py',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService'
    ),
    (
        'apps/attendance/services/admin/swipe_logs/swipe_log_export_service.py',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService'
    ),
    (
        'apps/attendance/services/admin/swipe_logs/swipe_log_service.py',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService'
    ),
    (
        'apps/attendance/services/admin/swipe_logs/device_service.py',
        'from apps.attendance.validators.device_validator import DeviceValidator',
        'from apps.attendance.validators.device_management.device_validator import DeviceValidator'
    ),
    (
        'apps/attendance/services/swipe_logs/swipe_log_detection_service.py',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService'
    ),
    (
        'apps/attendance/services/swipe_logs/swipe_log_export_service.py',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService',
        'from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService'
    ),
    (
        'apps/attendance/services/swipe_logs/device_service.py',
        'from apps.attendance.validators.device_validator import DeviceValidator',
        'from apps.attendance.validators.device_management.device_validator import DeviceValidator'
    ),

    # ========== PRIORITY 4: Serializer Cross-Imports ==========
    (
        'apps/attendance/serializers/admin/shift_roster/shift_master_serializer.py',
        'from apps.attendance.serializers.shift_roster.shift_type_serializer import ShiftTypeListSerializer',
        'from apps.attendance.serializers.shift_roster.shift_type_serializer import ShiftTypeListSerializer'
    ),
    (
        'apps/attendance/serializers/shift_roster/shift_master_serializer.py',
        'from apps.attendance.serializers.shift_roster.shift_type_serializer import ShiftTypeListSerializer',
        'from apps.attendance.serializers.shift_roster.shift_type_serializer import ShiftTypeListSerializer'
    ),

    # ========== PRIORITY 5: View Cross-Imports ==========
    (
        'apps/attendance/views/attendance_matrix/matrix.py',
        'from apps.attendance.serializers.matrix import (',
        'from apps.attendance.serializers.attendance_matrix.matrix import ('
    ),
    (
        'apps/attendance/views/attendance_matrix/matrix.py',
        'from apps.attendance.services.matrix import AttendanceMatrixService',
        'from apps.attendance.services.attendance_matrix.matrix import AttendanceMatrixService'
    ),
    (
        'apps/attendance/views/admin/attendance_matrix/matrix.py',
        'from apps.attendance.serializers.admin.matrix import (',
        'from apps.attendance.serializers.attendance_matrix.matrix import ('
    ),
    (
        'apps/attendance/views/admin/attendance_matrix/matrix.py',
        'from apps.attendance.services.admin.matrix import AttendanceMatrixService',
        'from apps.attendance.services.attendance_matrix.matrix import AttendanceMatrixService'
    ),
    (
        'apps/attendance/views/whos_in/whos_in.py',
        'from apps.attendance.services.admin.whos_in import (',
        'from apps.attendance.services.whos_in import ('
    ),
    (
        'apps/attendance/views/admin/whos_in/whos_in.py',
        'from apps.attendance.services.admin.whos_in import (',
        'from apps.attendance.services.whos_in import ('
    ),

    # ========== PRIORITY 6: URL Imports ==========
    (
        'apps/attendance/urls/admin_urls.py',
        'from apps.attendance.views.device_view import DeviceViewSet',
        'from apps.attendance.views.device_management.device_view import DeviceViewSet'
    ),
    (
        'apps/attendance/urls/admin_urls.py',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_timeline_view import SwipeLogTimelineAPI',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_timeline_view import SwipeLogTimelineAPI'
    ),
    (
        'apps/attendance/urls/admin_urls.py',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_bulk_view import SwipeLogBulkAPI',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_bulk_view import SwipeLogBulkAPI'
    ),
    (
        'apps/attendance/urls/admin_urls.py',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_export_view import SwipeLogExportAPI',
        'from apps.attendance.views.admin.swipe_logs.swipe_log_export_view import SwipeLogExportAPI'
    ),
    (
        'apps/attendance/urls/admin_urls.py',
        'from apps.attendance.views.admin.swipe_logs.swipe_live_view import SwipeLiveView',
        'from apps.attendance.views.admin.swipe_logs.swipe_live_view import SwipeLiveView'
    ),
    (
        'apps/attendance/urls/admin_urls.py',
        'from apps.attendance.views.admin.swipe_logs.swipe_sync_view import SwipeSyncView',
        'from apps.attendance.views.admin.swipe_logs.swipe_sync_view import SwipeSyncView'
    ),
    (
        'apps/attendance/urls/admin_urls.py',
        'from apps.attendance.views.matrix import (',
        'from apps.attendance.views.admin.attendance_matrix.matrix import ('
    ),
    (
        'apps/attendance/urls/admin_urls.py',
        'from apps.attendance.views.admin.whos_in import (',
        'from apps.attendance.views.admin.whos_in import ('
    ),
    (
        'apps/attendance/urls/device_urls.py',
        'from apps.attendance.views.device_view import DeviceViewSet',
        'from apps.attendance.views.device_management.device_view import DeviceViewSet'
    ),
    (
        'apps/attendance/urls/analytics_urls.py',
        'from apps.attendance.views.attendance_analytics_view import (',
        'from apps.attendance.views.attendance_intelligence.attendance_analytics_view import ('
    ),
    # ========== NEW RELOCATION MAPPINGS (2026 REORGANIZATION) ==========
    (
        '',  # Global replacement
        'from apps.attendance.views.device_management.device_view import DeviceViewSet',
        'from apps.attendance.views.device_management.device_view import DeviceViewSet'
    ),
    (
        '',
        'from apps.attendance.views.attendance_intelligence.attendance_analytics_view import',
        'from apps.attendance.views.attendance_intelligence.attendance_analytics_view import'
    ),
    (
        '',
        'from apps.attendance.services.device_management.device_service import DeviceService',
        'from apps.attendance.services.device_management.device_service import DeviceService'
    ),
    (
        '',
        'from apps.attendance.services.attendance_intelligence.attendance_analytics_service import',
        'from apps.attendance.services.attendance_intelligence.attendance_analytics_service import'
    ),
    (
        '',
        'from apps.attendance.serializers.device_management.device_serializer import',
        'from apps.attendance.serializers.device_management.device_serializer import'
    ),
    (
        '',
        'from apps.attendance.serializers.attendance_intelligence.attendance_analytics_serializer import',
        'from apps.attendance.serializers.attendance_intelligence.attendance_analytics_serializer import'
    ),
    (
        '',
        'from apps.attendance.validators.device_management.device_validator import DeviceValidator',
        'from apps.attendance.validators.device_management.device_validator import DeviceValidator'
    ),
]


def find_project_root() -> Path:
    """Find the Django project root (where manage.py is located)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / 'manage.py').exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find Django project root (manage.py)")


def apply_fix(file_path: Path, old_import: str, new_import: str, dry_run: bool = True) -> bool:
    """Apply a single import fix to a file."""
    if not file_path.exists():
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if old_import not in content:
            return False

        new_content = content.replace(old_import, new_import)

        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        return True
    except Exception as e:
        print(f"{RED}[ERROR] Error processing {file_path}: {e}{RESET}")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Fix HRMS Attendance import paths')
    parser.add_argument('--fix', action='store_true', help='Apply fixes (default is dry-run)')
    parser.add_argument('--file', type=str, help='Fix specific file only')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')

    args = parser.parse_args()

    dry_run = not args.fix
    project_root = find_project_root()
    os.chdir(project_root)

    mode_text = 'DRY RUN' if dry_run else 'FIXING'
    print(f"\n{BLUE}{'='*70}")
    print(f"HRMS Attendance - Import Path Fixer ({mode_text})")
    print(f"{'='*70}{RESET}\n")

    # Separate global and specific fixes
    global_fixes = [(o, n) for f, o, n in IMPORT_FIXES if not f]
    specific_fixes_by_file: Dict[str, List[Tuple[str, str]]] = {}
    for file_path, old_import, new_import in IMPORT_FIXES:
        if file_path:
            if file_path not in specific_fixes_by_file:
                specific_fixes_by_file[file_path] = []
            specific_fixes_by_file[file_path].append((old_import, new_import))

    total_fixes = 0
    successful_fixes = 0
    files_processed = set()

    # 1. Apply global fixes to all Python files in attendance app
    attendance_dir = project_root / 'apps' / 'attendance'
    if global_fixes:
        print(f"{YELLOW}Applying global fixes to {attendance_dir}...{RESET}")
        for py_file in attendance_dir.rglob('*.py'):
            rel_path = py_file.relative_to(project_root).as_posix()
            if args.file and args.file not in rel_path:
                continue
                
            for old_import, new_import in global_fixes:
                total_fixes += 1
                if apply_fix(py_file, old_import, new_import, dry_run):
                    successful_fixes += 1
                    files_processed.add(rel_path)
                    if args.verbose:
                        print(f"  {GREEN}[OK]{RESET} {rel_path}: {old_import[:40]}...")

    # 2. Apply specific fixes
    for rel_path_str, import_fixes in sorted(specific_fixes_by_file.items()):
        if args.file and args.file not in rel_path_str:
            continue
            
        file_path = project_root / rel_path_str
        for old_import, new_import in import_fixes:
            total_fixes += 1
            if apply_fix(file_path, old_import, new_import, dry_run):
                successful_fixes += 1
                files_processed.add(rel_path_str)
                if args.verbose:
                    print(f"  {GREEN}[OK]{RESET} {rel_path_str}: {old_import[:40]}...")

    # Summary
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"Summary: {successful_fixes}/{total_fixes} fixes applied/identified")
    print(f"Files affected: {len(files_processed)}")

    if dry_run:
        print(f"\n{YELLOW}This was a DRY RUN. Use --fix to apply changes.{RESET}")
    else:
        print(f"\n{GREEN}[OK] All fixes applied!{RESET}")

    print(f"{BLUE}{'='*70}{RESET}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())


if __name__ == '__main__':
    sys.exit(main())





