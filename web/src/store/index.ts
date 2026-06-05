import { configureStore } from '@reduxjs/toolkit';
import employeeReducer from './slices/employeeSlice';
import requestReducer from './slices/requestSlice';
import notificationReducer from './slices/notificationSlice';
import activityReducer from './slices/activitySlice';
import adminReducer from './slices/adminSlice';
import letterReducer from './slices/letterSlice';
import documentTypesReducer from './slices/documentTypesSlice';
import policyReducer from './slices/policySlice';
import segmentReducer from './slices/segmentSlice';
import roleFilterReducer from './slices/roleFilterSlice';
import finesDamagesReducer from './slices/finesDamagesSlice';

export const store = configureStore({
  reducer: {
    employee: employeeReducer,
    requests: requestReducer,
    notifications: notificationReducer,
    activities: activityReducer,
    admin: adminReducer,
    letter: letterReducer,
    documentTypes: documentTypesReducer,
    policy: policyReducer,
    segment: segmentReducer,
    roleFilter: roleFilterReducer,
    finesDamages: finesDamagesReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
