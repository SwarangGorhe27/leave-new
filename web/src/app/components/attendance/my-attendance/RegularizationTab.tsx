import { useState, useMemo, useEffect } from "react";
import {
  format,
  isSameMonth,
  parse,
  startOfMonth,
  eachDayOfInterval,
  startOfWeek,
  endOfWeek,
  endOfMonth,
  isAfter,
  parseISO,
  isToday,
} from "date-fns";

import {
  ChevronLeft,
  ChevronRight,
  Send,
  ArrowRight,
  Info,
  Lock,
} from "lucide-react";

import { DailyAttendance } from "../../../modules/attendance/types";
import { isDateLocked } from "./utils";
import { motion } from "motion/react";
import type { RegularizationBulkPayload } from "../../../../api/employeeAttendanceClient";

interface RegularizationTabProps {
  records: DailyAttendance[];
  initialDate?: string | null;
  readOnly?: boolean;
  onSubmitRegularization?: (payload: RegularizationBulkPayload) => Promise<void>;
}

export function RegularizationTab({
  records,
  initialDate,
  readOnly = false,
  onSubmitRegularization,
}: RegularizationTabProps) {
  const [currentNavDate, setCurrentNavDate] = useState(new Date());

  const [selectedDates, setSelectedDates] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const [perDateComments, setPerDateComments] = useState<
    Record<string, string>
  >({});

  const [requestType, setRequestType] =
    useState("Missing Punch");

  const [requestStatus, setRequestStatus] =
    useState("Present");

  const [correctedInTime, setCorrectedInTime] =
    useState("");

  const [correctedOutTime, setCorrectedOutTime] =
    useState("");

  useEffect(() => {
    if (initialDate) {
      const date = parse(initialDate, "yyyy-MM-dd", new Date());

      const dateKey = format(date, "yyyy-MM-dd");

      setSelectedDates([dateKey]);

      setCurrentNavDate(startOfMonth(date));
    }
  }, [initialDate]);

  useEffect(() => {
    setPerDateComments((prev) => {
      const next: Record<string, string> = {};

      selectedDates.forEach((d) => {
        next[d] = prev[d] || "";
      });

      return next;
    });
  }, [selectedDates]);

  const monthStart = startOfMonth(currentNavDate);

  const calendarDays = eachDayOfInterval({
    start: startOfWeek(monthStart),
    end: endOfWeek(endOfMonth(monthStart)),
  });

  const isLocked = selectedDates.some((date) =>
    isDateLocked(parse(date, "yyyy-MM-dd", new Date()))
  );

  const toggleSelectedDate = (
    day: Date,
    isCurrentMonthDay: boolean,
    isFuture: boolean
  ) => {
    if (!isCurrentMonthDay || isFuture) return;

    const dateKey = format(day, "yyyy-MM-dd");

    setSelectedDates((prev) =>
      prev.includes(dateKey)
        ? prev.filter((d) => d !== dateKey)
        : [...prev, dateKey].sort()
    );
  };

  const needsRegularization = (record?: DailyAttendance) => {
    if (!record) return false;

    return (
      record.isLate ||
      record.earlyExitMins > 0 ||
      record.status === "Half Day" ||
      record.status === "Absent" ||
      !record.firstIn ||
      !record.lastOut
    );
  };

  const selectedCount = selectedDates.length;

  const handleSubmit = async () => {
    if (!onSubmitRegularization || readOnly || isLocked || selectedCount === 0) return;

    const missingReason = selectedDates.some((date) => (perDateComments[date] || "").trim().length < 10);
    if (missingReason) {
      setSubmitError("Each selected date requires a reason of at least 10 characters.");
      return;
    }

    setSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);
    try {
      await onSubmitRegularization({
        dates: selectedDates.map((date) => ({
          date,
          reason: perDateComments[date].trim(),
        })),
        request_type: requestType,
        requested_status: requestStatus,
        corrected_in_time: correctedInTime || null,
        corrected_out_time: correctedOutTime || null,
      });
      setSubmitSuccess(true);
      setSelectedDates([]);
      setPerDateComments({});
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to submit regularization request.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

      {/* CALENDAR */}
      <div className="lg:col-span-5 space-y-6">

        <div className="attendance-regularization-panel p-6 rounded-[32px] border border-white/10 bg-white/60 dark:bg-[#111827]/60 backdrop-blur-2xl shadow-[0_10px_40px_rgba(0,0,0,0.08)] dark:shadow-[0_10px_40px_rgba(0,0,0,0.4)]">

          {/* HEADER */}
          <div className="flex items-center justify-between mb-8">

            <h3 className="text-[22px] font-bold text-slate-900 dark:text-white">
              {format(currentNavDate, "MMMM yyyy")}
            </h3>

            <div className="flex items-center gap-2">

              <button
                onClick={() =>
                  setCurrentNavDate(
                    (prev) =>
                      new Date(
                        prev.getFullYear(),
                        prev.getMonth() - 1,
                        1
                      )
                  )
                }
                className="w-10 h-10 rounded-2xl border border-black/5 dark:border-white/10 bg-white/70 dark:bg-white/5 flex items-center justify-center hover:scale-105 transition-all"
              >
                <ChevronLeft size={18} />
              </button>

              <button
                onClick={() =>
                  setCurrentNavDate(
                    (prev) =>
                      new Date(
                        prev.getFullYear(),
                        prev.getMonth() + 1,
                        1
                      )
                  )
                }
                className="w-10 h-10 rounded-2xl border border-black/5 dark:border-white/10 bg-white/70 dark:bg-white/5 flex items-center justify-center hover:scale-105 transition-all"
              >
                <ChevronRight size={18} />
              </button>

            </div>
          </div>

          {/* WEEK */}
          <div className="grid grid-cols-7 mb-3">
            {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(
              (day) => (
                <div
                  key={day}
                  className="text-center text-[11px] font-semibold text-slate-500 dark:text-slate-400 py-2"
                >
                  {day}
                </div>
              )
            )}
          </div>

          {/* GRID */}
          <div className="grid grid-cols-7 gap-2">

            {calendarDays.map((day, i) => {

              const dateKey = format(day, "yyyy-MM-dd");

              const isSel = selectedDates.includes(dateKey);

              const isCurrentMonthDay = isSameMonth(
                day,
                monthStart
              );

              const isTodayDate = isToday(day);

              const isFuture = isAfter(day, new Date());

              const locked = isDateLocked(day);

              const dayRecord = records.find(
                (record) => record.date === dateKey
              );

              const regularize =
                needsRegularization(dayRecord);

              return (
                <motion.button
                  key={i}
                  whileHover={{
                    scale: isCurrentMonthDay ? 1.03 : 1,
                    y: isCurrentMonthDay ? -2 : 0,
                  }}
                  transition={{
                    duration: 0.2,
                  }}
                  disabled={!isCurrentMonthDay || isFuture}
                  onClick={() =>
                    toggleSelectedDate(
                      day,
                      isCurrentMonthDay,
                      isFuture
                    )
                  }
                  className={`
                    relative
                    h-[92px]
                    rounded-[24px]
                    transition-all
                    overflow-hidden
                    border

                    ${
                      isCurrentMonthDay
                        ? "opacity-100"
                        : "opacity-25"
                    }

                    ${
                      isSel
                        ? "border-indigo-500 bg-indigo-500/10 dark:bg-indigo-500/15"
                        : "border-black/[0.06] dark:border-white/[0.06]"
                    }

                    ${
                      isTodayDate
                        ? "ring-2 ring-indigo-500/40"
                        : ""
                    }

                    bg-white/70
                    dark:bg-[#182033]/70

                    backdrop-blur-xl
                  `}
                >

                  {/* DATE */}
                  <div className="absolute top-3 left-3">
                    <span
                      className={`
                        text-[15px]
                        font-semibold

                        ${
                          isTodayDate
                            ? "text-indigo-600 dark:text-indigo-400"
                            : "text-slate-900 dark:text-white"
                        }
                      `}
                    >
                      {format(day, "d")}
                    </span>
                  </div>

                  {/* STATUS */}
                  {dayRecord && (
                    <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">

                      <span className="text-[10px] font-medium text-slate-600 dark:text-slate-300 truncate">
                        {dayRecord.status}
                      </span>

                      {regularize && (
                        <span
                          className="
                            w-2 h-2
                            rounded-full
                            bg-yellow-400
                            shadow-[0_0_10px_rgba(250,204,21,0.45)]
                          "
                        />
                      )}

                    </div>
                  )}

                  {/* LOCK */}
                  {locked && (
                    <Lock
                      size={12}
                      className="absolute top-3 right-3 text-rose-500"
                    />
                  )}
                </motion.button>
              );
            })}
          </div>
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="lg:col-span-7">

        <div className="attendance-regularization-panel p-8 rounded-[32px] border border-white/10 bg-white/60 dark:bg-[#111827]/60 backdrop-blur-2xl">

          {selectedCount === 0 ? (

            <div className="h-full flex flex-col items-center justify-center text-center opacity-40 py-16">

              <div className="w-20 h-20 rounded-full bg-black/5 dark:bg-white/5 flex items-center justify-center mb-5">
                <ArrowRight
                  size={38}
                  className="text-slate-400"
                />
              </div>

              <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                Select dates
              </h3>

              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                Click dates that need regularization
              </p>

            </div>

          ) : (

            <form className="space-y-6">

              <div>

                <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                  Submit Regularization
                </h3>

                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  {selectedCount} selected dates
                </p>

              </div>

              <div className="space-y-2">

                <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                  Request Type
                </label>

                <select
                  value={requestType}
                  onChange={(e) =>
                    setRequestType(e.target.value)
                  }
                  className="w-full h-12 rounded-2xl border border-black/[0.06] dark:border-white/[0.06] bg-white/70 dark:bg-white/[0.03] px-4 text-sm text-slate-900 dark:text-white outline-none"
                >
                  <option>Missing Punch</option>
                  <option>Late Arrival</option>
                  <option>Early Exit</option>
                  <option>Half Day</option>
                  <option>Work From Home</option>
                </select>

              </div>

              <div className="space-y-2">

                <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                  Request Status
                </label>

                <select
                  value={requestStatus}
                  onChange={(e) =>
                    setRequestStatus(e.target.value)
                  }
                  className="w-full h-12 rounded-2xl border border-black/[0.06] dark:border-white/[0.06] bg-white/70 dark:bg-white/[0.03] px-4 text-sm text-slate-900 dark:text-white outline-none"
                >
                  <option>Present</option>
                  <option>Half Day</option>
                  <option>Absent</option>
                </select>

              </div>

              <div className="grid grid-cols-2 gap-4">

                <div className="space-y-2">

                  <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                    Corrected In Time
                  </label>

                  <input
                    type="time"
                    value={correctedInTime}
                    onChange={(e) =>
                      setCorrectedInTime(e.target.value)
                    }
                    className="w-full h-12 rounded-2xl border border-black/[0.06] dark:border-white/[0.06] bg-white/70 dark:bg-white/[0.03] px-4 text-sm text-slate-900 dark:text-white outline-none"
                  />

                </div>

                <div className="space-y-2">

                  <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                    Corrected Out Time
                  </label>

                  <input
                    type="time"
                    value={correctedOutTime}
                    onChange={(e) =>
                      setCorrectedOutTime(e.target.value)
                    }
                    className="w-full h-12 rounded-2xl border border-black/[0.06] dark:border-white/[0.06] bg-white/70 dark:bg-white/[0.03] px-4 text-sm text-slate-900 dark:text-white outline-none"
                  />

                </div>

              </div>

              <div className="space-y-4">

                <label className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                  Reasons Per Selected Date
                </label>

                {selectedDates.map((date) => (

                  <div
                    key={date}
                    className="p-4 rounded-2xl bg-white/60 dark:bg-white/[0.03] border border-black/[0.06] dark:border-white/[0.06]"
                  >

                    <div className="flex items-center justify-between mb-3">

                      <p className="text-sm font-semibold text-slate-900 dark:text-white">
                        {format(
                          parseISO(date),
                          "EEE, dd MMM yyyy"
                        )}
                      </p>

                      <span className="text-[10px] text-slate-500">
                        {date}
                      </span>

                    </div>

                    <textarea
                      rows={3}
                      disabled={isLocked}
                      value={perDateComments[date] || ""}
                      onChange={(e) =>
                        setPerDateComments((prev) => ({
                          ...prev,
                          [date]: e.target.value,
                        }))
                      }
                      placeholder="Enter reason for this date"
                      className="
                        w-full
                        rounded-2xl
                        border
                        border-black/[0.06]
                        dark:border-white/[0.06]
                        bg-white/70
                        dark:bg-white/[0.03]
                        px-4
                        py-3
                        text-sm
                        text-slate-900
                        dark:text-white
                        outline-none
                        resize-none
                      "
                    />

                  </div>

                ))}

              </div>

              <button
                type="button"
                disabled={isLocked || submitting || readOnly || !onSubmitRegularization}
                onClick={() => void handleSubmit()}
                className="
                  w-full
                  h-14
                  rounded-[22px]
                  bg-indigo-600
                  hover:bg-indigo-700
                  text-white
                  font-semibold
                  transition-all
                  flex
                  items-center
                  justify-center
                  gap-2
                  disabled:opacity-50
                "
              >
                <Send size={18} />
                {submitting ? "Submitting…" : "Submit Request"}
              </button>

              {submitSuccess ? (
                <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-600 font-medium">
                  Regularization request submitted successfully.
                </div>
              ) : null}

              {submitError ? (
                <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-500 font-medium">
                  {submitError}
                </div>
              ) : null}

              {isLocked && (
                <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center gap-3">

                  <Info
                    size={16}
                    className="text-rose-500"
                  />

                  <p className="text-xs text-rose-500 font-medium">
                    One or more selected dates are locked.
                  </p>

                </div>
              )}

            </form>
          )}
        </div>
      </div>
    </div>
  );
}