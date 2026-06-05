import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@api/client';

const RUNS_KEY = 'hrms-demo-payroll-runs';

const DEMO_RUNS: PayrollRunAPI[] = [
  {
    id: 'run-1',
    name: 'Apr 2026 Payroll',
    run_type: 'REGULAR',
    period_start: '2026-04-01',
    period_end: '2026-04-30',
    status: 'COMPUTED',
    total_employees: 128,
    total_gross: 11850000,
    total_net: 9624000,
    created_at: '2026-04-28T10:00:00Z',
  },
  {
    id: 'run-2',
    name: 'May 2026 Payroll',
    run_type: 'REGULAR',
    period_start: '2026-05-01',
    period_end: '2026-05-31',
    status: 'DRAFT',
    total_employees: 132,
    total_gross: 0,
    total_net: 0,
    created_at: '2026-05-01T09:00:00Z',
  },
];

function readRuns(): PayrollRunAPI[] {
  const raw = localStorage.getItem(RUNS_KEY);
  if (raw) {
    try {
      return JSON.parse(raw) as PayrollRunAPI[];
    } catch {
      // fallback to seed
    }
  }
  localStorage.setItem(RUNS_KEY, JSON.stringify(DEMO_RUNS));
  return DEMO_RUNS;
}

function writeRuns(runs: PayrollRunAPI[]) {
  localStorage.setItem(RUNS_KEY, JSON.stringify(runs));
}

function extract<T>(res: unknown): T[] {
  const d = res as Record<string, unknown>;
  return (d?.data as Record<string, unknown>)?.results as T[]
    ?? (d?.data as Record<string, unknown>)?.data as T[]
    ?? d?.data as T[]
    ?? d?.results as T[]
    ?? (Array.isArray(d) ? d : []) as T[];
}

function extractOne<T>(res: unknown): T {
  const d = res as Record<string, unknown>;
  return ((d?.data as Record<string, unknown>)?.data ?? d?.data ?? d) as T;
}

export function useMyPayslips() {
  return useQuery({
    queryKey: ['me', 'payslips'],
    queryFn: async () => {
      try {
        const res = await api.get('/me/payslips/');
        const rows = extract<Record<string, unknown>>(res);
        if (rows.length) return rows;
      } catch {
        // fallback
      }
      // Demo payslips for last 6 months
      const payslips = [];
      const today = new Date();
      for (let i = 0; i < 6; i++) {
        const d = new Date(today.getFullYear(), today.getMonth() - i - 1, 1);
        const year = d.getFullYear();
        const month = d.getMonth() + 1;
        const monthName = d.toLocaleString('en-IN', { month: 'long' });
        const paidDays = month === 1 ? 22 : 26;
        const gross = 100000;
        const pf = 4800;
        const tds = 9000;
        const net = gross - pf - tds;
        payslips.push({
          id: `payslip-${year}-${String(month).padStart(2, '0')}`,
          month,
          year,
          run_name: `${monthName} ${year} Payroll`,
          period_start: `${year}-${String(month).padStart(2, '0')}-01`,
          period_end: `${year}-${String(month).padStart(2, '0')}-${new Date(year, month, 0).getDate()}`,
          gross_earnings: gross,
          total_deductions: pf + tds,
          net_pay: net,
          tax_deducted: tds,
          paid_days: paidDays,
          total_working_days: 26,
          lop_days: 0,
          payment_mode: 'BANK_TRANSFER',
          is_published: true,
          line_items: [
            { id: `li-1-${month}`, component_name: 'Basic Salary', component_code: 'BASIC', component_type: 'EARNING', final_amount: 40000 },
            { id: `li-2-${month}`, component_name: 'House Rent Allowance', component_code: 'HRA', component_type: 'EARNING', final_amount: 16000 },
            { id: `li-3-${month}`, component_name: 'Special Allowance', component_code: 'SA', component_type: 'EARNING', final_amount: 44000 },
            { id: `li-4-${month}`, component_name: 'PF Employee', component_code: 'PF_EE', component_type: 'DEDUCTION', final_amount: pf },
            { id: `li-5-${month}`, component_name: 'TDS', component_code: 'TDS', component_type: 'DEDUCTION', final_amount: tds },
          ],
        });
      }
      return payslips as unknown as Record<string, unknown>[];
    },
  });
}

export function useMySalary() {
  return useQuery({
    queryKey: ['me', 'salary'],
    queryFn: async () => {
      try {
        const res = await api.get('/me/salary/');
        return extractOne<Record<string, unknown>>(res);
      } catch {
        return {
          ctc: 1200000,
          gross: 100000,
          net: 81200,
          effective_from: '2026-04-01',
          structure_name: 'SS-STAFF-001',
          components: [
            { id: '1', component_detail: { name: 'Basic Salary', component_type: 'EARNING' }, monthly_amount: 40000, annual_amount: 480000 },
            { id: '2', component_detail: { name: 'House Rent Allowance', component_type: 'EARNING' }, monthly_amount: 16000, annual_amount: 192000 },
            { id: '3', component_detail: { name: 'Special Allowance', component_type: 'EARNING' }, monthly_amount: 44000, annual_amount: 528000 },
            { id: '4', component_detail: { name: 'PF Employee', component_type: 'DEDUCTION' }, monthly_amount: 4800, annual_amount: 57600 },
            { id: '5', component_detail: { name: 'TDS', component_type: 'DEDUCTION' }, monthly_amount: 9000, annual_amount: 108000 },
          ],
        };
      }
    },
  });
}

/* ------------------------------------------------------------------ */
/*  Admin hooks (HRMS portal)                                          */
/* ------------------------------------------------------------------ */

export interface PayrollRunAPI {
  id: string;
  name: string;
  run_type: string;
  period_start: string;
  period_end: string;
  status: 'DRAFT' | 'COMPUTING' | 'COMPUTED' | 'FINALIZED' | 'PUBLISHED';
  total_employees: number;
  total_gross: string | number;
  total_net: string | number;
  created_at: string;
}

export function usePayrollRuns() {
  return useQuery({
    queryKey: ['payroll-runs'],
    queryFn: async () => {
      try {
        const res = await api.get('/payroll/runs/');
        const rows = extract<PayrollRunAPI>(res);
        if (rows.length) {
          writeRuns(rows);
          return rows;
        }
      } catch {
        // fallback
      }
      return readRuns();
    },
    staleTime: 60_000,
  });
}

export function useComputePayrollRun() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        const res = await api.post(`/payroll/runs/${id}/compute/`);
        return res.data;
      } catch {
        const updated = readRuns().map((run) => (
          run.id === id
            ? {
                ...run,
                status: 'COMPUTED' as const,
                total_gross: Number(run.total_gross) || run.total_employees * 90000,
                total_net: Number(run.total_net) || run.total_employees * 73000,
              }
            : run
        ));
        writeRuns(updated);
        return updated.find((run) => run.id === id);
      }
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['payroll-runs'] }),
  });
}

export function useFinalizePayrollRun() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        const res = await api.post(`/payroll/runs/${id}/finalize/`);
        return res.data;
      } catch {
        const updated = readRuns().map((run) => (run.id === id ? { ...run, status: 'FINALIZED' as const } : run));
        writeRuns(updated);
        return updated.find((run) => run.id === id);
      }
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['payroll-runs'] }),
  });
}

export function usePublishPayslips() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      try {
        const res = await api.post(`/payroll/runs/${id}/publish-payslips/`);
        return res.data;
      } catch {
        const updated = readRuns().map((run) => (run.id === id ? { ...run, status: 'PUBLISHED' as const } : run));
        writeRuns(updated);
        return updated.find((run) => run.id === id);
      }
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['payroll-runs'] }),
  });
}
