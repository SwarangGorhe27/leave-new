import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@api/client';

const STORAGE_PREFIX = 'hrms-demo-masters';

const DEMO_MASTERS: Record<string, MasterItem[]> = {
  departments: [
    { id: 'dept-1', name: 'Human Resources', code: 'HR', is_active: true },
    { id: 'dept-2', name: 'Finance', code: 'FIN', is_active: true },
    { id: 'dept-3', name: 'Engineering', code: 'ENG', is_active: true },
  ],
  designations: [
    { id: 'desig-1', name: 'HR Manager', code: 'HRM', is_active: true },
    { id: 'desig-2', name: 'Payroll Specialist', code: 'PAY', is_active: true },
    { id: 'desig-3', name: 'Software Engineer', code: 'SWE', is_active: true },
  ],
  'employment-types': [
    { id: 'emptype-1', name: 'Permanent', code: 'PERM', is_active: true },
    { id: 'emptype-2', name: 'Contract', code: 'CONT', is_active: true },
    { id: 'emptype-3', name: 'Intern', code: 'INT', is_active: true },
  ],
  'company-locations': [
    { id: 'loc-1', name: 'Mumbai HO', code: 'MUM-HO', is_active: true },
    { id: 'loc-2', name: 'Pune Office', code: 'PUN-01', is_active: true },
  ],
  'leave-types': [
    { id: 'lt-1', name: 'Privilege Leave', code: 'PL', is_active: true, category: 'ANNUAL', is_paid: true },
    { id: 'lt-2', name: 'Sick Leave', code: 'SL', is_active: true, category: 'SICK', is_paid: true },
    { id: 'lt-3', name: 'Casual Leave', code: 'CL', is_active: true, category: 'CASUAL', is_paid: true },
  ],
  'shift-types': [
    { id: 'st-1', name: 'Day', code: 'DAY', is_active: true },
    { id: 'st-2', name: 'Night', code: 'NIGHT', is_active: true },
    { id: 'st-3', name: 'Rotational', code: 'ROT', is_active: true },
  ],
  branches: [
    { id: 'br-1', name: 'Mumbai Branch', code: 'MUM-01', is_active: true, branch_type: 'HEAD_OFFICE', is_payroll_entity: true },
    { id: 'br-2', name: 'Pune Branch', code: 'PUN-01', is_active: true, branch_type: 'BRANCH', is_payroll_entity: true },
  ],
  'cost-centers': [
    { id: 'cc-1', name: 'IT Delivery', code: 'CC-IT-001', is_active: true, cost_center_type: 'DIRECT', budget_code: 'BUD-IT-25' },
    { id: 'cc-2', name: 'Corporate HR', code: 'CC-HR-001', is_active: true, cost_center_type: 'OVERHEAD', budget_code: 'BUD-HR-25' },
  ],
  shifts: [
    { id: 'shift-1', name: 'General Shift', code: 'GEN', is_active: true, start_time: '09:00', end_time: '18:00', grace_in_minutes: 10, grace_out_minutes: 5, break_minutes: 60, weekly_off_days: 'SAT,SUN', is_overnight: false, is_flexible: false, ot_applicable: true },
    { id: 'shift-2', name: 'Night Shift', code: 'NITE', is_active: true, start_time: '21:00', end_time: '06:00', grace_in_minutes: 15, grace_out_minutes: 10, break_minutes: 45, weekly_off_days: 'SUN', is_overnight: true, is_flexible: false, ot_applicable: true },
  ],
  'pay-components': [
    { id: 'pc-1', name: 'Basic Salary', code: 'BASIC', is_active: true, component_type: 'FIXED', is_taxable: true, formula_type: 'PERCENT_OF_CTC', formula_value: 40 },
    { id: 'pc-2', name: 'House Rent Allowance', code: 'HRA', is_active: true, component_type: 'FIXED', is_taxable: true, formula_type: 'PERCENT_OF_BASIC', formula_value: 40 },
    { id: 'pc-3', name: 'PF Employee', code: 'PF_EE', is_active: true, component_type: 'STATUTORY', is_taxable: false, formula_type: 'PERCENT_OF_BASIC', formula_value: 12 },
  ],
  'salary-structures': [
    { id: 'ss-1', name: 'Staff Standard Structure', code: 'SS-STAFF-001', is_active: true, min_ctc: 300000, max_ctc: 1200000, currency_code: 'INR', effective_from: '2025-04-01' },
    { id: 'ss-2', name: 'Manager Structure', code: 'SS-MGR-001', is_active: true, min_ctc: 1200000, max_ctc: 3000000, currency_code: 'INR', effective_from: '2025-04-01' },
  ],
};

function storageKey(key: string) {
  return `${STORAGE_PREFIX}:${key}`;
}

function readDemoMasters(key: string): MasterItem[] {
  const raw = localStorage.getItem(storageKey(key));
  if (raw) {
    try {
      return JSON.parse(raw) as MasterItem[];
    } catch {
      // fallback to seeded data
    }
  }
  const seeded = DEMO_MASTERS[key] ?? [];
  localStorage.setItem(storageKey(key), JSON.stringify(seeded));
  return seeded;
}

function writeDemoMasters(key: string, items: MasterItem[]) {
  localStorage.setItem(storageKey(key), JSON.stringify(items));
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

export interface MasterItem {
  id: number | string;
  name: string;
  code?: string;
  is_active: boolean;
  [key: string]: unknown;
}

function makeMasterHooks(path: string, key: string) {
  return {
    useList: () =>
      useQuery({
        queryKey: ['masters', key],
        queryFn: async () => {
          try {
            const res = await api.get(`/masters/${path}/`);
            const items = extract<MasterItem>(res);
            if (items.length) {
              writeDemoMasters(key, items);
              return items;
            }
          } catch {
            // fallback to demo data
          }
          return readDemoMasters(key);
        },
        staleTime: 120_000,
      }),
    useCreate: () => {
      const qc = useQueryClient();
      return useMutation({
        mutationFn: async (data: Partial<MasterItem>) => {
          try {
            const res = await api.post(`/masters/${path}/`, data);
            return extractOne<MasterItem>(res);
          } catch {
            const item: MasterItem = {
              id: crypto.randomUUID(),
              name: String(data.name ?? 'New Item'),
              code: data.code ? String(data.code) : undefined,
              is_active: data.is_active ?? true,
              ...data,
            };
            const items = readDemoMasters(key);
            writeDemoMasters(key, [item, ...items]);
            return item;
          }
        },
        onSuccess: () => qc.invalidateQueries({ queryKey: ['masters', key] }),
      });
    },
    useUpdate: () => {
      const qc = useQueryClient();
      return useMutation({
        mutationFn: async ({ id, ...data }: Partial<MasterItem> & { id: number | string }) => {
          try {
            const res = await api.patch(`/masters/${path}/${id}/`, data);
            return extractOne<MasterItem>(res);
          } catch {
            const items = readDemoMasters(key);
            const updated = items.map((item) => (String(item.id) === String(id) ? { ...item, ...data } : item));
            writeDemoMasters(key, updated);
            return (updated.find((item) => String(item.id) === String(id)) ?? items[0]) as MasterItem;
          }
        },
        onSuccess: () => qc.invalidateQueries({ queryKey: ['masters', key] }),
      });
    },
    useDelete: () => {
      const qc = useQueryClient();
      return useMutation({
        mutationFn: async (id: number | string) => {
          try {
            await api.delete(`/masters/${path}/${id}/`);
            return;
          } catch {
            const items = readDemoMasters(key);
            writeDemoMasters(key, items.filter((item) => String(item.id) !== String(id)));
          }
        },
        onSuccess: () => qc.invalidateQueries({ queryKey: ['masters', key] }),
      });
    },
  };
}

export const useDepartments = makeMasterHooks('departments', 'departments');
export const useDesignations = makeMasterHooks('designations', 'designations');
export const useEmploymentTypes = makeMasterHooks('employment-types', 'employment-types');
export const useCompanyLocations = makeMasterHooks('company-locations', 'company-locations');
export const useLeaveTypesMaster = makeMasterHooks('leave-types', 'leave-types');
export const useShiftTypes = makeMasterHooks('shift-types', 'shift-types');
export const useEmployeeStatuses = makeMasterHooks('employee-statuses', 'employee-statuses');
export const useEmployeeCategories = makeMasterHooks('employee-categories', 'employee-categories');
export const useBranches = makeMasterHooks('branches', 'branches');
export const useCostCenters = makeMasterHooks('cost-centers', 'cost-centers');
export const useShifts = makeMasterHooks('shifts', 'shifts');
export const usePayComponents = makeMasterHooks('pay-components', 'pay-components');
export const useSalaryStructures = makeMasterHooks('salary-structures', 'salary-structures');
