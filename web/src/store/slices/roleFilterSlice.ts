import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Role {
  id: string;
  name: string;
  access: string;
  status: string;
  users: number;
}

export interface EmployeeRoleMapping {
  employeeId: string;
  assignedRoles: string[]; // Role names or IDs
}

export interface CustomFilterRule {
  id: string;
  field: string;
  operator: string;
  value: string;
}

export interface CustomFilterGroup {
  id: string;
  conjunction: 'AND' | 'OR';
  rows: CustomFilterRule[];
}

export interface QuickFilterConfig {
  categoryType: string; // Designation, Department, Grade, Location, Attendance Scheme
  employeeType: 'All' | 'Current' | 'Resigned';
  employeeStatus: 'Probation' | 'Confirmed' | 'Contract' | 'Trainee';
}

export interface EmployeeFilter {
  id: string;
  title: string;
  isShared: boolean;
  type: 'quick' | 'custom';
  quickFilter: QuickFilterConfig;
  customFilterGroups: CustomFilterGroup[];
}

interface RoleFilterState {
  roles: Role[];
  mappings: EmployeeRoleMapping[];
  filters: EmployeeFilter[];
}

const DEFAULT_ROLES: Role[] = [
  { id: 'role-1', name: 'HR Manager', users: 5, access: 'Full Access', status: 'Critical' },
  { id: 'role-2', name: 'Finance Reviewer', users: 3, access: 'View & Edit', status: 'Moderate' },
  { id: 'role-3', name: 'General User', users: 1240, access: 'Self Service', status: 'Low' },
  { id: 'role-4', name: 'IT Administrator', users: 8, access: 'System Settings', status: 'High' }
];

const DEFAULT_MAPPINGS: EmployeeRoleMapping[] = [
  { employeeId: 'emp-1', assignedRoles: ['General User'] },
  { employeeId: 'emp-2', assignedRoles: ['HR Manager', 'General User'] },
  { employeeId: 'emp-3', assignedRoles: ['Finance Reviewer'] }
];

const DEFAULT_FILTERS: EmployeeFilter[] = [
  {
    id: 'f-1',
    title: 'Above 5 years',
    isShared: true,
    type: 'custom',
    quickFilter: { categoryType: 'Designation', employeeType: 'All', employeeStatus: 'Confirmed' },
    customFilterGroups: [
      {
        id: 'g-1',
        conjunction: 'AND',
        rows: [{ id: 'r-1', field: 'Years In Service', operator: 'GREATER THAN', value: '5' }]
      }
    ]
  },
  {
    id: 'f-2',
    title: 'All Current Employees',
    isShared: true,
    type: 'quick',
    quickFilter: { categoryType: 'Department', employeeType: 'Current', employeeStatus: 'Confirmed' },
    customFilterGroups: []
  },
  {
    id: 'f-3',
    title: 'All Past Employees',
    isShared: true,
    type: 'quick',
    quickFilter: { categoryType: 'Department', employeeType: 'Resigned', employeeStatus: 'Contract' },
    customFilterGroups: []
  },
  {
    id: 'f-4',
    title: 'Bangalore Employees',
    isShared: true,
    type: 'custom',
    quickFilter: { categoryType: 'Location', employeeType: 'All', employeeStatus: 'Confirmed' },
    customFilterGroups: [
      {
        id: 'g-4',
        conjunction: 'AND',
        rows: [{ id: 'r-4', field: 'Location', operator: 'EQUAL TO', value: 'Bangalore' }]
      }
    ]
  },
  {
    id: 'f-5',
    title: 'Between 3 – 5 years',
    isShared: true,
    type: 'custom',
    quickFilter: { categoryType: 'Designation', employeeType: 'All', employeeStatus: 'Confirmed' },
    customFilterGroups: [
      {
        id: 'g-5',
        conjunction: 'AND',
        rows: [{ id: 'r-5', field: 'Years In Service', operator: 'BETWEEN', value: '3, 5' }]
      }
    ]
  },
  {
    id: 'f-6',
    title: 'Confirmed Employees',
    isShared: true,
    type: 'quick',
    quickFilter: { categoryType: 'Designation', employeeType: 'Current', employeeStatus: 'Confirmed' },
    customFilterGroups: []
  },
  {
    id: 'f-7',
    title: 'Contract Emp',
    isShared: true,
    type: 'quick',
    quickFilter: { categoryType: 'Designation', employeeType: 'Current', employeeStatus: 'Contract' },
    customFilterGroups: []
  },
  {
    id: 'f-8',
    title: 'Partially Vaccinated Employees',
    isShared: true,
    type: 'custom',
    quickFilter: { categoryType: 'Designation', employeeType: 'All', employeeStatus: 'Confirmed' },
    customFilterGroups: [
      {
        id: 'g-8',
        conjunction: 'AND',
        rows: [{ id: 'r-8', field: 'PAN Status', operator: 'EQUAL TO', value: 'Verified' }]
      }
    ]
  },
  {
    id: 'f-9',
    title: 'Probation Emp',
    isShared: true,
    type: 'quick',
    quickFilter: { categoryType: 'Designation', employeeType: 'Current', employeeStatus: 'Probation' },
    customFilterGroups: []
  },
  {
    id: 'f-10',
    title: 'Sales Department',
    isShared: true,
    type: 'custom',
    quickFilter: { categoryType: 'Department', employeeType: 'Current', employeeStatus: 'Confirmed' },
    customFilterGroups: [
      {
        id: 'g-10',
        conjunction: 'AND',
        rows: [{ id: 'r-10', field: 'Department', operator: 'EQUAL TO', value: 'Sales' }]
      }
    ]
  },
  {
    id: 'f-11',
    title: 'Trainee Employees',
    isShared: true,
    type: 'quick',
    quickFilter: { categoryType: 'Designation', employeeType: 'Current', employeeStatus: 'Trainee' },
    customFilterGroups: []
  },
  {
    id: 'f-12',
    title: 'Upto 3 years service',
    isShared: true,
    type: 'custom',
    quickFilter: { categoryType: 'Designation', employeeType: 'All', employeeStatus: 'Confirmed' },
    customFilterGroups: [
      {
        id: 'g-12',
        conjunction: 'AND',
        rows: [{ id: 'r-12', field: 'Years In Service', operator: 'LESS THAN', value: '3' }]
      }
    ]
  }
];

const initialState: RoleFilterState = {
  roles: DEFAULT_ROLES,
  mappings: DEFAULT_MAPPINGS,
  filters: DEFAULT_FILTERS
};

const roleFilterSlice = createSlice({
  name: 'roleFilter',
  initialState,
  reducers: {
    addRole: (state, action: PayloadAction<Role>) => {
      state.roles.unshift(action.payload);
    },
    deleteRole: (state, action: PayloadAction<string>) => {
      state.roles = state.roles.filter(r => r.id !== action.payload);
    },
    saveMapping: (state, action: PayloadAction<EmployeeRoleMapping>) => {
      const idx = state.mappings.findIndex(m => m.employeeId === action.payload.employeeId);
      if (idx !== -1) {
        state.mappings[idx] = action.payload;
      } else {
        state.mappings.push(action.payload);
      }
      
      // Update count of users per role
      state.roles.forEach(role => {
        role.users = state.mappings.filter(m => m.assignedRoles.includes(role.name)).length;
      });
    },
    addFilter: (state, action: PayloadAction<EmployeeFilter>) => {
      state.filters.unshift(action.payload);
    },
    updateFilter: (state, action: PayloadAction<EmployeeFilter>) => {
      const idx = state.filters.findIndex(f => f.id === action.payload.id);
      if (idx !== -1) {
        state.filters[idx] = action.payload;
      }
    },
    deleteFilter: (state, action: PayloadAction<string>) => {
      state.filters = state.filters.filter(f => f.id !== action.payload);
    }
  }
});

export const { 
  addRole, 
  deleteRole, 
  saveMapping, 
  addFilter, 
  updateFilter, 
  deleteFilter 
} = roleFilterSlice.actions;

export default roleFilterSlice.reducer;
