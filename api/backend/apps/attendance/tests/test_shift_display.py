"""Tests for shift display code resolution."""

from datetime import time
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from apps.attendance.utils.shift_display import (
    ShiftDisplayResolver,
    _is_internal_code,
    _parse_sd_code_times,
    _pick_display_master,
)


class ShiftDisplayHelpersTests(SimpleTestCase):
    def test_internal_code_detection(self):
        self.assertTrue(_is_internal_code("SD_US1_1600_0100"))
        self.assertFalse(_is_internal_code("MG"))
        self.assertFalse(_is_internal_code("NS"))

    def test_parse_sd_code_times(self):
        parsed = _parse_sd_code_times("SD_US1_1600_0100")
        self.assertEqual(parsed, (time(16, 0), time(1, 0)))

    def test_pick_display_master_prefers_short_code(self):
        internal = MagicMock(code="SD_US1_1600_0100")
        short = MagicMock(code="NS")
        picked = _pick_display_master([internal, short])
        self.assertEqual(picked.code, "NS")


class ShiftDisplayResolverTests(SimpleTestCase):
    def test_prefers_hr_shift_code(self):
        master = MagicMock(
            code="SD_US1_1600_0100",
            name="US 1",
            start_time=time(16, 0),
            end_time=time(1, 0),
            cross_midnight=True,
        )
        resolver = ShiftDisplayResolver([master], {})
        shift = MagicMock()
        shift.id = "def-1"
        shift.code = "SD_US1_1600_0100"
        shift.name = "US 1 Shift"
        shift.start_time = time(16, 0)
        shift.end_time = time(1, 0)
        shift.cross_midnight = True
        shift.hr_shift = MagicMock(code="US")
        self.assertEqual(
            ShiftDisplayResolver._resolve_definition_display(shift, [master]),
            "US",
        )

    def test_matches_shift_master_by_timing(self):
        master = MagicMock(
            code="NS",
            name="Night Shift",
            start_time=time(16, 0),
            end_time=time(1, 0),
            cross_midnight=True,
        )
        shift = MagicMock()
        shift.id = "def-1"
        shift.code = "SD_US1_1600_0100"
        shift.name = "US 1 Shift"
        shift.start_time = time(16, 0)
        shift.end_time = time(1, 0)
        shift.cross_midnight = True
        shift.hr_shift = None
        self.assertEqual(
            ShiftDisplayResolver._resolve_definition_display(shift, [master]),
            "NS",
        )

    def test_parses_sd_code_to_match_master(self):
        master = MagicMock(
            code="MG",
            name="Morning",
            start_time=time(9, 30),
            end_time=time(18, 30),
            cross_midnight=False,
        )
        shift = MagicMock()
        shift.code = "SD_DAY_0930_1830"
        shift.name = "Day"
        shift.start_time = time(10, 0)
        shift.end_time = time(19, 0)
        shift.cross_midnight = False
        shift.hr_shift = None
        self.assertEqual(
            ShiftDisplayResolver._resolve_definition_display(shift, [master]),
            "MG",
        )
