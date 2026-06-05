"""Resolve user-facing shift codes for roster and calendar APIs."""

from __future__ import annotations

import re
from datetime import time
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from apps.attendance.models import ShiftDefinition, ShiftMaster


def _time_key(start_time, end_time, cross_midnight: bool) -> Tuple:
    return (start_time, end_time, bool(cross_midnight))


def _is_internal_code(code: Optional[str]) -> bool:
    """Internal attendance definition codes (SD_* or long underscore tokens)."""
    c = (code or "").strip().upper()
    if not c:
        return False
    if c.startswith("SD_"):
        return True
    return len(c) > 10 and "_" in c


def _parse_sd_code_times(code: str) -> Optional[Tuple[time, time]]:
    """Extract start/end from codes like SD_US1_1600_0100."""
    match = re.match(
        r"^SD_[A-Z0-9]+_(\d{2})(\d{2})_(\d{2})(\d{2})$",
        (code or "").strip().upper(),
    )
    if not match:
        return None
    return (
        time(int(match.group(1)), int(match.group(2))),
        time(int(match.group(3)), int(match.group(4))),
    )


def _pick_display_master(candidates: List[ShiftMaster]) -> Optional[ShiftMaster]:
    if not candidates:
        return None
    short = [m for m in candidates if not _is_internal_code(m.code)]
    if short:
        return min(short, key=lambda m: len((m.code or "").strip()))
    return candidates[0]


class ShiftDisplayResolver:
    """
    Maps attendance ShiftDefinition records to Shift Master display codes (MG, NS, …).
    """

    def __init__(
        self,
        masters: List[ShiftMaster],
        def_display_by_id: Dict[str, str],
    ):
        self._masters = masters
        self._def_display_by_id = def_display_by_id

    @classmethod
    def build(cls, company_id: UUID) -> "ShiftDisplayResolver":
        masters = list(
            ShiftMaster.objects.filter(
                company_id=company_id,
                deleted_at__isnull=True,
                is_active=True,
            )
        )
        def_display = cls._build_definition_display_map(company_id, masters)
        return cls(masters, def_display)

    @classmethod
    def _build_definition_display_map(
        cls,
        company_id: UUID,
        masters: List[ShiftMaster],
    ) -> Dict[str, str]:
        definitions = ShiftDefinition.objects.filter(
            company_id=company_id,
            deleted_at__isnull=True,
            is_active=True,
        ).select_related("hr_shift")
        return {
            str(defn.id): cls._resolve_definition_display(defn, masters)
            for defn in definitions
        }

    @classmethod
    def _resolve_definition_display(
        cls,
        defn: ShiftDefinition,
        masters: List[ShiftMaster],
    ) -> str:
        hr_shift = getattr(defn, "hr_shift", None)
        if hr_shift is not None and getattr(hr_shift, "code", None):
            hr_code = str(hr_shift.code).strip().upper()
            if hr_code and not _is_internal_code(hr_code):
                return hr_code

        picked = _pick_display_master(
            cls._masters_matching_times(defn.start_time, defn.end_time, masters)
        )
        if picked:
            return (picked.code or "").strip().upper()

        parsed = _parse_sd_code_times(defn.code or "")
        if parsed:
            picked = _pick_display_master(
                cls._masters_matching_times(parsed[0], parsed[1], masters)
            )
            if picked:
                return (picked.code or "").strip().upper()

        def_code = (defn.code or "").strip()
        def_upper = def_code.upper()
        if not _is_internal_code(def_upper):
            for master in masters:
                if (master.code or "").strip().upper() == def_upper:
                    return def_upper
            return def_upper

        def_name = (defn.name or "").strip().lower()
        if def_name:
            for master in masters:
                master_name = (master.name or "").strip().lower()
                master_code = (master.code or "").strip().upper()
                if not master_name or _is_internal_code(master_code):
                    continue
                if master_name in def_name or def_name in master_name:
                    return master_code

        return def_code

    @staticmethod
    def _masters_matching_times(
        start: time,
        end: time,
        masters: List[ShiftMaster],
    ) -> List[ShiftMaster]:
        return [m for m in masters if m.start_time == start and m.end_time == end]

    def display_code(self, shift: ShiftDefinition) -> str:
        """Return Shift Master / HR short code for roster display."""
        sid = str(shift.id)
        if sid in self._def_display_by_id:
            return self._def_display_by_id[sid]
        return self._resolve_definition_display(shift, self._masters)

    def roster_shift_options(self, company_id: UUID) -> List[Dict[str, Any]]:
        """Shift picker: ShiftDefinition id with display code from Shift Master."""
        definitions = (
            ShiftDefinition.objects.filter(
                company_id=company_id,
                deleted_at__isnull=True,
                is_active=True,
            )
            .select_related("hr_shift")
            .order_by("code")
        )
        options: List[Dict[str, Any]] = []
        seen_codes: set[str] = set()
        for shift_def in definitions:
            def_code = (shift_def.code or "").strip()
            name = (shift_def.name or def_code).strip()
            name_key = name.upper()
            if name_key in seen_codes:
                continue
            seen_codes.add(name_key)
            options.append(
                {
                    "id": str(shift_def.id),
                    "code": def_code,
                    "name": name,
                    "definition_code": def_code,
                    "start_time": shift_def.start_time.strftime("%H:%M"),
                    "end_time": shift_def.end_time.strftime("%H:%M"),
                }
            )
        return options
