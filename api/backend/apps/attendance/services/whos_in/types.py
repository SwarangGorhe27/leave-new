# apps/attendance/services/admin/whos_in/types.py

from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class WhoIsInFilters:
    company_id: UUID
    attendance_date: date
    shift_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    work_mode_id: Optional[int] = None
    designation_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    search: Optional[str] = None