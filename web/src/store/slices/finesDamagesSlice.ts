import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface FineRecord {
  id: string;
  employeeId: string;
  employeeName: string;
  employeeNumber: string;
  dateOfOffence: string;
  actOmission: string;
  showedCause: 'Yes' | 'No';
  dateOfShowCauseNotice: string;
  hearingAuthorityName: string;
  fineAmount: number;
  dateFineRealized: string;
  remarks: string;
}

export interface DamageRecord {
  id: string;
  employeeId: string;
  employeeName: string;
  employeeNumber: string;
  dateOfDamage: string;
  damageParticulars: string;
  showedCause: 'Yes' | 'No';
  dateOfShowCauseNotice: string;
  hearingAuthorityName: string;
  deductionAmount: number;
  installments: number;
  firstInstallmentDate: string;
  lastInstallmentDate: string;
  remarks: string;
}

interface FinesDamagesState {
  fines: FineRecord[];
  damages: DamageRecord[];
}

const DEFAULT_FINES: FineRecord[] = [
  {
    id: 'fine-1',
    employeeId: 'emp-1',
    employeeName: 'Rahul Sharma',
    employeeNumber: 'EMP001',
    dateOfOffence: '2026-05-10',
    actOmission: 'Unauthorized absence from workstation during shift hours',
    showedCause: 'Yes',
    dateOfShowCauseNotice: '2026-05-12',
    hearingAuthorityName: 'Amit Verma (Operations Head)',
    fineAmount: 500,
    dateFineRealized: '2026-05-15',
    remarks: 'First offence warnings were ignored.'
  },
  {
    id: 'fine-2',
    employeeId: 'emp-2',
    employeeName: 'Priya Nair',
    employeeNumber: 'EMP002',
    dateOfOffence: '2026-05-08',
    actOmission: 'Late login exceeding maximum grace minutes limits',
    showedCause: 'No',
    dateOfShowCauseNotice: '',
    hearingAuthorityName: '',
    fineAmount: 200,
    dateFineRealized: '2026-05-12',
    remarks: 'Auto-deducted from attendance metrics.'
  }
];

const DEFAULT_DAMAGES: DamageRecord[] = [
  {
    id: 'damage-1',
    employeeId: 'emp-3',
    employeeName: 'Vikram Singh',
    employeeNumber: 'EMP003',
    dateOfDamage: '2026-05-01',
    damageParticulars: 'Company laptop screen breakage due to negligence',
    showedCause: 'Yes',
    dateOfShowCauseNotice: '2026-05-03',
    hearingAuthorityName: 'Sanjay Kumar (IT Director)',
    deductionAmount: 8000,
    installments: 4,
    firstInstallmentDate: '2026-05-31',
    lastInstallmentDate: '2026-08-31',
    remarks: 'Recoverable in 4 equal parts monthly.'
  }
];

const initialState: FinesDamagesState = {
  fines: DEFAULT_FINES,
  damages: DEFAULT_DAMAGES
};

const finesDamagesSlice = createSlice({
  name: 'finesDamages',
  initialState,
  reducers: {
    addFine: (state, action: PayloadAction<FineRecord>) => {
      state.fines.unshift(action.payload);
    },
    updateFine: (state, action: PayloadAction<FineRecord>) => {
      const idx = state.fines.findIndex(f => f.id === action.payload.id);
      if (idx !== -1) {
        state.fines[idx] = action.payload;
      }
    },
    deleteFine: (state, action: PayloadAction<string>) => {
      state.fines = state.fines.filter(f => f.id !== action.payload);
    },
    addDamage: (state, action: PayloadAction<DamageRecord>) => {
      state.damages.unshift(action.payload);
    },
    updateDamage: (state, action: PayloadAction<DamageRecord>) => {
      const idx = state.damages.findIndex(d => d.id === action.payload.id);
      if (idx !== -1) {
        state.damages[idx] = action.payload;
      }
    },
    deleteDamage: (state, action: PayloadAction<string>) => {
      state.damages = state.damages.filter(d => d.id !== action.payload);
    }
  }
});

export const {
  addFine, updateFine, deleteFine,
  addDamage, updateDamage, deleteDamage
} = finesDamagesSlice.actions;

export default finesDamagesSlice.reducer;
