"use client";

import { useMemo, useState } from "react";
import { Filter, Plus, X } from "lucide-react";
import { Button } from "../ui/button";
import { Drawer, DrawerClose, DrawerContent, DrawerDescription, DrawerFooter, DrawerHeader, DrawerTitle, DrawerTrigger } from "../ui/drawer";
import { Input } from "../ui/input";
import { cn } from "../ui/utils";
import type { AdvancedLeaveFilters } from "./constants";
import type { LeaveCategory, LeaveRequestStatus } from "../../modules/adminLeave/types";

export interface SavedView {
  id: string;
  name: string;
  query: string;
  category: LeaveCategory | "ALL";
  status: LeaveRequestStatus | "ALL";
  advancedFilters: AdvancedLeaveFilters;
}

interface AdvancedFilterDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  query: string;
  category: LeaveCategory | "ALL";
  status: LeaveRequestStatus | "ALL";
  advancedFilters: AdvancedLeaveFilters;
  onFilterChange: (key: keyof AdvancedLeaveFilters, value: string) => void;
  onReset: () => void;
  onSaveView: (name: string) => void;
  views: SavedView[];
  activeViewId: string | "ALL";
  onApplyView: (view: SavedView) => void;
  departmentOptions: string[];
  employeeOptions: string[];
  locationOptions: string[];
  businessUnitOptions: string[];
}

export function AdvancedFilterDrawer({
  open,
  onOpenChange,
  query,
  category,
  status,
  advancedFilters,
  onFilterChange,
  onReset,
  onSaveView,
  views,
  activeViewId,
  onApplyView,
  departmentOptions,
  employeeOptions,
  locationOptions,
  businessUnitOptions,
}: AdvancedFilterDrawerProps) {
  const [presetName, setPresetName] = useState("");

  const appliedPresets = useMemo(
    () => views.map((view) => ({ ...view, active: activeViewId === view.id })),
    [views, activeViewId],
  );

  const handleSavePreset = () => {
    const trimmed = presetName.trim();
    if (!trimmed) return;
    onSaveView(trimmed);
    setPresetName("");
  };

  const renderSelect = (
    label: string,
    value: string,
    options: string[],
    name: keyof AdvancedLeaveFilters,
  ) => (
    <label className="space-y-2 text-sm text-neutral-300">
      <span className="text-xs uppercase tracking-[0.2em] text-neutral-500">{label}</span>
      <select
        value={value}
        onChange={(event) => onFilterChange(name, event.target.value)}
        className="w-full rounded-xl border border-white/10 bg-neutral-950 px-3 py-2 text-sm text-white outline-none transition hover:border-white/20 focus:border-white/20"
      >
        {options.map((option) => (
          <option key={option} value={option} className="bg-neutral-950 text-white">
            {option === "ALL" ? `All ${label}` : option}
          </option>
        ))}
      </select>
    </label>
  );

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerTrigger asChild>
        <button
          type="button"
          className="inline-flex items-center rounded-xl border border-white/10 bg-neutral-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-neutral-900"
        >
          <Filter className="h-4 w-4" />
          Advanced Filters
        </button>
      </DrawerTrigger>
      <DrawerContent direction="right" className="max-w-[420px] bg-neutral-950 border-l border-white/10 text-white">
        <DrawerHeader>
          <div className="flex items-center justify-between gap-3">
            <div>
              <DrawerTitle>Advanced Filters</DrawerTitle>
              <DrawerDescription>Keep the top bar clean and refine results with enterprise fields.</DrawerDescription>
            </div>
            <DrawerClose asChild>
              <button className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-neutral-900 text-neutral-300 hover:bg-neutral-800">
                <X className="h-4 w-4" />
              </button>
            </DrawerClose>
          </div>
        </DrawerHeader>

        <div className="space-y-6 px-4 pb-4">
          <div className="rounded-3xl border border-white/10 bg-neutral-900 p-4 shadow-sm">
            <div className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="space-y-2 text-sm text-neutral-300">
                  <span className="text-xs uppercase tracking-[0.2em] text-neutral-500">Date from</span>
                  <Input
                    type="date"
                    value={advancedFilters.dateFrom}
                    onChange={(event) => onFilterChange("dateFrom", event.target.value)}
                    className="bg-neutral-950 border border-white/10 text-white placeholder:text-neutral-500 rounded-xl px-3 py-2"
                  />
                </label>
                <label className="space-y-2 text-sm text-neutral-300">
                  <span className="text-xs uppercase tracking-[0.2em] text-neutral-500">Date to</span>
                  <Input
                    type="date"
                    value={advancedFilters.dateTo}
                    onChange={(event) => onFilterChange("dateTo", event.target.value)}
                    className="bg-neutral-950 border border-white/10 text-white placeholder:text-neutral-500 rounded-xl px-3 py-2"
                  />
                </label>
              </div>

              {renderSelect("Department", advancedFilters.department, departmentOptions, "department")}
              {renderSelect("Employee", advancedFilters.employee, employeeOptions, "employee")}
              {renderSelect("Workflow Level", advancedFilters.workflowLevel, ["ALL", "1", "2", "3"], "workflowLevel")}
              {renderSelect("Payroll Lock", advancedFilters.payrollLock, ["ALL", "Unlocked", "Locked"], "payrollLock")}
              {renderSelect("Location", advancedFilters.location, locationOptions, "location")}
              {renderSelect("Business Unit", advancedFilters.businessUnit, businessUnitOptions, "businessUnit")}
              {renderSelect("Balance Impact", advancedFilters.balanceImpact, ["ALL", "POSITIVE", "NEUTRAL", "NEGATIVE"], "balanceImpact")}
              {renderSelect("Approval SLA", advancedFilters.approvalSla, ["ALL", "ON_TIME", "AT_RISK", "BREACHED"], "approvalSla")}
              {renderSelect("Escalation Status", advancedFilters.escalationStatus, ["ALL", "NONE", "PENDING", "ESCALATED"], "escalationStatus")}
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-neutral-900 p-4 shadow-sm">
            <div className="mb-3 flex items-center justify-between gap-2">
              <p className="text-sm font-semibold text-white">Saved filter presets</p>
              <span className="rounded-full bg-white/5 px-2 py-1 text-xs text-neutral-400">{views.length} saved</span>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className={cn(
                  "rounded-full border border-white/10 px-3 py-2 text-sm font-medium transition",
                  activeViewId === "ALL" ? "bg-white/10 text-white" : "text-neutral-300 hover:bg-white/5 hover:text-white",
                )}
                onClick={() => onApplyView({ id: "ALL", name: "All", query, category, status, advancedFilters })}
              >
                All
              </button>
              {views.map((view) => (
                <button
                  key={view.id}
                  type="button"
                  className={cn(
                    "rounded-full border border-white/10 px-3 py-2 text-sm font-medium transition",
                    activeViewId === view.id ? "bg-white/10 text-white" : "text-neutral-300 hover:bg-white/5 hover:text-white",
                  )}
                  onClick={() => onApplyView(view)}
                >
                  {view.name}
                </button>
              ))}
            </div>
            <div className="mt-4 flex items-center gap-2">
              <Input
                value={presetName}
                onChange={(event) => setPresetName(event.target.value)}
                placeholder="Preset name"
                className="bg-neutral-950 border border-white/10 text-white placeholder:text-neutral-500 rounded-xl px-3 py-2"
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="rounded-xl border border-white/10 bg-neutral-900 text-white hover:bg-neutral-800"
                onClick={handleSavePreset}
              >
                <Plus className="h-4 w-4" />
                Save
              </Button>
            </div>
          </div>
        </div>

        <DrawerFooter className="flex flex-col gap-3 px-4 pb-4">
          <Button
            variant="outline"
            className="rounded-xl border border-white/10 bg-neutral-900 text-white hover:bg-neutral-800"
            onClick={onReset}
          >
            Clear all filters
          </Button>
          <Button
            className="rounded-xl bg-white/10 text-white hover:bg-white/15"
            onClick={() => onOpenChange(false)}
          >
            Done
          </Button>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}
