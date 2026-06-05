import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface FilterRow {
  id: string;
  field: string;
  operator: string;
  value: string;
}

export interface CriteriaGroup {
  id: string;
  conjunction: 'AND' | 'OR';
  rows: FilterRow[];
}

export interface Segment {
  id: string;
  name: string;
  createdBy: string;
  createdDate: string;
  totalEmployees: number;
  source: 'Based on employee filter criteria' | 'Manual, ad hoc list of employees';
  employeeIds: string[]; // Used for manual ad hoc lists
  criteriaGroups: CriteriaGroup[]; // Used for criteria-based segmentation
  quickFilters: string[]; // Selected predefined filter tags
  isArchived?: boolean;
}

export interface SharedFilter {
  id: string;
  title: string;
  criteriaGroups: CriteriaGroup[];
  quickFilters: string[];
}

interface SegmentState {
  segments: Segment[];
  sharedFilters: SharedFilter[];
  loading: boolean;
}

const DEFAULT_SEGMENTS: Segment[] = [
  {
    id: 'seg-1',
    name: 'Engineering Leads',
    createdBy: 'admin',
    createdDate: '2026-04-10',
    totalEmployees: 24,
    source: 'Based on employee filter criteria',
    employeeIds: [],
    criteriaGroups: [
      {
        id: 'g-1',
        conjunction: 'AND',
        rows: [
          { id: 'r-1', field: 'Employee Role', operator: 'EQUAL TO', value: 'Lead' },
          { id: 'r-2', field: 'Department', operator: 'EQUAL TO', value: 'Engineering' }
        ]
      }
    ],
    quickFilters: ['All Current Employees']
  },
  {
    id: 'seg-2',
    name: 'NYC Sales Team',
    createdBy: 'admin',
    createdDate: '2026-04-15',
    totalEmployees: 156,
    source: 'Based on employee filter criteria',
    employeeIds: [],
    criteriaGroups: [
      {
        id: 'g-2',
        conjunction: 'AND',
        rows: [
          { id: 'r-3', field: 'Location', operator: 'EQUAL TO', value: 'New York' },
          { id: 'r-4', field: 'Department', operator: 'EQUAL TO', value: 'Sales' }
        ]
      }
    ],
    quickFilters: ['All Current Employees']
  },
  {
    id: 'seg-3',
    name: 'Trainees Cohort',
    createdBy: 'recruit1',
    createdDate: '2026-05-01',
    totalEmployees: 18,
    source: 'Manual, ad hoc list of employees',
    employeeIds: ['emp-1', 'emp-2', 'emp-3'], // mock list
    criteriaGroups: [],
    quickFilters: []
  }
];

const DEFAULT_SHARED_FILTERS: SharedFilter[] = [
  {
    id: 'sf-1',
    title: 'Senior Tenure',
    criteriaGroups: [
      {
        id: 'g-sf1',
        conjunction: 'AND',
        rows: [
          { id: 'r-sf1', field: 'Years In Service', operator: 'GREATER THAN', value: '5' }
        ]
      }
    ],
    quickFilters: ['All Current Employees']
  }
];

const initialState: SegmentState = {
  segments: DEFAULT_SEGMENTS,
  sharedFilters: DEFAULT_SHARED_FILTERS,
  loading: false
};

const segmentSlice = createSlice({
  name: 'segment',
  initialState,
  reducers: {
    addSegment: (state, action: PayloadAction<Segment>) => {
      state.segments.unshift(action.payload);
    },
    updateSegment: (state, action: PayloadAction<Segment>) => {
      const idx = state.segments.findIndex(s => s.id === action.payload.id);
      if (idx !== -1) {
        state.segments[idx] = action.payload;
      }
    },
    deleteSegment: (state, action: PayloadAction<string>) => {
      state.segments = state.segments.filter(s => s.id !== action.payload);
    },
    duplicateSegment: (state, action: PayloadAction<string>) => {
      const base = state.segments.find(s => s.id === action.payload);
      if (base) {
        state.segments.unshift({
          ...base,
          id: `seg-${Date.now()}`,
          name: `${base.name} (Copy)`,
          createdDate: new Date().toISOString().split('T')[0]
        });
      }
    },
    archiveSegment: (state, action: PayloadAction<string>) => {
      const seg = state.segments.find(s => s.id === action.payload);
      if (seg) {
        seg.isArchived = !seg.isArchived;
      }
    },
    addSharedFilter: (state, action: PayloadAction<SharedFilter>) => {
      state.sharedFilters.unshift(action.payload);
    }
  }
});

export const { 
  addSegment, 
  updateSegment, 
  deleteSegment, 
  duplicateSegment, 
  archiveSegment, 
  addSharedFilter 
} = segmentSlice.actions;

export default segmentSlice.reducer;
