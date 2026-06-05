import { useMemo, useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router";
import { Search, Settings2 } from "lucide-react";
import { MASTER_CATEGORIES, getMasterConfig } from "../../../modules/masters/config";
import { Input } from "../../../components/ui/input";
import { MasterTable } from "./MasterTable";
import { cn } from "../../../components/ui/utils";

export function MasterLayout() {
  const navigate = useNavigate();
  const { category = "", masterName = "" } = useParams();
  const [masterSearch, setMasterSearch] = useState("");

  const currentCategory = MASTER_CATEGORIES.find((c) => c.key === category);
  const fallbackCategory = MASTER_CATEGORIES[0];
  const fallbackMaster = fallbackCategory?.masters[0];
  const isValidMaster = Boolean(currentCategory && getMasterConfig(category, masterName));

  const categoryButtons = useMemo(
    () =>
      MASTER_CATEGORIES.map((c) => (
        <button
          key={c.key}
          type="button"
          className={cn(
            "rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors",
            c.key === category
              ? "border-border bg-secondary text-foreground"
              : "border-transparent text-muted-foreground hover:border-border hover:bg-secondary/60 hover:text-foreground",
          )}
          onClick={() => navigate(`/superadmin/masters/${c.key}/${c.masters[0]?.key}`)}
        >
          {c.label}
        </button>
      )),
    [category, navigate],
  );

  if (!fallbackCategory || !fallbackMaster) {
    return <div className="p-6">No masters configured.</div>;
  }

  if (!isValidMaster) {
    return (
      <Navigate
        to={`/superadmin/masters/${fallbackCategory.key}/${fallbackMaster.key}`}
        replace
      />
    );
  }

  const selectedConfig = getMasterConfig(category, masterName)!;

  const normalizedMasterSearch = masterSearch.trim().toLowerCase();
  const filteredMasters = normalizedMasterSearch
    ? currentCategory.masters.filter((m) =>
        `${m.label} ${m.apiName} ${m.key}`.toLowerCase().includes(normalizedMasterSearch),
      )
    : currentCategory.masters;

  return (
    <div className="p-6 space-y-4">
      <div className="rounded-xl border border-white/10 bg-[#0f2744] p-4 text-neutral-100 shadow-xl">
        <div className="flex items-center gap-2">
          <Settings2 className="h-4 w-4" />
          <h1 className="text-lg font-semibold tracking-tight">Masters Management</h1>
        </div>
        <p className="mt-1 text-xs text-neutral-400">
          Super Admin console for configuration masters across HRMS domains.
        </p>
      </div>

      <div className="flat-card bg-card p-3">
        <div className="flex flex-wrap gap-2">{categoryButtons}</div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="flat-card bg-card p-3">
          <p className="mb-2 px-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            {currentCategory.label}
          </p>
          <div className="relative mb-3">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground dark:text-muted-foreground" />
            <Input
              value={masterSearch}
              onChange={(event) => setMasterSearch(event.target.value)}
              className="h-9 pl-8 text-sm"
              placeholder="Search masters"
            />
          </div>
          <nav className="space-y-1">
            {filteredMasters.length === 0 ? (
              <div className="rounded-lg border border-dashed border-border px-2.5 py-3 text-xs text-muted-foreground">
                No masters found.
              </div>
            ) : filteredMasters.map((m) => {
              const active = m.key === masterName;
              return (
                <button
                  key={m.key}
                  type="button"
                  className={cn(
                    "w-full rounded-lg border px-2.5 py-2 text-left text-xs font-medium transition-colors",
                    active
                      ? "border-border bg-secondary text-foreground"
                      : "border-transparent text-muted-foreground hover:border-border hover:bg-secondary/50 hover:text-foreground",
                  )}
                  onClick={() => navigate(`/superadmin/masters/${currentCategory.key}/${m.key}`)}
                >
                  {m.label}
                </button>
              );
            })}
          </nav>
        </aside>

        <MasterTable config={selectedConfig} />
      </div>
    </div>
  );
}
