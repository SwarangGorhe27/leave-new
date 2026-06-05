import { useState } from "react";
import { FileText } from "lucide-react";
import { toast } from "sonner";
import { Employee } from "../mockData";
import { useAdminSync } from "../../admin/useAdminSync";
import { EditableSectionCard } from "../employee-details";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../../../store";
import {
  addDocumentType,
  removeDocumentType,
  selectActiveDocumentTypes,
  updateDocumentType,
} from "../../../../store/slices/documentTypesSlice";
import { DocumentTypeModal } from "../../../modules/employees/documentTypes/DocumentTypeModal";
import { EmployeeDocumentsGrid } from "../../../modules/employees/documentTypes/EmployeeDocumentsGrid";
import type { DocumentTypeConfig } from "../../../modules/employees/documentTypes/types";

interface Props {
  employee: Employee;
  showAddButton?: boolean;
}

export function EmployeeDocumentsSection({ employee, showAddButton = true }: Props) {
  const dispatch = useDispatch<AppDispatch>();
  const documentTypes = useSelector(selectActiveDocumentTypes);
  const { handleAdminSave, handleToggleEditAccess } = useAdminSync();

  // --- Document Management state ---
  const [docs, setDocs] = useState(() => ({ ...(employee.employeeDocuments || {}) }));
  const [modalOpen, setModalOpen] = useState(false);
  const [editingType, setEditingType] = useState<DocumentTypeConfig | null>(null);
  const isEditable = employee.editableSections?.includes("employee-documents");
  const existingIds = useSelector((s: RootState) => s.documentTypes.types.map((t) => t.id));

  const handleDocsChange = async (updatedDocs: typeof docs) => {
    setDocs(updatedDocs);
    await handleAdminSave("Employee Documents", employee, {
      ...employee,
      employeeDocuments: updatedDocs,
    });
  };

  const handleSaveType = (config: DocumentTypeConfig) => {
    if (editingType) {
      dispatch(updateDocumentType(config));
      toast.success(`"${config.documentName}" updated`);
    } else {
      dispatch(addDocumentType(config));
      toast.success(`"${config.documentName}" added to document list`);
    }
    setEditingType(null);
  };

  const handleRemoveType = (type: DocumentTypeConfig) => {
    const isProtected = ["panCard", "aadhaarCard", "educationalCertificates", "salarySlips", "insuranceDocuments"].includes(type.id);
    if (isProtected) return;
    if (!window.confirm(`Remove document type "${type.documentName}"?`)) return;
    dispatch(removeDocumentType(type.id));
    setDocs((d) => {
      const n = { ...d };
      Object.keys(n).forEach((k) => {
        if (k === type.id || k.startsWith(`${type.id}_`)) delete n[k];
      });
      return n;
    });
  };

  return (
    <div className="space-y-5 pb-24">
      <div>
        <h2 className="text-lg font-bold text-foreground">Employee Documents</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Upload and manage documents for {employee.name}
        </p>
      </div>

      {/* ── General Document Management Card ── */}
      <EditableSectionCard
        title="Document Management"
        icon={FileText}
        sectionId="employee-documents"
        canEmployeeEdit={isEditable}
        onToggleEmployeeEdit={(v) => handleToggleEditAccess(employee, "employee-documents", v)}
        requestStatus={employee.editRequestStatus}
        isEditing={false}
        onSave={() => {}}
        onCancel={() => {}}
        headerExtra={showAddButton ? (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => { setEditingType(null); setModalOpen(true); }}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-bold hover:bg-secondary transition-colors"
            >
              Add New Document
            </button>
          </div>
        ) : null}
      >
        <EmployeeDocumentsGrid
          documentTypes={documentTypes}
          docs={docs}
          isEditing={true}
          onChange={handleDocsChange}
          showTypeControls={showAddButton}
          onEditType={(type) => {
            setEditingType(type);
            setModalOpen(true);
          }}
          onRemoveType={handleRemoveType}
        />
      
      </EditableSectionCard>

      <DocumentTypeModal
        open={modalOpen}
        onOpenChange={(open) => {
          setModalOpen(open);
          if (!open) setEditingType(null);
        }}
        initial={editingType}
        existingIds={existingIds}
        onSave={handleSaveType}
      />
    </div>
  );
}
