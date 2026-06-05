import { useState, useMemo } from "react";
import { format, parseISO } from "date-fns";
import { AttendanceRequest } from "../../../modules/attendance/types";
import { Search, Filter, Calendar, Clock, User, MessageCircle, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import { motion } from "motion/react";

interface RegularizationHistoryManagerProps {
  requests: AttendanceRequest[];
  teamMembers?: { id: string; name: string; department: string }[];
}

export function RegularizationHistoryManager({
  requests,
  teamMembers = [],
}: RegularizationHistoryManagerProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "pending" | "approved" | "rejected" | "cancelled" | "under-review">("all");
  const [dateRangeFilter, setDateRangeFilter] = useState<"all" | "this-month" | "last-month">("all");
  const [employeeFilter, setEmployeeFilter] = useState<string>("all");

  const teamMemberIds = useMemo(
    () => teamMembers.map((m) => m.id),
    [teamMembers]
  );

  const filteredRequests = useMemo(() => {
    let filtered = requests;

    // Only show requests from team members
    if (teamMemberIds.length > 0) {
      filtered = filtered.filter((r) => teamMemberIds.includes(r.employeeId));
    }

    // Filter by employee
    if (employeeFilter !== "all") {
      filtered = filtered.filter((r) => r.employeeId === employeeFilter);
    }

    // Filter by search term
    if (searchTerm.trim()) {
      const s = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (r) =>
          r.employeeName?.toLowerCase().includes(s) ||
          r.attendanceDate?.toLowerCase().includes(s) ||
          r.requestedStatus?.toLowerCase().includes(s) ||
          r.reason.toLowerCase().includes(s)
      );
    }

    // Filter by status
    if (statusFilter !== "all") {
      const statusMap: Record<string, string> = {
        pending: "Pending",
        approved: "Approved",
        rejected: "Rejected",
        cancelled: "Cancelled",
        "under-review": "Under Review",
      };
      filtered = filtered.filter((r) => r.status === statusMap[statusFilter]);
    }

    // Filter by date range
    if (dateRangeFilter !== "all") {
      const now = new Date(2026, 4, 12); // Mock today
      const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
      const lastMonthStart = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const lastMonthEnd = new Date(now.getFullYear(), now.getMonth(), 0);

      filtered = filtered.filter((r) => {
        const submitDate = r.submittedDate ? parseISO(r.submittedDate.split(" ")[0]) : new Date();
        if (dateRangeFilter === "this-month") {
          return submitDate >= monthStart && submitDate <= now;
        } else if (dateRangeFilter === "last-month") {
          return submitDate >= lastMonthStart && submitDate <= lastMonthEnd;
        }
        return true;
      });
    }

    return filtered.sort((a, b) => {
      const dateA = a.lastUpdated ? parseISO(a.lastUpdated.split(" ")[0]) : new Date();
      const dateB = b.lastUpdated ? parseISO(b.lastUpdated.split(" ")[0]) : new Date();
      return dateB.getTime() - dateA.getTime();
    });
  }, [requests, teamMemberIds, employeeFilter, searchTerm, statusFilter, dateRangeFilter]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "Approved":
        return <CheckCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />;
      case "Rejected":
        return <XCircle className="w-4 h-4 text-rose-600 dark:text-rose-400" />;
      case "Pending":
        return <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400" />;
      case "Under Review":
        return <Clock className="w-4 h-4 text-blue-600 dark:text-blue-400" />;
      default:
        return null;
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case "Approved":
        return "bg-emerald-100 text-emerald-700 border-emerald-300 dark:bg-emerald-500/15 dark:text-emerald-300 dark:border-emerald-500/30";
      case "Rejected":
        return "bg-rose-100 text-rose-700 border-rose-300 dark:bg-rose-500/15 dark:text-rose-300 dark:border-rose-500/30";
      case "Pending":
        return "bg-amber-100 text-amber-700 border-amber-300 dark:bg-amber-500/15 dark:text-amber-300 dark:border-amber-500/30";
      case "Under Review":
        return "bg-blue-100 text-blue-700 border-blue-300 dark:bg-blue-500/15 dark:text-blue-300 dark:border-blue-500/30";
      case "Cancelled":
        return "bg-slate-100 text-slate-700 border-slate-300 dark:bg-slate-500/15 dark:text-slate-300 dark:border-slate-500/30";
      default:
        return "bg-slate-100 text-slate-700 border-slate-300 dark:bg-slate-500/15 dark:text-slate-300 dark:border-slate-500/30";
    }
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col gap-3 p-3 bg-secondary/30 dark:bg-secondary/30 rounded-lg border border-border dark:border-border">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground dark:text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by employee, date, or reason…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-xs rounded-lg border border-border dark:border-slate-700 bg-background dark:bg-slate-900 text-foreground dark:text-white placeholder:text-muted-foreground dark:placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-ring dark:focus:ring-slate-500"
          />
        </div>

        {/* Filters Row */}
        <div className="flex flex-col sm:flex-row gap-2">
          {/* Employee Filter */}
          {teamMembers.length > 0 && (
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground dark:text-muted-foreground pointer-events-none" />
              <select
                value={employeeFilter}
                onChange={(e) => setEmployeeFilter(e.target.value)}
                className="pl-10 pr-3 py-2 text-xs rounded-lg border border-border dark:border-slate-700 bg-background dark:bg-slate-900 text-foreground dark:text-white focus:outline-none focus:ring-1 focus:ring-ring dark:focus:ring-slate-500 appearance-none cursor-pointer"
              >
                <option value="all">All Team Members</option>
                {teamMembers.map((member) => (
                  <option key={member.id} value={member.id}>
                    {member.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Status Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground dark:text-muted-foreground pointer-events-none" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="pl-10 pr-3 py-2 text-xs rounded-lg border border-border dark:border-slate-700 bg-background dark:bg-slate-900 text-foreground dark:text-white focus:outline-none focus:ring-1 focus:ring-ring dark:focus:ring-slate-500 appearance-none cursor-pointer"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="under-review">Under Review</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          {/* Date Range Filter */}
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground dark:text-muted-foreground pointer-events-none" />
            <select
              value={dateRangeFilter}
              onChange={(e) => setDateRangeFilter(e.target.value as any)}
              className="pl-10 pr-3 py-2 text-xs rounded-lg border border-border dark:border-slate-700 bg-background dark:bg-slate-900 text-foreground dark:text-white focus:outline-none focus:ring-1 focus:ring-ring dark:focus:ring-slate-500 appearance-none cursor-pointer"
            >
              <option value="all">All Dates</option>
              <option value="this-month">This Month</option>
              <option value="last-month">Last Month</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className="text-xs font-medium text-muted-foreground px-1">
        {filteredRequests.length} request{filteredRequests.length !== 1 ? "s" : ""}
      </div>

      {/* History List */}
      <div className="space-y-2">
        {filteredRequests.length > 0 ? (
          filteredRequests.map((request, index) => (
            <motion.div
              key={request.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="border border-border dark:border-slate-700 rounded-lg p-3 bg-card dark:bg-slate-800 hover:shadow-sm dark:hover:shadow-sm transition-shadow"
            >
              {/* Header Row */}
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-start gap-2 flex-1 min-w-0">
                  <div className="mt-0.5">{getStatusIcon(request.status)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <p className="text-xs font-semibold text-foreground dark:text-white">
                        {request.employeeName || "Unknown"}
                      </p>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-secondary/50 dark:bg-secondary/50 text-muted-foreground dark:text-slate-400">
                        {request.attendanceDate ? format(parseISO(request.attendanceDate), "MMM d") : "N/A"}
                      </span>
                      <span className="text-[10px] px-2 py-0.5 border rounded-full bg-secondary/50 dark:bg-secondary/50 text-foreground dark:text-white border-border dark:border-slate-600">
                        {request.requestedStatus}
                      </span>
                    </div>
                    <p className="text-[11px] text-muted-foreground dark:text-slate-400 line-clamp-2">
                      {request.reason}
                    </p>
                  </div>
                </div>
                <span className={`text-[10px] px-2 py-1 border rounded-md font-semibold whitespace-nowrap ${getStatusBadgeClass(request.status)}`}>
                  {request.status}
                </span>
              </div>

              {/* Details Row */}
              <div className="flex flex-col gap-2 text-[10px] text-muted-foreground dark:text-slate-400">
                <div className="flex items-center gap-4 flex-wrap">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3 opacity-60" />
                    <span>Submitted: {request.submittedDate ? format(parseISO(request.submittedDate), "MMM d, h:mm a") : "N/A"}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3 opacity-60" />
                    <span>Updated: {request.lastUpdated ? format(parseISO(request.lastUpdated), "MMM d, h:mm a") : "N/A"}</span>
                  </div>
                </div>

                {/* Approval Details */}
                {request.status === "Approved" && request.approvedBy && (
                  <div className="flex items-center gap-1 text-emerald-700 dark:text-emerald-300">
                    <User className="w-3 h-3" />
                    <span>Approved by {request.approvedBy} on {request.approvedDate ? format(parseISO(request.approvedDate), "MMM d, h:mm a") : "N/A"}</span>
                  </div>
                )}

                {/* Rejection Details */}
                {request.status === "Rejected" && request.rejectedBy && (
                  <div className="space-y-1">
                    <div className="flex items-center gap-1 text-rose-700 dark:text-rose-300">
                      <User className="w-3 h-3" />
                      <span>Rejected by {request.rejectedBy} on {request.rejectionDate ? format(parseISO(request.rejectionDate), "MMM d, h:mm a") : "N/A"}</span>
                    </div>
                    {request.rejectionReason && (
                      <div className="flex items-start gap-1 text-rose-600 dark:text-rose-400 ml-4">
                        <MessageCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                        <span className="line-clamp-2">{request.rejectionReason}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Pending/Under Review Note */}
                {(request.status === "Under Review" || request.status === "Pending") && (
                  <div className="flex items-center gap-1 text-blue-700 dark:text-blue-300">
                    <Clock className="w-3 h-3" />
                    <span>Awaiting approval</span>
                  </div>
                )}
              </div>
            </motion.div>
          ))
        ) : (
          <div className="text-center py-12">
            <div className="flex justify-center mb-3">
              <div className="p-3 bg-secondary/50 dark:bg-secondary/50 rounded-full">
                <Calendar className="w-5 h-5 text-muted-foreground dark:text-slate-400" />
              </div>
            </div>
            <p className="text-sm font-medium text-foreground dark:text-white">No regularization requests found</p>
            <p className="text-xs text-muted-foreground dark:text-slate-400 mt-1">Regularization requests from your team will appear here</p>
          </div>
        )}
      </div>
    </div>
  );
}
