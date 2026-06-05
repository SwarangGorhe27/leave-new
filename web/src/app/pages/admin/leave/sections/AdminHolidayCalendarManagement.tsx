import { useEffect, useMemo, useState } from "react";
import { CalendarDays, Plus, X } from "lucide-react";
import { cn } from "../../../../components/ui/utils";
import { HolidayCalendarView } from "../../../../components/leaves/HolidayCalendarView";
import { useAdminLeaveHolidays, useCreateAdminHoliday } from "../../../../modules/adminLeave/useAdminLeave";
import { getMasterList } from "../../../../modules/masters/api";

const HOLIDAY_TYPES = [
  { value: "NATIONAL", label: "National" },
  { value: "RESTRICTED", label: "Restricted" },
  { value: "OPTIONAL", label: "Optional" },
  { value: "COMPANY", label: "Company" },
] as const;

type BranchOption = { id: string; label: string };

function AddHolidayModal({
  year,
  onClose,
  onSuccess,
}: {
  year: number;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const createHoliday = useCreateAdminHoliday(year);
  const [branches, setBranches] = useState<BranchOption[]>([]);
  const [loadingBranches, setLoadingBranches] = useState(true);
  const [date, setDate] = useState("");
  const [name, setName] = useState("");
  const [type, setType] = useState<(typeof HOLIDAY_TYPES)[number]["value"]>("NATIONAL");
  const [branchIds, setBranchIds] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const response = await getMasterList("Branch", { is_active: true, page: 1, page_size: 200 });
        if (cancelled) return;
        const options = response.results.map((branch) => ({
          id: String(branch.id),
          label: String(branch.name ?? branch.label ?? branch.code ?? branch.id),
        }));
        setBranches(options);
        if (options.length === 1) {
          setBranchIds([options[0].id]);
        }
      } catch {
        if (!cancelled) setError("Failed to load branches.");
      } finally {
        if (!cancelled) setLoadingBranches(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const toggleBranch = (branchId: string) => {
    setBranchIds((current) =>
      current.includes(branchId)
        ? current.filter((id) => id !== branchId)
        : [...current, branchId],
    );
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    if (!date || !name.trim()) {
      setError("Date and name are required.");
      return;
    }
    if (branchIds.length === 0) {
      setError("Select at least one branch.");
      return;
    }

    try {
      await createHoliday.mutateAsync({
        date,
        name: name.trim(),
        type,
        branch_ids: branchIds,
      });
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { branch_ids?: string[]; detail?: string } } })?.response?.data
          ?.branch_ids?.[0] ??
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Failed to add holiday.";
      setError(String(message));
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div
        className="relative bg-background border border-border rounded-xl shadow-xl w-[92vw] max-w-lg overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="border-b border-border bg-card px-5 py-4 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold text-foreground">Add Holiday</h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Add a holiday to the {year} calendar for selected branches.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-9 h-9 flex items-center justify-center rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          <div>
            <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
              Holiday Name
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Republic Day"
              className="flat-input h-10 px-3 text-sm w-full"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
                Date
              </label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                min={`${year}-01-01`}
                max={`${year}-12-31`}
                className="flat-input h-10 px-3 text-sm w-full"
                required
              />
            </div>
            <div>
              <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
                Type
              </label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value as typeof type)}
                className="flat-input h-10 px-3 text-sm w-full"
              >
                {HOLIDAY_TYPES.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
              Branches
            </label>
            {loadingBranches ? (
              <p className="text-xs text-muted-foreground">Loading branches…</p>
            ) : branches.length === 0 ? (
              <p className="text-xs text-rose-600">No active branches found. Create a branch in HR Setup first.</p>
            ) : (
              <div className="max-h-40 overflow-y-auto rounded-lg border border-border divide-y divide-border">
                {branches.map((branch) => (
                  <label
                    key={branch.id}
                    className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-secondary/50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={branchIds.includes(branch.id)}
                      onChange={() => toggleBranch(branch.id)}
                      className="h-4 w-4 rounded border-border"
                    />
                    <span>{branch.label}</span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {error && <p className="text-xs text-rose-600 font-medium">{error}</p>}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg border border-border text-sm font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createHoliday.isPending || loadingBranches || branches.length === 0}
              className="px-4 py-2 rounded-lg bg-foreground text-primary-foreground text-sm font-semibold disabled:opacity-40"
            >
              {createHoliday.isPending ? "Saving…" : "Add Holiday"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export function AdminHolidayCalendarManagement() {
  const [view, setView] = useState<"list" | "calendar">("calendar");
  const [showAddModal, setShowAddModal] = useState(false);
  const year = new Date().getFullYear();
  const holidaysQ = useAdminLeaveHolidays(year);

  const holidays = useMemo(() => {
    return (holidaysQ.data ?? []).map((holiday) => ({
      id: holiday.id,
      name: holiday.name,
      date: holiday.holiday_date,
      holiday_type: holiday.holiday_type,
      is_optional: holiday.holiday_type === "OPTIONAL",
    }));
  }, [holidaysQ.data]);

  const stats = useMemo(() => {
    const total = holidays.length;
    const optional = holidays.filter((h) => h.is_optional).length;
    return { total, optional };
  }, [holidays]);

  if (holidaysQ.error) {
    return (
      <div className="flat-card bg-card p-6 text-center">
        <p className="text-sm text-rose-600 font-semibold">Failed to load holidays</p>
        <p className="text-xs text-muted-foreground mt-1">{String(holidaysQ.error)}</p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flat-card bg-card p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-semibold text-foreground flex items-center gap-2">
              <CalendarDays className="w-4 h-4 text-muted-foreground" />
              Holiday Calendar Management
            </h2>
            <p className="text-sm text-muted-foreground mt-1">
              Configure year holidays, optional holidays, and calendar publishing.
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="text-[11px] font-semibold text-muted-foreground bg-secondary border border-border px-2 py-0.5 rounded-md">
                Year: {year}
              </span>
              <span className="text-[11px] font-semibold text-muted-foreground bg-secondary border border-border px-2 py-0.5 rounded-md">
                Total: {stats.total}
              </span>
              <span className="text-[11px] font-semibold text-muted-foreground bg-secondary border border-border px-2 py-0.5 rounded-md">
                Optional: {stats.optional}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              className="px-3 py-2 rounded-lg text-xs font-semibold bg-secondary border border-border text-foreground hover:bg-background transition-colors"
              onClick={() => setView((v) => (v === "calendar" ? "list" : "calendar"))}
            >
              {view === "calendar" ? "List view" : "Calendar view"}
            </button>
            <button
              type="button"
              className="px-3 py-2 rounded-lg text-xs font-semibold bg-foreground text-primary-foreground hover:bg-accent transition-colors inline-flex items-center gap-2"
              onClick={() => setShowAddModal(true)}
            >
              <Plus className="w-4 h-4" />
              Add Holiday
            </button>
          </div>
        </div>
      </div>

      {view === "calendar" ? (
        <HolidayCalendarView holidays={holidays} initialYear={year} />
      ) : (
        <div className="flat-card bg-card overflow-hidden">
          <div className="px-6 py-4 border-b border-border flex items-center justify-between">
            <p className="text-sm font-semibold text-foreground">Yearly List</p>
            <span className="text-[11px] font-semibold text-muted-foreground bg-secondary border border-border px-2 py-0.5 rounded-md">
              {holidays.length}
            </span>
          </div>
          <div className="divide-y divide-border">
            {holidays
              .slice()
              .sort((a, b) => a.date.localeCompare(b.date))
              .map((h) => (
                <div key={h.id} className="px-6 py-4 flex items-center justify-between gap-4 hover:bg-secondary transition-colors">
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-foreground truncate">{h.name}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{h.holiday_type} · {h.date}</p>
                  </div>
                  <span className={cn(
                    "text-[11px] font-semibold px-2 py-0.5 rounded-md border",
                    h.is_optional ? "bg-secondary text-muted-foreground border-border" : "bg-foreground text-primary-foreground border-border",
                  )}>
                    {h.is_optional ? "Optional" : "Mandatory"}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}

      {showAddModal && (
        <AddHolidayModal
          year={year}
          onClose={() => setShowAddModal(false)}
          onSuccess={() => holidaysQ.refetch()}
        />
      )}
    </div>
  );
}
