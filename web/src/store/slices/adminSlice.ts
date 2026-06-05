import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Employee, normalizeLegacyEmployee } from '../../app/components/employees/mockData';
import { findEmployeeRecordIndex } from '../../app/utils/employeeStoreUtils';

/** In-memory cache only — populated from API, not localStorage mock DB. */
interface AdminState {
  employees: Employee[];
}

const initialState: AdminState = {
  employees: [],
};

const adminSlice = createSlice({
  name: 'admin',
  initialState,
  reducers: {
    updateAdminEmployee: (state, action: PayloadAction<Employee>) => {
      const index = findEmployeeRecordIndex(state.employees, action.payload);
      if (index >= 0) {
        const existingId = state.employees[index].id;
        state.employees[index] = { ...action.payload, id: existingId };
      } else {
        state.employees.unshift(action.payload);
      }
    },
    addAdminEmployee: (state, action: PayloadAction<Employee>) => {
      const index = findEmployeeRecordIndex(state.employees, action.payload);
      if (index < 0) {
        state.employees.unshift(action.payload);
      }
    },
    addAdminEmployees: (state, action: PayloadAction<Employee[]>) => {
      for (const emp of action.payload) {
        if (findEmployeeRecordIndex(state.employees, emp) < 0) {
          state.employees.unshift(emp);
        }
      }
    },
    setAdminEmployees: (state, action: PayloadAction<Employee[]>) => {
      state.employees = action.payload.map((row) =>
        normalizeLegacyEmployee(row as unknown as Record<string, unknown>),
      );
    },
    clearAdminEmployees: (state) => {
      state.employees = [];
    },
  },
});

export const {
  updateAdminEmployee,
  addAdminEmployee,
  addAdminEmployees,
  setAdminEmployees,
  clearAdminEmployees,
} = adminSlice.actions;
export default adminSlice.reducer;
