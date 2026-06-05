import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';

export interface AdminActivity {
  id: string;
  employeeId: string;
  adminName: string;
  editedSection: string;
  changedField: string;
  oldValue: string | number | boolean | null;
  newValue: string | number | boolean | null;
  timestamp: string;
}

interface ActivityState {
  activities: AdminActivity[];
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
}

const initialState: ActivityState = {
  activities: [],
  status: 'idle',
};

// Mock storage for activities
const readActivities = (): AdminActivity[] => {
  const raw = localStorage.getItem('mock_activity_db');
  return raw ? JSON.parse(raw) : [];
};

const writeActivities = (activities: AdminActivity[]) => {
  localStorage.setItem('mock_activity_db', JSON.stringify(activities));
};

export const fetchActivities = createAsyncThunk(
  'activities/fetch',
  async (employeeId: string) => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const all = readActivities();
    return all.filter(a => a.employeeId === employeeId).sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }
);

export const logActivity = createAsyncThunk(
  'activities/log',
  async (payload: Omit<AdminActivity, 'id' | 'timestamp'>) => {
    const activity: AdminActivity = {
      ...payload,
      id: Date.now().toString() + Math.random().toString(),
      timestamp: new Date().toISOString(),
    };
    const activities = readActivities();
    activities.unshift(activity);
    writeActivities(activities);
    return activity;
  }
);

const activitySlice = createSlice({
  name: 'activities',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchActivities.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchActivities.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.activities = action.payload;
      })
      .addCase(logActivity.fulfilled, (state, action) => {
        state.activities.unshift(action.payload);
      });
  },
});

export default activitySlice.reducer;
