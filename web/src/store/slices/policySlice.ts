import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Policy {
  id: string;
  name: string;
  description: string;
  category: string;
  serialNo: string;
  file?: {
    name: string;
    size: number;
    url: string;
  };
  releaseToEss: boolean;
  employeeFilters: string[];
  enforcePolicy: boolean;
  lastUpdated: string;
}

export interface Form {
  id: string;
  name: string;
  description: string;
  category: string;
  serialNo: string;
  file?: {
    name: string;
    size: number;
    url: string;
  };
  lastUpdated: string;
}

export interface Category {
  id: string;
  name: string;
}

interface PolicyState {
  policies: Policy[];
  forms: Form[];
  policyCategories: Category[];
  formCategories: Category[];
}

const INITIAL_POLICY_CATEGORIES: Category[] = [
  { id: 'cat-p-1', name: 'General' },
  { id: 'cat-p-2', name: 'PF Forms' },
  { id: 'cat-p-3', name: 'HR' }
];

const INITIAL_FORM_CATEGORIES: Category[] = [
  { id: 'cat-f-1', name: 'General' }
];

const INITIAL_POLICIES: Policy[] = [
  {
    id: 'p-1',
    name: 'Employee Code of Conduct',
    description: 'Guidelines regarding employee conduct, professional ethics, and company standards.',
    category: 'HR',
    serialNo: 'POL-001',
    releaseToEss: true,
    employeeFilters: ['All Current Employees'],
    enforcePolicy: true,
    lastUpdated: '2026-05-01',
    file: { name: 'code_of_conduct.pdf', size: 1024000, url: '#' }
  },
  {
    id: 'p-2',
    name: 'Travel Policy 2026',
    description: 'Rules and reimbursements guide for official travel, accommodations, and food allowances.',
    category: 'General',
    serialNo: 'POL-002',
    releaseToEss: true,
    employeeFilters: ['Sales Department', 'Bangalore Employees'],
    enforcePolicy: false,
    lastUpdated: '2026-03-22',
    file: { name: 'travel_policy_2026.pdf', size: 1540000, url: '#' }
  }
];

const INITIAL_FORMS: Form[] = [
  {
    id: 'f-1',
    name: 'Sick Leave Application Form',
    description: 'Standard template for applying for extended medical leave.',
    category: 'General',
    serialNo: 'FRM-001',
    lastUpdated: '2026-01-15',
    file: { name: 'sick_leave_application.docx', size: 54000, url: '#' }
  },
  {
    id: 'f-2',
    name: 'NDA - Standard Template',
    description: 'Non-disclosure agreement template required for external consultants and new recruits.',
    category: 'General',
    serialNo: 'FRM-002',
    lastUpdated: '2026-04-10',
    file: { name: 'nda_template.pdf', size: 450000, url: '#' }
  }
];

const initialState: PolicyState = {
  policies: INITIAL_POLICIES,
  forms: INITIAL_FORMS,
  policyCategories: INITIAL_POLICY_CATEGORIES,
  formCategories: INITIAL_FORM_CATEGORIES
};

const policySlice = createSlice({
  name: 'policy',
  initialState,
  reducers: {
    // Policies
    addPolicy: (state, action: PayloadAction<Policy>) => {
      state.policies.unshift(action.payload);
    },
    updatePolicy: (state, action: PayloadAction<Policy>) => {
      const index = state.policies.findIndex(p => p.id === action.payload.id);
      if (index !== -1) {
        state.policies[index] = action.payload;
      }
    },
    deletePolicy: (state, action: PayloadAction<string>) => {
      state.policies = state.policies.filter(p => p.id !== action.payload);
    },

    // Forms
    addForm: (state, action: PayloadAction<Form>) => {
      state.forms.unshift(action.payload);
    },
    updateForm: (state, action: PayloadAction<Form>) => {
      const index = state.forms.findIndex(f => f.id === action.payload.id);
      if (index !== -1) {
        state.forms[index] = action.payload;
      }
    },
    deleteForm: (state, action: PayloadAction<string>) => {
      state.forms = state.forms.filter(f => f.id !== action.payload);
    },

    // Policy Categories
    addPolicyCategory: (state, action: PayloadAction<string>) => {
      const exists = state.policyCategories.some(c => c.name.toLowerCase() === action.payload.toLowerCase());
      if (!exists) {
        state.policyCategories.push({
          id: `cat-p-${Date.now()}`,
          name: action.payload
        });
      }
    },
    deletePolicyCategory: (state, action: PayloadAction<string>) => {
      state.policyCategories = state.policyCategories.filter(c => c.id !== action.payload);
    },

    // Form Categories
    addFormCategory: (state, action: PayloadAction<string>) => {
      const exists = state.formCategories.some(c => c.name.toLowerCase() === action.payload.toLowerCase());
      if (!exists) {
        state.formCategories.push({
          id: `cat-f-${Date.now()}`,
          name: action.payload
        });
      }
    },
    deleteFormCategory: (state, action: PayloadAction<string>) => {
      state.formCategories = state.formCategories.filter(c => c.id !== action.payload);
    }
  }
});

export const {
  addPolicy,
  updatePolicy,
  deletePolicy,
  addForm,
  updateForm,
  deleteForm,
  addPolicyCategory,
  deletePolicyCategory,
  addFormCategory,
  deleteFormCategory
} = policySlice.actions;

export default policySlice.reducer;
