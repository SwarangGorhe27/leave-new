import React, { useState } from 'react';
import {
  ArrowDownCircle,
  Banknote,
  Building2,
  CalendarDays,
  ChevronDown,
  ChevronRight,
  Download,
  Play,
  TrendingUp,
  Wallet,
  CheckCircle2,
  Send,
  Users,
} from 'lucide-react';
import { useMyPayslips, useMySalary, usePayrollRuns, useComputePayrollRun, useFinalizePayrollRun, usePublishPayslips } from '@hooks/usePayroll';
import type { PayrollRunAPI } from '@hooks/usePayroll';
import { Badge } from '@components/ui/Badge';
import { useUIStore } from '@store/uiStore';
import { cn } from '@utils/utils';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
interface LineItem {
  id: string;
  component_name: string;
  component_code: string;
  component_type: 'EARNING' | 'DEDUCTION' | 'EMPLOYER_CONTRIBUTION';
  final_amount: number;
}

interface Payslip {
  id: string;
  month: number;
  year: number;
  run_name: string;
  period_start: string;
  period_end: string;
  gross_earnings: number;
  total_deductions: number;
  net_pay: number;
  tax_deducted: number;
  paid_days: number;
  total_working_days: number;
  lop_days: number;
  payment_mode: string;
  is_published: boolean;
  line_items: LineItem[];
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function fmt(n: number) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);
}

/* ------------------------------------------------------------------ */
/*  Admin: Payroll Runs View                                           */
/* ------------------------------------------------------------------ */

const RUN_STATUS_VARIANT: Record<string, 'neutral' | 'warning' | 'info' | 'success'> = {
  DRAFT: 'neutral',
  COMPUTING: 'warning',
  COMPUTED: 'info',
  FINALIZED: 'info',
  PUBLISHED: 'success',
};

function AdminPayrollRunsView() {
  const { data: runs = [], isLoading } = usePayrollRuns();
  const computeMut = useComputePayrollRun();
  const finalizeMut = useFinalizePayrollRun();
  const publishMut = usePublishPayslips();

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-3 p-4">
        {[1, 2, 3].map((i) => <div key={i} className="h-24 rounded-xl bg-surface-200 dark:bg-white/10" />)}
      </div>
    );
  }

  if (!runs.length) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <Banknote className="h-10 w-10 text-surface-300 dark:text-white/20" />
        <p className="mt-3 text-sm text-surface-500 dark:text-white/40">No payroll runs found.</p>
        <p className="mt-1 text-xs text-surface-400 dark:text-white/25">Create a payroll run from the admin backend or CLI.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-surface-700 dark:text-white/80">Payroll Runs</h2>
        <span className="rounded-lg bg-surface-100 px-2 py-0.5 text-xs text-surface-500 dark:bg-white/5 dark:text-white/40">
          {runs.length} run{runs.length !== 1 ? 's' : ''}
        </span>
      </div>

      {(runs as PayrollRunAPI[]).map((run) => (
        <div
          key={run.id}
          className="rounded-xl border border-surface-200/70 bg-surface-0 p-4 shadow-xs dark:border-white/10 dark:bg-white/[0.03]"
        >
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <p className="font-semibold text-surface-900 dark:text-white">{run.name}</p>
                <Badge variant={RUN_STATUS_VARIANT[run.status] ?? 'neutral'} size="sm">
                  {run.status}
                </Badge>
              </div>
              <p className="mt-0.5 text-xs text-surface-500 dark:text-white/40">
                {new Date(run.period_start).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                {' – '}
                {new Date(run.period_end).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                {' · '}{run.run_type}
              </p>
            </div>
            <div className="flex items-center gap-3 text-right">
              <div>
                <p className="text-xs text-surface-400 dark:text-white/30">Employees</p>
                <p className="flex items-center gap-1 text-sm font-semibold text-surface-900 dark:text-white">
                  <Users className="h-3.5 w-3.5 text-surface-400" /> {run.total_employees}
                </p>
              </div>
              <div>
                <p className="text-xs text-surface-400 dark:text-white/30">Gross</p>
                <p className="text-sm font-semibold text-surface-900 dark:text-white">{fmt(Number(run.total_gross))}</p>
              </div>
              <div>
                <p className="text-xs text-surface-400 dark:text-white/30">Net</p>
                <p className="text-sm font-bold text-emerald-600 dark:text-emerald-400">{fmt(Number(run.total_net))}</p>
              </div>
            </div>
          </div>

          {/* Action buttons based on status */}
          <div className="mt-3 flex flex-wrap gap-2 border-t border-surface-100 pt-3 dark:border-white/5">
            {run.status === 'DRAFT' && (
              <button
                type="button"
                disabled={computeMut.isPending}
                onClick={() => computeMut.mutate(run.id)}
                className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-brand-700 disabled:opacity-50"
              >
                <Play className="h-3.5 w-3.5" /> Compute Payroll
              </button>
            )}
            {run.status === 'COMPUTED' && (
              <button
                type="button"
                disabled={finalizeMut.isPending}
                onClick={() => finalizeMut.mutate(run.id)}
                className="flex items-center gap-1.5 rounded-lg bg-amber-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-700 disabled:opacity-50"
              >
                <CheckCircle2 className="h-3.5 w-3.5" /> Finalize Run
              </button>
            )}
            {run.status === 'FINALIZED' && (
              <button
                type="button"
                disabled={publishMut.isPending}
                onClick={() => publishMut.mutate(run.id)}
                className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                <Send className="h-3.5 w-3.5" /> Publish Payslips
              </button>
            )}
            {run.status === 'PUBLISHED' && (
              <span className="flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" /> Payslips published
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Payslip Card                                                       */
/* ------------------------------------------------------------------ */
function PayslipCard({ slip, isOpen, onToggle }: { slip: Payslip; isOpen: boolean; onToggle: () => void }) {
  const earnings = slip.line_items.filter((l) => l.component_type === 'EARNING');
  const deductions = slip.line_items.filter((l) => l.component_type === 'DEDUCTION');

  return (
    <div className="rounded-2xl border border-surface-200/70 bg-surface-0 shadow-xs dark:border-white/10 dark:bg-white/5">
      {/* Header row */}
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between rounded-2xl px-5 py-4 text-left hover:bg-surface-50/60 dark:hover:bg-white/5"
      >
        <div className="flex items-center gap-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-400">
            <Banknote className="h-5 w-5" />
          </div>
          <div>
            <p className="font-semibold text-surface-900 dark:text-white">
              {MONTHS[slip.month - 1]} {slip.year}
            </p>
            <p className="text-xs text-surface-500 dark:text-white/45">{slip.run_name}</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="hidden text-right sm:block">
            <p className="text-xs text-surface-500 dark:text-white/40">Gross</p>
            <p className="text-sm font-medium text-surface-800 dark:text-white/80">{fmt(slip.gross_earnings)}</p>
          </div>
          <div className="hidden text-right sm:block">
            <p className="text-xs text-surface-500 dark:text-white/40">Deductions</p>
            <p className="text-sm font-medium text-red-600 dark:text-red-400">-{fmt(slip.total_deductions)}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-surface-500 dark:text-white/40">Net Pay</p>
            <p className="text-base font-bold text-emerald-600 dark:text-emerald-400">{fmt(slip.net_pay)}</p>
          </div>
          <Badge variant={slip.is_published ? 'success' : 'warning'}>
            {slip.is_published ? 'Published' : 'Draft'}
          </Badge>
          {isOpen ? (
            <ChevronDown className="h-4 w-4 text-surface-400 dark:text-white/30" />
          ) : (
            <ChevronRight className="h-4 w-4 text-surface-400 dark:text-white/30" />
          )}
        </div>
      </button>

      {/* Expanded detail */}
      {isOpen && (
        <div className="border-t border-surface-200/70 px-5 py-4 dark:border-white/10">
          {/* Summary row */}
          <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              { label: 'Paid Days', value: `${slip.paid_days} / ${slip.total_working_days}` },
              { label: 'LOP Days', value: String(slip.lop_days) },
              { label: 'TDS', value: fmt(slip.tax_deducted) },
              { label: 'Payment Mode', value: slip.payment_mode.replace(/_/g, ' ') },
            ].map((s) => (
              <div key={s.label} className="rounded-xl bg-surface-50 px-3 py-2.5 dark:bg-white/5">
                <p className="text-2xs uppercase tracking-wider text-surface-400 dark:text-white/35">{s.label}</p>
                <p className="mt-0.5 text-sm font-medium text-surface-800 dark:text-white/80">{s.value}</p>
              </div>
            ))}
          </div>

          {/* Earnings & Deductions table */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {/* Earnings */}
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                Earnings
              </p>
              <table className="w-full text-sm">
                <tbody>
                  {earnings.map((e) => (
                    <tr key={e.id} className="border-b border-surface-100 dark:border-white/5">
                      <td className="py-1.5 text-surface-700 dark:text-white/70">{e.component_name}</td>
                      <td className="py-1.5 text-right font-medium text-surface-900 dark:text-white">{fmt(e.final_amount)}</td>
                    </tr>
                  ))}
                  <tr className="border-t-2 border-surface-200 dark:border-white/10">
                    <td className="py-2 font-semibold text-surface-900 dark:text-white">Total Earnings</td>
                    <td className="py-2 text-right font-bold text-emerald-600 dark:text-emerald-400">{fmt(slip.gross_earnings)}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Deductions */}
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-red-500 dark:text-red-400">
                Deductions
              </p>
              <table className="w-full text-sm">
                <tbody>
                  {deductions.map((d) => (
                    <tr key={d.id} className="border-b border-surface-100 dark:border-white/5">
                      <td className="py-1.5 text-surface-700 dark:text-white/70">{d.component_name}</td>
                      <td className="py-1.5 text-right font-medium text-red-600 dark:text-red-400">-{fmt(d.final_amount)}</td>
                    </tr>
                  ))}
                  <tr className="border-t-2 border-surface-200 dark:border-white/10">
                    <td className="py-2 font-semibold text-surface-900 dark:text-white">Total Deductions</td>
                    <td className="py-2 text-right font-bold text-red-600 dark:text-red-400">-{fmt(slip.total_deductions)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Net Pay banner */}
          <div className="mt-4 flex items-center justify-between rounded-xl bg-emerald-50 px-4 py-3 dark:bg-emerald-900/20">
            <span className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">Net Pay</span>
            <span className="text-xl font-bold text-emerald-700 dark:text-emerald-300">{fmt(slip.net_pay)}</span>
          </div>
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Salary Structure tab                                               */
/* ------------------------------------------------------------------ */
function SalaryStructureTab() {
  const { data: salary, isLoading } = useMySalary();

  if (isLoading) {
    return (
      <div className="space-y-3 p-1">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 animate-pulse rounded-xl bg-surface-100 dark:bg-white/5" />
        ))}
      </div>
    );
  }

  if (!salary) {
    return (
      <div className="py-12 text-center text-sm text-surface-500 dark:text-white/40">
        No salary record found.
      </div>
    );
  }

  type SalaryComp = { id: string; component_detail: { name: string; component_type: string }; monthly_amount: number; annual_amount: number };
  const comps = (salary.components as SalaryComp[] | undefined) ?? [];
  const earnings = comps.filter((c) => c.component_detail?.component_type === 'EARNING');
  const deductions = comps.filter((c) => c.component_detail?.component_type === 'DEDUCTION');

  return (
    <div className="space-y-4 p-1">
      {/* CTC Summary */}
      <div className="grid grid-cols-3 gap-3">
        {([
          { label: 'Annual CTC', value: fmt(Number(salary.ctc)), icon: <TrendingUp className="h-5 w-5" />, color: 'text-brand-600 bg-brand-50 dark:bg-brand-900/30 dark:text-brand-400' },
          { label: 'Monthly Gross', value: fmt(Number(salary.gross)), icon: <Wallet className="h-5 w-5" />, color: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/30 dark:text-emerald-400' },
          { label: 'Monthly Net', value: fmt(Number(salary.net)), icon: <Building2 className="h-5 w-5" />, color: 'text-blue-600 bg-blue-50 dark:bg-blue-900/30 dark:text-blue-400' },
        ] as { label: string; value: string; icon: React.ReactNode; color: string }[]).map((s) => (
          <div key={s.label} className="flex items-center gap-3 rounded-2xl border border-surface-200/70 bg-surface-0 px-4 py-3.5 dark:border-white/10 dark:bg-white/5">
            <span className={cn('flex h-9 w-9 items-center justify-center rounded-xl', s.color)}>{s.icon}</span>
            <div>
              <p className="text-xs text-surface-500 dark:text-white/40">{s.label}</p>
              <p className="text-base font-bold text-surface-900 dark:text-white">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Effective date */}
      <div className="flex items-center gap-2 text-xs text-surface-500 dark:text-white/40">
        <CalendarDays className="h-3.5 w-3.5" />
        <span>Effective from {String(salary.effective_from ?? '')}</span>
        <span className="ml-2 rounded-lg border border-surface-200 px-2 py-0.5 dark:border-white/10">{String(salary.structure_name ?? 'Standard CTC')}</span>
      </div>

      {/* Breakdown */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">Earnings</p>
          <div className="overflow-hidden rounded-xl border border-surface-200/70 dark:border-white/10">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-200/70 bg-surface-50 dark:border-white/10 dark:bg-white/5">
                  <th className="px-3 py-2 text-left text-xs font-medium text-surface-600 dark:text-white/50">Component</th>
                  <th className="px-3 py-2 text-right text-xs font-medium text-surface-600 dark:text-white/50">Monthly</th>
                  <th className="px-3 py-2 text-right text-xs font-medium text-surface-600 dark:text-white/50">Annual</th>
                </tr>
              </thead>
              <tbody>
                {earnings.map((c) => (
                  <tr key={c.id} className="border-b border-surface-100 last:border-0 dark:border-white/5">
                    <td className="px-3 py-2 text-surface-700 dark:text-white/70">{c.component_detail?.name}</td>
                    <td className="px-3 py-2 text-right font-medium text-surface-900 dark:text-white">{fmt(Number(c.monthly_amount))}</td>
                    <td className="px-3 py-2 text-right text-surface-600 dark:text-white/50">{fmt(Number(c.annual_amount))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-red-500 dark:text-red-400">Deductions</p>
          <div className="overflow-hidden rounded-xl border border-surface-200/70 dark:border-white/10">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-200/70 bg-surface-50 dark:border-white/10 dark:bg-white/5">
                  <th className="px-3 py-2 text-left text-xs font-medium text-surface-600 dark:text-white/50">Component</th>
                  <th className="px-3 py-2 text-right text-xs font-medium text-surface-600 dark:text-white/50">Monthly</th>
                  <th className="px-3 py-2 text-right text-xs font-medium text-surface-600 dark:text-white/50">Annual</th>
                </tr>
              </thead>
              <tbody>
                {deductions.map((c) => (
                  <tr key={c.id} className="border-b border-surface-100 last:border-0 dark:border-white/5">
                    <td className="px-3 py-2 text-surface-700 dark:text-white/70">{c.component_detail?.name}</td>
                    <td className="px-3 py-2 text-right font-medium text-red-600 dark:text-red-400">-{fmt(Number(c.monthly_amount))}</td>
                    <td className="px-3 py-2 text-right text-red-500 dark:text-red-400/70">-{fmt(Number(c.annual_amount))}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Payslips tab                                                       */
/* ------------------------------------------------------------------ */
function PayslipsTab() {
  const { data: payslips = [], isLoading } = useMyPayslips();
  const [openId, setOpenId] = useState<string | null>(null);
  const typedSlips = payslips as unknown as Payslip[];

  if (isLoading) {
    return (
      <div className="space-y-3 p-1">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-20 animate-pulse rounded-2xl bg-surface-100 dark:bg-white/5" />
        ))}
      </div>
    );
  }

  if (!typedSlips.length) {
    return (
      <div className="flex flex-col items-center py-16 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-surface-100 dark:bg-white/5">
          <ArrowDownCircle className="h-6 w-6 text-surface-400 dark:text-white/25" />
        </div>
        <p className="mt-4 text-sm font-medium text-surface-700 dark:text-white/60">No payslips available</p>
        <p className="mt-1 text-xs text-surface-400 dark:text-white/30">Payslips will appear once payroll is processed.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3 p-1">
      {/* Download hint */}
      <div className="flex items-center justify-between rounded-xl bg-brand-50/60 px-3 py-2 text-xs text-brand-700 dark:bg-brand-900/20 dark:text-brand-400">
        <span>Showing {typedSlips.length} published payslip{typedSlips.length !== 1 ? 's' : ''}</span>
        <Download className="h-3.5 w-3.5" />
      </div>

      {typedSlips.map((slip) => (
        <PayslipCard
          key={slip.id}
          slip={slip}
          isOpen={openId === slip.id}
          onToggle={() => setOpenId(openId === slip.id ? null : slip.id)}
        />
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main export                                                        */
/* ------------------------------------------------------------------ */
type Tab = 'payslips' | 'salary' | 'runs';

export function PayrollPanel() {
  const portal = useUIStore((s) => s.portal);
  const activeModule = useUIStore((s) => s.activeModule);
  const rawModuleView = useUIStore((s) => s.moduleViews[activeModule] ?? 'employee');
  const isAdminView = portal === 'hrms' && rawModuleView === 'admin';

  const [tab, setTab] = useState<Tab>(isAdminView ? 'runs' : 'payslips');

  const tabs: { key: Tab; label: string; adminOnly?: boolean }[] = [
    { key: 'payslips', label: 'My Payslips' },
    { key: 'salary', label: 'Salary Structure' },
    ...(isAdminView ? [{ key: 'runs' as Tab, label: 'Payroll Runs', adminOnly: true }] : []),
  ];

  // Reset tab if view changes
  const visibleKeys = tabs.map((t) => t.key);
  const activeTab = visibleKeys.includes(tab) ? tab : visibleKeys[0];

  return (
    <div className="space-y-5 p-1">
      {/* Tab bar */}
      <div className="flex gap-1 rounded-xl border border-surface-200/70 bg-surface-50 p-1 dark:border-white/10 dark:bg-white/5">
        {tabs.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setTab(t.key)}
            className={cn(
              'flex-1 rounded-lg px-4 py-2 text-sm font-medium transition-colors',
              activeTab === t.key
                ? 'bg-surface-0 text-surface-900 shadow-sm dark:bg-white/10 dark:text-white'
                : 'text-surface-500 hover:text-surface-800 dark:text-white/40 dark:hover:text-white/70',
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === 'runs' && <AdminPayrollRunsView />}
      {activeTab === 'payslips' && <PayslipsTab />}
      {activeTab === 'salary' && <SalaryStructureTab />}
    </div>
  );
}
