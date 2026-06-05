import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { ensureProfile } from '../../app/modules/ess/storage';
import { EmployeeProfile } from '../../app/modules/ess/types';
import { mergeAdminEmployeeIntoEssProfile, mergeEssEmployeeOwnedIntoAdmin, writeEssProfileToStorage } from '../../app/modules/ess/adminEssSync';
import { updateAdminEmployee } from './adminSlice';
import type { RootState } from '../index';

interface EmployeeState {
  profile: EmployeeProfile | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

const initialState: EmployeeState = {
  profile: null,
  status: 'idle',
  error: null,
};

export const fetchEmployeeData = createAsyncThunk(
  'employee/fetch',
  async (employeeId: string, { getState }) => {
    await new Promise(resolve => setTimeout(resolve, 400));
    const profile = ensureProfile(employeeId);
    const admin = (getState() as RootState).admin.employees.find((e) => e.id === employeeId);
    if (admin) return mergeAdminEmployeeIntoEssProfile(admin, profile);
    return profile;
  }
);

export const updateEmployeeData = createAsyncThunk(
  'employee/update',
  async ({ employeeId, section, data, bypassLock }: { employeeId: string; section: string; data: any; bypassLock?: boolean }) => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const profile = ensureProfile(employeeId);
    if (profile.profileLocked && !bypassLock) {
      throw new Error('Profile is locked for direct updates. Use request workflow.');
    }
    const updatedProfile = { ...profile, [section]: data };
    const raw = localStorage.getItem('hrms_ess_profiles') || '{}';
    const profiles = JSON.parse(raw);
    profiles[employeeId] = updatedProfile;
    localStorage.setItem('hrms_ess_profiles', JSON.stringify(profiles));
    return updatedProfile;
  }
);

export const forceUpdateEmployeeData = createAsyncThunk(
  'employee/forceUpdate',
  async ({ employeeId, fullProfile }: { employeeId: string; fullProfile: any }) => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const raw = localStorage.getItem('hrms_ess_profiles') || '{}';
    const profiles = JSON.parse(raw);
    profiles[employeeId] = fullProfile;
    localStorage.setItem('hrms_ess_profiles', JSON.stringify(profiles));
    return fullProfile;
  }
);

/** Persist ESS profile and mirror employee-owned fields onto admin Employee row. */
export const saveEssProfileWithAdminSync = createAsyncThunk(
  'employee/saveEssAdmin',
  async ({ employeeId, profile }: { employeeId: string; profile: EmployeeProfile }, { dispatch, getState }) => {
    writeEssProfileToStorage(employeeId, profile);
    const admin = (getState() as RootState).admin.employees.find((e) => e.id === employeeId);
    if (admin) {
      const merged = mergeEssEmployeeOwnedIntoAdmin(admin, profile);
      dispatch(updateAdminEmployee(merged));
    }
    return profile;
  }
);

const employeeSlice = createSlice({
  name: 'employee',
  initialState,
  reducers: {
    setProfileData(state, action: PayloadAction<EmployeeProfile>) {
      state.profile = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchEmployeeData.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchEmployeeData.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.profile = action.payload;
      })
      .addCase(updateEmployeeData.fulfilled, (state, action) => {
        state.profile = action.payload;
      })
      .addCase(forceUpdateEmployeeData.fulfilled, (state, action) => {
        state.profile = action.payload;
      })
      .addCase(saveEssProfileWithAdminSync.fulfilled, (state, action) => {
        state.profile = action.payload;
      });
  },
});

export const { setProfileData } = employeeSlice.actions;
export default employeeSlice.reducer;
