"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
    2. employee FK needs to be configured later.
"""

# apps/holiday/models/holiday_branch_map.py

"""
================================================================================
MODEL: holiday_branch_map
================================================================================

Purpose:
--------
Maps holidays to specific branches/locations.

Why this table is needed:
-------------------------
Not all holidays apply to every branch.

Examples:
---------

1. State-Specific Holidays
--------------------------
Mumbai Branch:
    Maharashtra Day

Bangalore Branch:
    Kannada Rajyotsava

2. Regional Festivals
---------------------
Chennai:
    Pongal

Kolkata:
    Durga Puja

3. International Offices
------------------------
India Office:
    Diwali

US Office:
    Thanksgiving

Without this mapping:
---------------------
- holidays become globally applied
- regional calendars become inaccurate
- attendance calculations break
- leave sandwich logic becomes incorrect

Production Usage:
-----------------
Used in:
    - attendance calculation
    - leave sandwich policy
    - holiday calendar rendering
    - payroll working-day computation
    - branch-wise holiday APIs

================================================================================
"""

import uuid
from django.db import models


# =========================================================
# MODEL
# =========================================================


class HolidayBranchMap(models.Model):
    """
    Holiday ↔ Branch Mapping
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    holiday = models.ForeignKey(
        "employees.HolidayCalendar",
        on_delete=models.CASCADE,
        related_name="branch_mappings",
    )

    branch = models.ForeignKey(
        "employees.Branch", on_delete=models.CASCADE, related_name="holiday_mappings"
    )

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "holiday_branch_map"

        indexes = [
            models.Index(fields=["holiday"]),
            models.Index(fields=["branch"]),
            models.Index(fields=["holiday", "branch"]),
        ]

        unique_together = [("holiday", "branch")]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.holiday} -> " f"{self.branch}"
