"""
ISSUES:- 
    1. employee FK needs to be configured later.
"""

# apps/leave/models/document/leave_documents.py

"""
================================================================================
MODEL: leave_documents
================================================================================

Purpose:
--------
Stores uploaded documents related to leave requests.

Examples:
---------
- Medical certificates
- Doctor prescriptions
- Travel documents
- Emergency proof
- HR supporting documents

Why separate table instead of file field in leave_requests:
-----------------------------------------------------------
A leave request may contain MULTIPLE documents.

Examples:
    - prescription
    - lab report
    - hospital admission proof

This table enables:
    - multiple attachments
    - scalable document storage
    - audit tracking
    - document metadata management

Storage Strategy:
-----------------
Actual files are typically stored in:
    - AWS S3
    - Azure Blob
    - GCP Storage
    - MinIO
    - CDN/File server

Database stores:
    - metadata
    - file URL/path
    - uploader info

Production Considerations:
--------------------------
- virus scanning
- secure/private URLs
- signed URL generation
- storage lifecycle policies
- access control
- retention compliance

Usage Across System:
--------------------
- Leave approval workflow
- HR verification
- Audit exports
- Employee document access
- Compliance checks

================================================================================
"""

import uuid
from django.db import models


# =========================================================
# MODEL
# =========================================================


class LeaveDocument(models.Model):
    """
    Documents uploaded for leave requests
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # =========================================================
    # Parent Leave Request
    # =========================================================

    leave_request = models.ForeignKey(
        "leave.LeaveRequest", on_delete=models.CASCADE, related_name="documents"
    )

    # =========================================================
    # File Information
    # =========================================================

    file_name = models.CharField(max_length=255)

    file_url = models.TextField()

    file_type = models.CharField(
        max_length=50, null=True, blank=True, help_text="MIME Type"
    )

    file_size_kb = models.IntegerField(null=True, blank=True)

    # =========================================================
    # Upload Tracking
    # =========================================================

    uploaded_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="uploaded_leave_documents",
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_documents"

        ordering = ["-uploaded_at"]

        indexes = [
            models.Index(fields=["leave_request"]),
            models.Index(fields=["uploaded_by"]),
            models.Index(fields=["uploaded_at"]),
            models.Index(fields=["file_type"]),
        ]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.file_name} | " f"{self.leave_request.id}"
