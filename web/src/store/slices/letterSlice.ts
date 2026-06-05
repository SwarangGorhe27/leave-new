import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface LetterTemplate {
  id: string;
  name: string;
  category: string;
  description: string;
  enabled: boolean;
  lastModified: string;
  owner: string[];
  suppressZeroPayroll: boolean;
  enforceLetter: 'Not Required' | 'Accept Only' | 'Acknowledge Only' | 'Accept or Reject';
  numberSeries: {
    type: 'Default Serial Number' | 'Custom Series';
    prefix?: string;
    startNumber?: string;
    suffix?: string;
  };
  mailTemplate: 'None' | 'Letter Default';
  enableDigitalSignature: boolean;
  customFields: CustomField[];
  templateFile?: {
    name: string;
    size: number;
    url: string;
  };
  workflow: {
    canRequest: boolean;
    autoApproval: boolean;
    hrApproval: boolean;
    managerApproval: boolean;
  };
}

export interface CustomField {
  id: string;
  name: string;
  label: string;
  type: 'Text' | 'Number' | 'Date' | 'Dropdown' | 'Textarea' | 'Checkbox' | 'File Upload';
  required: boolean;
  listValues?: string[];
  allowEmployeeEdit: boolean;
}

interface LetterState {
  templates: LetterTemplate[];
  loading: boolean;
}

const DEFAULT_TEMPLATES: LetterTemplate[] = [
  {
    id: 'tpl-1',
    name: 'Standard Offer Letter',
    category: 'Onboarding',
    description: 'Official offer letter for new hires',
    enabled: true,
    lastModified: '2024-05-10',
    owner: ['admin', 'recruit1'],
    suppressZeroPayroll: true,
    enforceLetter: 'Accept or Reject',
    numberSeries: { type: 'Default Serial Number' },
    mailTemplate: 'Letter Default',
    enableDigitalSignature: true,
    customFields: [],
    workflow: { canRequest: false, autoApproval: false, hrApproval: true, managerApproval: false }
  },
  {
    id: 'tpl-2',
    name: 'Relieving cum Experience Certificate',
    category: 'Offboarding',
    description: 'Letter issued at the time of employee exit',
    enabled: true,
    lastModified: '2024-05-12',
    owner: ['admin'],
    suppressZeroPayroll: false,
    enforceLetter: 'Not Required',
    numberSeries: { type: 'Custom Series', prefix: 'REL', startNumber: '1001', suffix: '2024' },
    mailTemplate: 'None',
    enableDigitalSignature: true,
    customFields: [],
    workflow: { canRequest: true, autoApproval: false, hrApproval: true, managerApproval: true }
  }
];

const initialState: LetterState = {
  templates: DEFAULT_TEMPLATES,
  loading: false,
};

const letterSlice = createSlice({
  name: 'letter',
  initialState,
  reducers: {
    addTemplate: (state, action: PayloadAction<LetterTemplate>) => {
      state.templates.unshift(action.payload);
    },
    updateTemplate: (state, action: PayloadAction<LetterTemplate>) => {
      const index = state.templates.findIndex(t => t.id === action.payload.id);
      if (index !== -1) {
        state.templates[index] = action.payload;
      }
    },
    deleteTemplate: (state, action: PayloadAction<string>) => {
      state.templates = state.templates.filter(t => t.id !== action.payload);
    },
    toggleTemplateStatus: (state, action: PayloadAction<string>) => {
      const template = state.templates.find(t => t.id === action.payload);
      if (template) {
        template.enabled = !template.enabled;
      }
    },
    duplicateTemplate: (state, action: PayloadAction<string>) => {
      const template = state.templates.find(t => t.id === action.payload);
      if (template) {
        const newTemplate = {
          ...template,
          id: `tpl-${Date.now()}`,
          name: `${template.name} (Copy)`,
          lastModified: new Date().toISOString().split('T')[0]
        };
        state.templates.unshift(newTemplate);
      }
    }
  },
});

export const { addTemplate, updateTemplate, deleteTemplate, toggleTemplateStatus, duplicateTemplate } = letterSlice.actions;
export default letterSlice.reducer;
