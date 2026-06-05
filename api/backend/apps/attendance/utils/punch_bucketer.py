"""
Punch Bucketer
==============
Builds a daily punch summary from raw PunchLog rows inside a shift window.

The summary keeps the legacy boundary fields (`first_in`, `last_out`,
`short_leave_mins`, `is_currently_in`) and also exposes session rows that can
be persisted under DailyAttendance.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

DEDUP_THRESHOLD_MINS = 2


@dataclass
class PunchSession:
    session_no: int
    in_time: datetime
    out_time: Optional[datetime] = None
    work_mins: int = 0
    break_mins: int = 0
    in_punch_id: Optional[int] = None
    out_punch_id: Optional[int] = None


@dataclass
class PunchSummary:
    first_in: Optional[datetime] = None
    last_out: Optional[datetime] = None
    short_leave_mins: int = 0
    session_work_mins: int = 0
    is_currently_in: bool = False
    has_any_punch: bool = False
    punch_count: int = 0
    all_punches: list = field(default_factory=list)
    valid_punches: list = field(default_factory=list)
    sessions: list[PunchSession] = field(default_factory=list)
    anomalies: list[dict] = field(default_factory=list)

    @property
    def last_punch_time(self):
        return self.valid_punches[-1].punch_time if self.valid_punches else None

    @property
    def last_punch_type(self):
        return self.valid_punches[-1].punch_type if self.valid_punches else None


# def bucket_punches(employee_id, window_start: datetime, window_end: datetime) -> PunchSummary:
#     from apps.attendance.models.enums import PunchType
#     from apps.attendance.models.punch_and_daily import PunchLog

#     punches = list(
#         PunchLog.objects
#         .filter(
#             employee_id=employee_id,
#             punch_time__gte=window_start,
#             punch_time__lte=window_end,
#         )
#         .exclude(meta_data__is_deleted=True)
#         .order_by("punch_time")
#     )

#     summary = PunchSummary(
#         has_any_punch=len(punches) > 0,
#         punch_count=len(punches),
#         all_punches=punches,
#     )

#     if not punches:
#         return summary

#     valid_punches = [
#         punch for punch in punches
#         if (punch.punch_type or "").upper() in (PunchType.IN, PunchType.OUT)
#     ]
#     summary.valid_punches = _deduplicate_ordered(valid_punches)

#     if not summary.valid_punches:
#         return summary

#     # OUT-only streams are treated as missing IN and intentionally do not enter
#     # pairing logic. This prevents downstream first_in/last_out crashes.
#     if (summary.valid_punches[0].punch_type or "").upper() == PunchType.OUT:
#         first = summary.valid_punches[0]
#         summary.last_out = first.punch_time
#         summary.anomalies.append(_anomaly("MISSING_IN", first, "OUT punch found before any IN punch."))
#         return summary

#     _build_sessions(summary, PunchType.IN, PunchType.OUT)
#     return summary
def bucket_punches(employee_id, window_start: datetime, window_end: datetime) -> PunchSummary:
    from apps.attendance.models.enums import PunchType
    from apps.attendance.models.punch_and_daily import PunchLog

    print("\n================ BUCKET_PUNCHES START ================")
    print("employee_id:", employee_id)
    print("window_start:", window_start)
    print("window_end:", window_end)

    all_employee_punches = PunchLog.objects.filter(
        employee_id=employee_id
    ).order_by("punch_time")

    print("TOTAL PUNCHES FOR EMPLOYEE:", all_employee_punches.count())

    print("ALL EMPLOYEE PUNCHES:")
    for p in all_employee_punches:
        print(
            "  id=", p.id,
            "time=", p.punch_time,
            "type=", p.punch_type,
            "meta_data=", p.meta_data,
        )

    before_exclude = (
        PunchLog.objects
        .filter(
            employee_id=employee_id,
            punch_time__gte=window_start,
            punch_time__lte=window_end,
        )
        .order_by("punch_time")
    )

    print("\nMATCHING WINDOW BEFORE EXCLUDE:", before_exclude.count())
    for p in before_exclude:
        print(
            "  id=", p.id,
            "time=", p.punch_time,
            "type=", p.punch_type,
            "meta_data=", p.meta_data,
        )

    print("\nSQL QUERY:")
    print(
        PunchLog.objects
        .filter(
            employee_id=employee_id,
            punch_time__gte=window_start,
            punch_time__lte=window_end,
        )
        # .exclude(meta_data__contains={"is_deleted": True})
        .order_by("punch_time")
        .query
    )

    punches = list(
        PunchLog.objects
        .filter(
            employee_id=employee_id,
            punch_time__gte=window_start,
            punch_time__lte=window_end,
        )
        .exclude(meta_data__contains={"is_deleted": True})
        .order_by("punch_time")
    )

    print("\nMATCHING WINDOW AFTER EXCLUDE:", len(punches))
    for p in punches:
        print(
            "  id=", p.id,
            "time=", p.punch_time,
            "type=", p.punch_type,
            "meta_data=", p.meta_data,
        )

    summary = PunchSummary(
        has_any_punch=len(punches) > 0,
        punch_count=len(punches),
        all_punches=punches,
    )

    print("\nSUMMARY AFTER QUERY:")
    print("has_any_punch =", summary.has_any_punch)
    print("punch_count =", summary.punch_count)

    if not punches:
        print("RETURNING EARLY: NO PUNCHES")
        print("================ BUCKET_PUNCHES END ================\n")
        return summary

    valid_punches = [
        punch for punch in punches
        if (punch.punch_type or "").upper() in (PunchType.IN, PunchType.OUT)
    ]

    print("\nVALID PUNCHES BEFORE DEDUP:", len(valid_punches))
    for p in valid_punches:
        print(
            "  id=", p.id,
            "time=", p.punch_time,
            "type=", p.punch_type,
        )

    summary.valid_punches = _deduplicate_ordered(valid_punches)

    print("\nVALID PUNCHES AFTER DEDUP:", len(summary.valid_punches))
    for p in summary.valid_punches:
        print(
            "  id=", p.id,
            "time=", p.punch_time,
            "type=", p.punch_type,
        )

    if not summary.valid_punches:
        print("RETURNING EARLY: NO VALID PUNCHES AFTER DEDUP")
        print("================ BUCKET_PUNCHES END ================\n")
        return summary

    if (summary.valid_punches[0].punch_type or "").upper() == PunchType.OUT:
        print("\nOUT-ONLY STREAM DETECTED")

        first = summary.valid_punches[0]

        summary.last_out = first.punch_time
        summary.anomalies.append(
            _anomaly(
                "MISSING_IN",
                first,
                "OUT punch found before any IN punch.",
            )
        )

        print("last_out =", summary.last_out)
        print("anomalies =", summary.anomalies)

        print("================ BUCKET_PUNCHES END ================\n")
        return summary

    print("\nCALLING _build_sessions()")
    _build_sessions(summary, PunchType.IN, PunchType.OUT)

    print("\nAFTER _build_sessions:")
    print("sessions =", len(summary.sessions))
    print("first_in =", summary.first_in)
    print("last_out =", summary.last_out)
    print("is_currently_in =", summary.is_currently_in)
    print("anomalies =", summary.anomalies)

    print("================ BUCKET_PUNCHES END ================\n")
    return summary

def _deduplicate_ordered(punches: list) -> list:
    if not punches:
        return []

    result = []
    cluster = [punches[0]]

    def flush(current):
        if not current:
            return
        punch_type = (current[0].punch_type or "").upper()
        result.append(current[0] if punch_type == "IN" else current[-1])

    for punch in punches[1:]:
        prev = cluster[-1]
        same_type = (punch.punch_type or "").upper() == (prev.punch_type or "").upper()
        gap_mins = (punch.punch_time - prev.punch_time).total_seconds() / 60
        if same_type and gap_mins <= DEDUP_THRESHOLD_MINS:
            cluster.append(punch)
        else:
            flush(cluster)
            cluster = [punch]

    flush(cluster)
    return sorted(result, key=lambda punch: punch.punch_time)


def _build_sessions(summary: PunchSummary, in_type, out_type) -> None:
    open_session: Optional[PunchSession] = None
    last_closed_session: Optional[PunchSession] = None

    for punch in summary.valid_punches:
        punch_type = (punch.punch_type or "").upper()

        if punch_type == in_type:
            if open_session is not None:
                summary.anomalies.append(
                    _anomaly("DUPLICATE_IN", punch, "IN punch found while a session is already open.")
                )
                continue

            break_mins = 0
            if last_closed_session and last_closed_session.out_time:
                gap_mins = int((punch.punch_time - last_closed_session.out_time).total_seconds() / 60)
                break_mins = max(gap_mins, 0)

            open_session = PunchSession(
                session_no=len(summary.sessions) + 1,
                in_time=punch.punch_time,
                break_mins=break_mins,
                in_punch_id=punch.id,
            )
            summary.sessions.append(open_session)
            if summary.first_in is None:
                summary.first_in = punch.punch_time

        elif punch_type == out_type:
            if open_session is None:
                summary.anomalies.append(
                    _anomaly("MISSING_IN", punch, "OUT punch found without a matching open IN session.")
                )
                continue

            open_session.out_time = punch.punch_time
            open_session.out_punch_id = punch.id
            open_session.work_mins = max(
                int((open_session.out_time - open_session.in_time).total_seconds() / 60),
                0,
            )
            summary.last_out = punch.punch_time
            last_closed_session = open_session
            open_session = None

    if open_session is not None:
        summary.is_currently_in = True
        summary.anomalies.append(
            _anomaly("MISSING_OUT", None, "IN punch found without a matching OUT punch.", open_session)
        )

    summary.session_work_mins = sum(session.work_mins for session in summary.sessions)
    summary.short_leave_mins = sum(session.break_mins for session in summary.sessions)


def _anomaly(code: str, punch, message: str, session: PunchSession | None = None) -> dict:
    punch_time = None
    punch_id = None
    if punch is not None:
        punch_time = punch.punch_time
        punch_id = punch.id
    elif session is not None:
        punch_time = session.in_time
        punch_id = session.in_punch_id

    return {
        "code": code,
        "punch_id": punch_id,
        "punch_time": punch_time.isoformat() if punch_time else None,
        "message": message,
    }
