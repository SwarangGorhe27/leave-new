import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import type { DocumentTypeConfig } from "../../app/modules/employees/documentTypes/types";
import { inferDocumentSection } from "../../app/modules/employees/documentTypes/types";
import { buildDefaultDocumentTypes } from "../../app/modules/employees/documentTypes/defaultDocumentTypes";

const STORAGE_KEY = "hrms_employee_document_types_v1";

function loadFromStorage(): DocumentTypeConfig[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return buildDefaultDocumentTypes();
    const parsed = JSON.parse(raw) as DocumentTypeConfig[];
    if (!Array.isArray(parsed) || !parsed.length) return buildDefaultDocumentTypes();
    let migrated = false;
    const result = parsed.map((type) => {
      let uploadType = type.uploadType;
      if (type.id === "insuranceDocuments" && uploadType !== "multiple") {
        uploadType = "multiple";
        migrated = true;
      }
      return {
        ...type,
        uploadType,
        documentSection: type.documentSection || inferDocumentSection(type.category || "General"),
      };
    });
    if (migrated) {
      persist(result);
    }
    return result;
  } catch {
    return buildDefaultDocumentTypes();
  }
}

function persist(types: DocumentTypeConfig[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(types));
}

interface DocumentTypesState {
  types: DocumentTypeConfig[];
}

const initialState: DocumentTypesState = {
  types: loadFromStorage(),
};

const documentTypesSlice = createSlice({
  name: "documentTypes",
  initialState,
  reducers: {
    setDocumentTypes(state, action: PayloadAction<DocumentTypeConfig[]>) {
      state.types = action.payload;
      persist(action.payload);
    },
    addDocumentType(state, action: PayloadAction<DocumentTypeConfig>) {
      state.types = [...state.types, action.payload].sort((a, b) => a.displayOrder - b.displayOrder);
      persist(state.types);
    },
    updateDocumentType(state, action: PayloadAction<DocumentTypeConfig>) {
      state.types = state.types
        .map((t) => (t.id === action.payload.id ? action.payload : t))
        .sort((a, b) => a.displayOrder - b.displayOrder);
      persist(state.types);
    },
    removeDocumentType(state, action: PayloadAction<string>) {
      state.types = state.types.filter((t) => t.id !== action.payload);
      persist(state.types);
    },
    resetDocumentTypes(state) {
      state.types = buildDefaultDocumentTypes();
      persist(state.types);
    },
  },
});

export const { setDocumentTypes, addDocumentType, updateDocumentType, removeDocumentType, resetDocumentTypes } =
  documentTypesSlice.actions;

export default documentTypesSlice.reducer;

export const selectDocumentTypes = (state: { documentTypes: DocumentTypesState }) => state.documentTypes.types;

export const selectActiveDocumentTypes = (state: { documentTypes: DocumentTypesState }) =>
  state.documentTypes.types
    .filter((t) => t.status === "Active")
    .sort((a, b) => a.displayOrder - b.displayOrder);
