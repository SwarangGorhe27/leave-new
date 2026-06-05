"""mst_exception_type — anomaly codes for att_exception (v7 Section L)."""

from django.db import models


class ExceptionType(models.Model):
    id = models.SmallAutoField(primary_key=True)
    code = models.CharField(max_length=40, unique=True)
    label = models.CharField(max_length=120)
    auto_flag = models.BooleanField(default=True)
    notify_hr = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_exception_type"
        ordering = ("code",)

    def __str__(self) -> str:
        return self.label
