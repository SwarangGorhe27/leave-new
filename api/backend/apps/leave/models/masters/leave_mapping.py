from django.db import models


class LeaveMapping(models.Model):
    role = models.CharField(max_length=100)
    leave_type = models.ForeignKey(
        "leave.LeaveType",
        on_delete=models.CASCADE,
        related_name="role_mappings",
    )
    allowed_days = models.PositiveIntegerField()

    class Meta:
        db_table = "mst_leave_mapping"
        ordering = ["role", "leave_type__name"]
        unique_together = [("role", "leave_type")]

    def __str__(self):
        return f"{self.role} - {self.leave_type.code}"
