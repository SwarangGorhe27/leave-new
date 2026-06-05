import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { SectionKey, RequestStatus } from '../../app/modules/ess/types';
import { updateEmployeeData } from './employeeSlice';
import { addNotification } from './notificationSlice';

export interface FieldChange {
  fieldName: string;
  fieldLabel: string;
  oldValue: any;
  newValue: any;
}

export interface ProfileRequest {
  id: string;
  employeeId: string;
  section: SectionKey;
  sectionLabel: string;
  changes: FieldChange[];
  status: RequestStatus;
  createdAt: string;
  reviewedBy: string | null;
  reviewedAt: string | null;
  rejectionComment?: string;
  adminRemark?: string;
}

interface RequestState {
  requests: ProfileRequest[];
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

const initialState: RequestState = {
  requests: [],
  status: 'idle',
  error: null,
};

// Helper for local storage mock DB
const readRequests = (): ProfileRequest[] => {
  const raw = localStorage.getItem('mock_requests_db');
  return raw ? JSON.parse(raw) : [];
};

const writeRequests = (reqs: ProfileRequest[]) => {
  localStorage.setItem('mock_requests_db', JSON.stringify(reqs));
};

export const fetchRequests = createAsyncThunk(
  'requests/fetch',
  async (employeeId?: string) => {
    await new Promise((resolve) => setTimeout(resolve, 500));

    let requests = readRequests();
    if (employeeId) {
      requests = requests.filter((r) => r.employeeId === employeeId);
    }

    return requests.sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
    );
  },
);

export const createRequest = createAsyncThunk(
  'requests/create',
  async (
    payload: Omit<
      ProfileRequest,
      'id' | 'status' | 'createdAt' | 'reviewedBy' | 'reviewedAt'
    >,
    { dispatch },
  ) => {
    await new Promise((resolve) => setTimeout(resolve, 500));

    const newRequest: ProfileRequest = {
      ...payload,
      id: Date.now().toString() + Math.random().toString(),
      status: 'pending',
      createdAt: new Date().toISOString(),
      reviewedBy: null,
      reviewedAt: null,
    };

    const reqs = readRequests();
    reqs.push(newRequest);
    writeRequests(reqs);

    dispatch(
      addNotification({
        type: 'info',
        message: 'Your request has been sent to admin.',
      }),
    );

    return newRequest;
  },
);

export const reviewRequest = createAsyncThunk(
  'requests/review',
  async (
    {
      requestId,
      status,
      reviewer,
      rejectionComment,
      adminRemark,
      employeeId,
      section,
      finalData,
    }: {
      requestId: string;
      status: RequestStatus;
      reviewer: string;
      rejectionComment?: string;
      adminRemark?: string;
      employeeId: string;
      section: SectionKey;
      finalData?: any;
    },
    { dispatch },
  ) => {
    await new Promise((resolve) => setTimeout(resolve, 500));

    const reqs = readRequests();
    const index = reqs.findIndex((r) => r.id === requestId);

    if (index < 0) {
      throw new Error('Request not found');
    }

    reqs[index].status = status;
    reqs[index].reviewedBy = reviewer;
    reqs[index].reviewedAt = new Date().toISOString();

    if (rejectionComment) {
      reqs[index].rejectionComment = rejectionComment;
    }
    if (adminRemark !== undefined) {
      reqs[index].adminRemark = adminRemark;
    }

    writeRequests(reqs);

    if (status === 'approved' && finalData) {
      // Trigger profile update (bypass lock because this is an admin approval path)
      try {
        dispatch(updateEmployeeData({ employeeId, section, data: finalData, bypassLock: true } as any));
        // Append audit log
        try {
          const raw = localStorage.getItem('hrms_profile_change_audit') || '[]';
          const audits = JSON.parse(raw) as any[];
          audits.push({ id: Date.now().toString(), requestId, employeeId, section, reviewer, reviewedAt: new Date().toISOString(), changes: finalData });
          localStorage.setItem('hrms_profile_change_audit', JSON.stringify(audits));
        } catch (e) {
          console.error('Failed to write audit log', e);
        }
        dispatch(
          addNotification({
            type: 'success',
            message: 'Profile update request approved.',
          }),
        );
      } catch (e) {
        dispatch(
          addNotification({
            type: 'error',
            message: 'Failed to apply approved changes.',
          }),
        );
      }
    } else if (status === 'rejected') {
      dispatch(
        addNotification({
          type: 'warning',
          message: 'Profile update request rejected.',
        }),
      );
    }

    return reqs[index];
  },
);

export const updateRequest = createAsyncThunk(
  'requests/update',
  async (payload: ProfileRequest, { dispatch }) => {
    await new Promise((resolve) => setTimeout(resolve, 400));

    const reqs = readRequests();
    const idx = reqs.findIndex((r) => r.id === payload.id);

    if (idx >= 0) {
      reqs[idx] = { ...reqs[idx], ...payload };
      writeRequests(reqs);

      dispatch(
        addNotification({
          type: 'info',
          message: 'Your request has been updated.',
        }),
      );

      return reqs[idx];
    }

    throw new Error('Request not found');
  },
);

export const withdrawRequest = createAsyncThunk(
  'requests/withdraw',
  async ({ requestId }: { requestId: string }, { dispatch }) => {
    await new Promise((resolve) => setTimeout(resolve, 300));

    const reqs = readRequests();
    const idx = reqs.findIndex((r) => r.id === requestId);

    if (idx >= 0) {
      const removed = reqs.splice(idx, 1)[0];
      writeRequests(reqs);

      dispatch(
        addNotification({
          type: 'info',
          message: 'Request withdrawn.',
        }),
      );

      return removed;
    }

    throw new Error('Request not found');
  },
);

const requestSlice = createSlice({
  name: 'requests',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchRequests.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchRequests.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.requests = action.payload;
      })
      .addCase(createRequest.fulfilled, (state, action) => {
        state.requests.unshift(action.payload);
      })
      .addCase(updateRequest.fulfilled, (state, action) => {
        const index = state.requests.findIndex((r) => r.id === action.payload.id);
        if (index >= 0) state.requests[index] = action.payload;
      })
      .addCase(withdrawRequest.fulfilled, (state, action) => {
        state.requests = state.requests.filter((r) => r.id !== action.payload.id);
      })
      .addCase(reviewRequest.fulfilled, (state, action) => {
        const index = state.requests.findIndex((r) => r.id === action.payload.id);
        if (index >= 0) {
          state.requests[index] = action.payload;
        }
      });
  },
});

export default requestSlice.reducer;

