import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../../../components/ui/dialog";
import { Button } from "../../../components/ui/button";
import { Label } from "../../../components/ui/label";
import { Input } from "../../../components/ui/input";
import {
  ALLOWED_FILE_TYPE_OPTIONS,
  DOCUMENT_SECTION_OPTIONS,
  UPLOAD_TYPE_OPTIONS,
  type AllowedFileType,
  type DocumentSection,
  type DocumentTypeConfig,
  type DocumentUploadType,
  slugifyDocumentId,
} from "./types";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initial?: DocumentTypeConfig | null;
  existingIds: string[];
  onSave: (config: DocumentTypeConfig) => void;
}

const emptyForm = (): Omit<DocumentTypeConfig, "id"> & { id: string, needsVerification?: boolean } => ({
  id: "",
  documentName: "",
  documentSection: "Personal",
  category: "General",
  uploadType: "single",
  allowedFileTypes: ["pdf", "jpg", "png"],
  mandatory: false,
  allowEmployeeEdit: true,
  displayOrder: 100,
  status: "Active",
  needsVerification: false,
});

export function DocumentTypeModal({ open, onOpenChange, initial, existingIds, onSave }: Props) {
  const [form, setForm] = useState(emptyForm());
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    if (initial) {
      setForm({ ...initial });
    } else {
      setForm(emptyForm());
    }
    setError(null);
  }, [open, initial]);

  const toggleFileType = (ft: AllowedFileType) => {
    setForm((f) => {
      const has = f.allowedFileTypes.includes(ft);
      const next = has ? f.allowedFileTypes.filter((x) => x !== ft) : [...f.allowedFileTypes, ft];
      return { ...f, allowedFileTypes: next.length ? next : [ft] };
    });
  };

  const handleSubmit = () => {
    if (!form.documentName.trim()) {
      setError("Document name is required");
      return;
    }
    if (!form.category.trim()) {
      setError("Document category is required");
      return;
    }
    if (!form.documentSection) {
      setError("Document section is required");
      return;
    }
    if (!form.allowedFileTypes.length) {
      setError("Select at least one allowed file type");
      return;
    }
    const id = initial?.id || slugifyDocumentId(form.documentName);
    if (!id) {
      setError("Could not generate document key — use a valid name");
      return;
    }
    if (!initial && existingIds.includes(id)) {
      setError("A document type with this name already exists");
      return;
    }
    onSave({
      id,
      documentName: form.documentName.trim(),
      documentSection: form.documentSection,
      category: form.category.trim(),
      uploadType: form.uploadType,
      allowedFileTypes: form.allowedFileTypes,
      mandatory: form.mandatory,
      allowEmployeeEdit: form.allowEmployeeEdit,
      displayOrder: Number(form.displayOrder) || 100,
      status: form.status,
      isSystem: initial?.isSystem,
      needsVerification: form.needsVerification,
    });
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{initial ? "Edit Document Type" : "Add New Document Type"}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {error ? <p className="text-sm text-destructive font-medium">{error}</p> : null}

          <div className="space-y-1.5">
            <Label>Document Name</Label>
            <Input
              value={form.documentName}
              onChange={(e) => setForm((f) => ({ ...f, documentName: e.target.value }))}
              placeholder="e.g. Driving Licence"
            />
          </div>

          <div className="space-y-1.5">
            <Label>Document Category</Label>
            <Input
              value={form.category}
              onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
              placeholder="e.g. KYC, Onboarding"
            />
          </div>

          <div className="space-y-1.5">
            <Label>Document Section</Label>
            <select
              value={form.documentSection}
              onChange={(e) => setForm((f) => ({ ...f, documentSection: e.target.value as DocumentSection }))}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              {DOCUMENT_SECTION_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <Label>Upload Type</Label>
            <div className="flex flex-col gap-2">
              {UPLOAD_TYPE_OPTIONS.map((opt) => (
                <label key={opt.value} className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="radio"
                    name="uploadType"
                    checked={form.uploadType === opt.value}
                    onChange={() => setForm((f) => ({ ...f, uploadType: opt.value as DocumentUploadType }))}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label>Allowed File Types</Label>
            <div className="flex flex-wrap gap-3">
              {ALLOWED_FILE_TYPE_OPTIONS.map((opt) => (
                <label key={opt.value} className="flex items-center gap-1.5 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.allowedFileTypes.includes(opt.value)}
                    onChange={() => toggleFileType(opt.value)}
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Mandatory</Label>
              <div className="flex gap-4 text-sm">
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="radio"
                    checked={form.mandatory === true}
                    onChange={() => setForm((f) => ({ ...f, mandatory: true }))}
                  />
                  Yes
                </label>
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="radio"
                    checked={form.mandatory === false}
                    onChange={() => setForm((f) => ({ ...f, mandatory: false }))}
                  />
                  No
                </label>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Status</Label>
              <div className="flex gap-4 text-sm">
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="radio"
                    checked={form.status === "Active"}
                    onChange={() => setForm((f) => ({ ...f, status: "Active" }))}
                  />
                  Active
                </label>
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="radio"
                    checked={form.status === "Inactive"}
                    onChange={() => setForm((f) => ({ ...f, status: "Inactive" }))}
                  />
                  Inactive
                </label>
              </div>
            </div>
          </div>

          <div className="space-y-2 py-1">
            <label className="flex items-center gap-2 text-sm font-semibold cursor-pointer text-foreground select-none">
              <input
                type="checkbox"
                checked={Boolean(form.needsVerification)}
                onChange={(e) => setForm((f) => ({ ...f, needsVerification: e.target.checked }))}
                className="h-4 w-4 rounded border-input text-primary focus:ring-primary accent-primary"
              />
              Needs Verification (e.g. name as per Aadhaar/PAN Card)
            </label>
          </div>

          <div className="space-y-1.5">
            <Label>Display Order / Sequence</Label>
            <Input
              type="number"
              min={1}
              value={form.displayOrder}
              onChange={(e) => setForm((f) => ({ ...f, displayOrder: Number(e.target.value) }))}
            />
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button type="button" onClick={handleSubmit}>
            {initial ? "Save Changes" : "Add Document Type"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
