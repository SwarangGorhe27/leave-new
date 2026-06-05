import uuid
from django.db import models
from django.utils import timezone


class ImportStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class SwipeLogImportJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="swipe_log_imports"
    )
    created_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        db_column="created_by",
        related_name="swipe_log_imports_created"
    )
    device_id = models.IntegerField(null=True, blank=True)
    import_mode = models.CharField(max_length=50, default="APPEND")
    dry_run = models.BooleanField(default=False)
    
    file_path = models.CharField(max_length=500, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=ImportStatus.choices, default=ImportStatus.PENDING)
    
    total_rows = models.IntegerField(default=0)
    accepted = models.IntegerField(default=0)
    rejected = models.IntegerField(default=0)
    duplicate_detected = models.IntegerField(default=0)
    
    errors = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "att_swipe_log_import_job"
        verbose_name_plural = "Swipe Log Import Jobs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"SwipeLogImportJob(id={self.id}, status={self.status})"
