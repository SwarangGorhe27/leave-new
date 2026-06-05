import { create } from "zustand";
import { attendanceEmployees, attendanceExceptions, attendanceRequests, dailyAttendance } from "./mockData";
import { RequestStatus } from "./types";

interface AttendanceState {
  view: "calendar" | "list";
  selectedDate: string | null;
  filters: {
    employeeId: string;
    department: string;
    location: string;
    status: string;
    workMode: string;
    shift: string;
    exceptionType: string;
    from: string;
    to: string;
  };
  setView: (view: "calendar" | "list") => void;
  setSelectedDate: (date: string | null) => void;
  setFilter: (key: keyof AttendanceState["filters"], value: string) => void;
}

export const useAttendanceStore = create<AttendanceState>((set) => ({
  view: "calendar",
  selectedDate: null,
  filters: {
    employeeId: "all",
    department: "all",
    location: "all",
    status: "all",
    workMode: "all",
    shift: "all",
    exceptionType: "all",
    from: "2026-05-01",
    to: "2026-05-31",
  },
  setView: (view) => set({ view }),
  setSelectedDate: (selectedDate) => set({ selectedDate }),
  setFilter: (key, value) => set((state) => ({ filters: { ...state.filters, [key]: value } })),
}));

export const attendanceDataset = {
  employees: attendanceEmployees,
  records: dailyAttendance,
  requests: attendanceRequests,
  exceptions: attendanceExceptions,
};

export const requestBadgeClass: Record<RequestStatus, string> = {
  Pending: "bg-amber-100 text-amber-700 border-amber-300",
  Approved: "bg-emerald-100 text-emerald-700 border-emerald-300",
  Rejected: "bg-rose-100 text-rose-700 border-rose-300",
};
