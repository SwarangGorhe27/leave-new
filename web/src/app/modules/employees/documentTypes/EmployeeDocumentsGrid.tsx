import { useCallback, useMemo, useState } from "react";
import {
  BriefcaseBusiness,
  Download,
  Eye,
  FileCheck2,
  FileText,
  Landmark,
  Pencil,
  ShieldCheck,
  Trash,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";
import type { EmployeeDocumentMeta } from "../../../components/employees/mockData";
import type { DocumentTypeConfig } from "./types";
import { fileTypesToAccept, getStorageKeys, validateFileAgainstTypes } from "./types";

export type EmployeeDocumentsMap = Partial<Record<string, EmployeeDocumentMeta>>;
type DocumentFilter = "all" | "personal" | "official" | "company";

interface Props {
  documentTypes: DocumentTypeConfig[];
  docs: EmployeeDocumentsMap;
  isEditing: boolean;
  onChange: (docs: EmployeeDocumentsMap) => void;
  showTypeControls?: boolean;
  onEditType?: (type: DocumentTypeConfig) => void;
  onRemoveType?: (type: DocumentTypeConfig) => void;
}

interface FrontBackPreview {
  front: EmployeeDocumentMeta | null;
  back: EmployeeDocumentMeta | null;
  docName: string;
}

function sideLabel(side: string | null): string | null {
  if (!side) return null;
  if (side === "front") return "Front Side";
  if (side === "back") return "Back Side";
  if (/^\d+$/.test(side)) return `File ${Number(side) + 1}`;
  return side;
}

function parseStorageKey(storageKey: string, typeId: string): string | null {
  if (storageKey === typeId) return null;
  return storageKey.replace(`${typeId}_`, "");
}

const DOCUMENT_SECTIONS = [
  {
    id: "personal",
    title: "Personal Documents",
    description: "Identity, KYC and address records",
    documentSection: "Personal",
    Icon: ShieldCheck,
  },
  {
    id: "official",
    title: "Official Documents",
    description: "Payroll, statutory, insurance and HR records",
    documentSection: "Official",
    Icon: Landmark,
  },
  {
    id: "company",
    title: "Company Documents",
    description: "Onboarding, employment and company-issued letters",
    documentSection: "Company",
    Icon: BriefcaseBusiness,
  },
] as const;

const FALLBACK_SECTION = {
  id: "other",
  title: "Other Documents",
  description: "Additional employee records",
  documentSection: "Company",
  Icon: FileText,
};

const DOCUMENT_FILTERS: { id: DocumentFilter; label: string; description: string }[] = [
  { id: "all", label: "All", description: "Every configured document" },
  { id: "personal", label: "Personal", description: "Documents assigned to the Personal section" },
  { id: "official", label: "Official", description: "Documents assigned to the Official section" },
  { id: "company", label: "Company", description: "Documents assigned to the Company section" },
];

function getDocumentSection(type: DocumentTypeConfig) {
  return DOCUMENT_SECTIONS.find((section) => section.documentSection === type.documentSection) || FALLBACK_SECTION;
}

function formatBytes(bytes?: number) {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getPreviewKind(fileName?: string) {
  if (!fileName) return "unsupported";
  if (/\.(png|jpe?g|gif|webp)$/i.test(fileName)) return "image";
  if (/\.pdf$/i.test(fileName)) return "pdf";
  return "unsupported";
}

export function EmployeeDocumentsGrid({
  documentTypes,
  docs,
  isEditing,
  onChange,
  showTypeControls,
  onEditType,
  onRemoveType,
}: Props) {
  const [progress, setProgress] = useState<Record<string, number>>({});
  const [err, setErr] = useState<string | null>(null);
  const [previewMeta, setPreviewMeta] = useState<EmployeeDocumentMeta | null>(null);
  const [frontBackPreview, setFrontBackPreview] = useState<FrontBackPreview | null>(null);
  const [activeFilter, setActiveFilter] = useState<DocumentFilter>("all");
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});
  const [verifiedDocs, setVerifiedDocs] = useState<Record<string, boolean>>({});

  const now = useMemo(() => new Date(), []);
  const [selectedSlipYear, setSelectedSlipYear] = useState<number>(now.getFullYear());
  const [selectedSlipMonth, setSelectedSlipMonth] = useState<number>(now.getMonth());

  const toggleRow = (id: string) => {
    setExpandedRows((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const [activeKeysState, setActiveKeysState] = useState<Record<string, string[]>>({});

  const getKeysForMultiple = useCallback((typeId: string) => {
    if (activeKeysState[typeId]) return activeKeysState[typeId];
    const existing = Object.keys(docs).filter((k) => new RegExp(`^${typeId}_\\d+$`).test(k));
    const base = [`${typeId}_0`, `${typeId}_1`, `${typeId}_2`];
    const combined = Array.from(new Set([...base, ...existing])).sort((a, b) => {
      const idxA = Number(a.split("_").pop());
      const idxB = Number(b.split("_").pop());
      return idxA - idxB;
    });
    return combined;
  }, [docs, activeKeysState]);

  const addSlot = (typeId: string) => {
    const currentKeys = getKeysForMultiple(typeId);
    const indices = currentKeys.map((k) => Number(k.split("_").pop())).filter((n) => !isNaN(n));
    const nextIdx = indices.length > 0 ? Math.max(...indices) + 1 : 0;
    const newKey = `${typeId}_${nextIdx}`;
    setActiveKeysState((prev) => ({
      ...prev,
      [typeId]: [...currentKeys, newKey],
    }));
  };

  const removeSlot = (typeId: string, storageKey: string) => {
    const updatedDocs = { ...docs };
    delete updatedDocs[storageKey];
    onChange(updatedDocs);
    const currentKeys = getKeysForMultiple(typeId);
    const updatedKeys = currentKeys.filter((k) => k !== storageKey);
    setActiveKeysState((prev) => ({
      ...prev,
      [typeId]: updatedKeys,
    }));
  };

  const getDynamicStorageKeys = (type: DocumentTypeConfig): string[] => {
    if (type.uploadType === "multiple") {
      return getKeysForMultiple(type.id);
    }
    return getStorageKeys(type);
  };

  const filteredDocumentTypes = useMemo(() => {
    if (activeFilter === "all") return documentTypes;
    return documentTypes.filter((type) => type.documentSection.toLowerCase() === activeFilter);
  }, [activeFilter, documentTypes]);

  const filteredStorageKeys = useMemo(() => filteredDocumentTypes.flatMap(getStorageKeys), [filteredDocumentTypes]);
  const filteredUploadedCount = filteredStorageKeys.filter((key) => docs[key]?.fileName).length;
  const filteredRequiredCount = filteredDocumentTypes.filter((type) => type.mandatory).length;

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const groupedDocumentTypes = useMemo(() => {
    const buckets = new Map<string, { section: ReturnType<typeof getDocumentSection>; types: DocumentTypeConfig[] }>();

    filteredDocumentTypes
      .slice()
      .sort((a, b) => a.displayOrder - b.displayOrder)
      .forEach((type) => {
        const section = getDocumentSection(type);
        const existing = buckets.get(section.id);
        if (existing) {
          existing.types.push(type);
        } else {
          buckets.set(section.id, { section, types: [type] });
        }
      });

    return [...buckets.values()];
  }, [filteredDocumentTypes]);

  const readFile = useCallback(
    (file: File, storageKey: string, type: DocumentTypeConfig) => {
      const e = validateFileAgainstTypes(file, type.allowedFileTypes);
      if (e) {
        setErr(e);
        return;
      }
      setErr(null);
      setProgress((p) => ({ ...p, [storageKey]: 10 }));
      const reader = new FileReader();
      reader.onprogress = (ev) => {
        if (ev.lengthComputable) {
          setProgress((p) => ({ ...p, [storageKey]: Math.round((ev.loaded / ev.total) * 90) + 10 }));
        }
      };
      reader.onload = () => {
        onChange({
          ...docs,
          [storageKey]: {
            fileName: file.name,
            dataUrl: String(reader.result || ""),
            uploadedAt: new Date().toISOString(),
            sizeBytes: file.size,
          },
        });
        setProgress((p) => ({ ...p, [storageKey]: 100 }));
        setTimeout(() => setProgress((p) => ({ ...p, [storageKey]: 0 })), 600);
      };
      reader.readAsDataURL(file);
    },
    [docs, onChange]
  );

  const download = (meta: EmployeeDocumentMeta) => {
    if (!meta.dataUrl || !meta.fileName) return;
    const a = document.createElement("a");
    a.href = meta.dataUrl;
    a.download = meta.fileName;
    a.click();
  };

  const previewDocument = (meta: EmployeeDocumentMeta) => {
    if (!meta.dataUrl || !meta.fileName) return;
    const previewKind = getPreviewKind(meta.fileName);
    if (previewKind === "unsupported") {
      download(meta);
      return;
    }
    setPreviewMeta(meta);
  };

  const remove = (storageKey: string) => {
    const n = { ...docs };
    delete n[storageKey];
    onChange(n);
  };

  const downloadAll = (type: DocumentTypeConfig) => {
    const keys =
      type.id === "salarySlips"
        ? Object.keys(docs).filter((k) => k.startsWith("salarySlips_"))
        : getStorageKeys(type);
    keys.forEach((key) => {
      const meta = docs[key];
      if (meta?.fileName && meta?.dataUrl) {
        download(meta);
      }
    });
  };

  const deleteAll = (type: DocumentTypeConfig) => {
    if (!window.confirm(`Delete all files for "${type.documentName}"?`)) return;
    const keys =
      type.id === "salarySlips"
        ? Object.keys(docs).filter((k) => k.startsWith("salarySlips_"))
        : getStorageKeys(type);
    const n = { ...docs };
    keys.forEach((key) => {
      delete n[key];
    });
    onChange(n);
  };

  const PROTECTED_IDS = ["panCard", "aadhaarCard", "educationalCertificates", "salarySlips", "insuranceDocuments"];

  if (!documentTypes.length) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        No document types configured. Add a document type to get started.
      </p>
    );
  }

  return (
    <>
      {err ? (
        <div className="mb-4 rounded-lg border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm font-medium text-destructive">
          {err}
        </div>
      ) : null}

      <div className="space-y-5">
        {/* Filter Bar */}
        <div className="rounded-2xl border border-border bg-background p-4">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-xs font-black uppercase tracking-widest text-muted-foreground">Document Category</p>
              <p className="mt-1 text-sm font-medium text-foreground">
                {DOCUMENT_FILTERS.find((filter) => filter.id === activeFilter)?.description}
              </p>
            </div>

            <div className="hidden flex-wrap items-center gap-2 md:flex">
              {DOCUMENT_FILTERS.map((filter) => {
                const active = activeFilter === filter.id;
                return (
                  <button
                    key={filter.id}
                    type="button"
                    onClick={() => setActiveFilter(filter.id)}
                    className={[
                      "rounded-full border px-4 py-2 text-xs font-black uppercase tracking-widest transition-colors",
                      active
                        ? "border-primary bg-primary text-primary-foreground"
                        : "border-border bg-card text-muted-foreground hover:bg-secondary hover:text-foreground",
                    ].join(" ")}
                  >
                    {filter.label}
                  </button>
                );
              })}
            </div>

            <select
              value={activeFilter}
              onChange={(e) => setActiveFilter(e.target.value as DocumentFilter)}
              className="h-10 rounded-lg border border-border bg-card px-3 text-xs font-black uppercase tracking-widest text-foreground md:hidden"
            >
              {DOCUMENT_FILTERS.map((filter) => (
                <option key={filter.id} value={filter.id}>
                  {filter.label}
                </option>
              ))}
            </select>

            <div className="flex flex-wrap items-center gap-2 text-[10px] font-black uppercase tracking-widest text-muted-foreground lg:justify-end">
              <span className="rounded-full border border-border bg-card px-3 py-1.5">
                {filteredUploadedCount}/{filteredStorageKeys.length} Uploaded
              </span>
              <span className="rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 text-amber-700">
                {filteredRequiredCount} Required
              </span>
            </div>
          </div>
        </div>

        {/* Unified Document Table */}
        <div className="overflow-hidden rounded-2xl border border-border bg-background shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left text-sm">
              <thead className="bg-secondary/40 border-b border-border text-xs font-black uppercase tracking-widest text-muted-foreground select-none">
                <tr>
                  <th scope="col" className="w-8 py-3.5 pl-4"></th>
                  <th scope="col" className="px-6 py-3.5">Document Name</th>
                  <th scope="col" className="px-6 py-3.5">Category</th>
                  <th scope="col" className="px-6 py-3.5">Uploaded Files</th>
                  <th scope="col" className="px-6 py-3.5 text-right pr-6">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {filteredDocumentTypes.map((type) => {
                  const typeStorageKeys = getDynamicStorageKeys(type);
                  const isExpandable = type.uploadType !== "single";
                  const isExpanded = !!expandedRows[type.id];
                  const accept = fileTypesToAccept(type.allowedFileTypes);
                  const completeCount =
                    type.id === "salarySlips"
                      ? Object.keys(docs).filter((k) => k.startsWith("salarySlips_") && docs[k]?.fileName).length
                      : typeStorageKeys.filter((key) => docs[key]?.fileName).length;
                  const singleKey = typeStorageKeys[0];
                  const singleMeta = docs[singleKey];
                  const isVerifiable =
                    type.id === "panCard" ||
                    type.id === "aadhaarCard" ||
                    Boolean(type.needsVerification) ||
                    type.id.toLowerCase().includes("bank") ||
                    type.id.toLowerCase().includes("passbook");

                  return (
                    <>
                      <tr key={type.id} className="hover:bg-secondary/5 transition-colors">
                        {/* Expand toggle cell */}
                        <td className="pl-4 py-4">
                          {isExpandable && (
                            <button
                              type="button"
                              onClick={() => toggleRow(type.id)}
                              className="flex h-5 w-5 items-center justify-center rounded text-muted-foreground hover:text-foreground"
                              title={isExpanded ? "Collapse" : "Expand"}
                            >
                              <span className="text-base leading-none">{isExpanded ? "▾" : "▸"}</span>
                            </button>
                          )}
                        </td>

                        {/* Document Name */}
                        <td className="px-6 py-4">
                          <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-bold text-foreground">{type.documentName}</span>
                              {type.mandatory && (
                                <span className="rounded-full bg-rose-50 border border-rose-100 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-rose-600">
                                  Required
                                </span>
                              )}
                              {isVerifiable && (
                                <label className="inline-flex items-center gap-1.5 cursor-pointer select-none ml-1">
                                  <input
                                    type="checkbox"
                                    checked={!!verifiedDocs[type.id]}
                                    onChange={(e) =>
                                      setVerifiedDocs((prev) => ({ ...prev, [type.id]: e.target.checked }))
                                    }
                                    className="h-3.5 w-3.5 rounded accent-emerald-600"
                                  />
                                  <span
                                    className={[
                                      "text-[10px] font-bold uppercase tracking-wider",
                                      verifiedDocs[type.id] ? "text-emerald-600" : "text-muted-foreground",
                                    ].join(" ")}
                                  >
                                    {verifiedDocs[type.id] ? "Verified" : "Verify"}
                                  </span>
                                </label>
                              )}
                            </div>
                            {!isExpandable && singleMeta?.fileName && (
                              <span className="text-[11px] text-muted-foreground mt-0.5 truncate max-w-xs font-mono">
                                📄 {singleMeta.fileName} ({formatBytes(singleMeta.sizeBytes)})
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Category */}
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center rounded-md bg-secondary/80 border border-border/70 px-2.5 py-0.5 text-xs font-bold text-foreground">
                            {type.category}
                          </span>
                        </td>

                        {/* Uploaded Files Count */}
                        <td className="px-6 py-4 font-mono text-xs font-semibold text-muted-foreground">
                          {type.id === "salarySlips"
                            ? `${completeCount} slip${completeCount !== 1 ? "s" : ""}`
                            : `${completeCount}/${typeStorageKeys.length} files`}
                        </td>

                        {/* Actions */}
                        <td className="px-6 py-4 text-right pr-6">
                          <div className="flex items-center justify-end gap-1.5">
                            {/* Single upload: preview + download if file exists */}
                            {!isExpandable && singleMeta?.fileName && (
                              <>
                                <button
                                  type="button"
                                  title="Preview"
                                  className="p-1.5 rounded-lg border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 transition-colors"
                                  onClick={() => previewDocument(singleMeta)}
                                >
                                  <Eye className="h-4 w-4" />
                                </button>
                                <button
                                  type="button"
                                  title="Download"
                                  className="p-1.5 rounded-lg border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 transition-colors"
                                  onClick={() => download(singleMeta)}
                                >
                                  <Download className="h-4 w-4" />
                                </button>
                              </>
                            )}

                            {/* Front/Back: side-by-side preview button */}
                            {type.uploadType === "frontBack" && completeCount > 0 && (
                              <button
                                type="button"
                                title="View side-by-side"
                                className="p-1.5 rounded-lg border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 transition-colors"
                                onClick={() => {
                                  setFrontBackPreview({
                                    front: docs[`${type.id}_front`] || null,
                                    back: docs[`${type.id}_back`] || null,
                                    docName: type.documentName,
                                  });
                                }}
                              >
                                <Eye className="h-4 w-4" />
                              </button>
                            )}

                            {/* Edit Document Settings */}
                            {((showTypeControls || !PROTECTED_IDS.includes(type.id)) && onEditType) && (
                              <button
                                type="button"
                                title="Edit Document Settings"
                                className="p-1.5 rounded-lg border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 transition-colors"
                                onClick={() => onEditType?.(type)}
                              >
                                <Pencil className="h-4 w-4" />
                              </button>
                            )}

                            {/* Single upload: upload / replace button */}
                            {!isExpandable && isEditing && (
                              <label className="cursor-pointer">
                                <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-dashed border-border bg-card text-xs font-bold text-muted-foreground hover:bg-secondary/50 hover:text-foreground transition-all">
                                  <UploadCloud className="h-3.5 w-3.5" />
                                  {singleMeta ? "Replace" : "Upload"}
                                </span>
                                <input
                                  type="file"
                                  accept={accept}
                                  className="hidden"
                                  onChange={(e) => {
                                    const f = e.target.files?.[0];
                                    if (f) readFile(f, singleKey, type);
                                    e.target.value = "";
                                  }}
                                />
                              </label>
                            )}

                            {/* Expandable: Edit Files / Collapse toggle */}
                            {isExpandable && isEditing && (
                              <button
                                type="button"
                                onClick={() => toggleRow(type.id)}
                                className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-border bg-card text-xs font-bold text-muted-foreground hover:bg-secondary/55 hover:text-foreground transition-all"
                              >
                                {isExpanded ? "Collapse" : "Edit Files"}
                              </button>
                            )}

                            {/* Expandable: Download All */}
                            {isExpandable && completeCount > 0 && (
                              <button
                                type="button"
                                title="Download all files"
                                className="p-1.5 rounded-lg border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 transition-colors"
                                onClick={() => downloadAll(type)}
                              >
                                <Download className="h-4 w-4" />
                              </button>
                            )}

                            {/* Single: Delete */}
                            {!isExpandable && singleMeta && isEditing && (
                              <button
                                type="button"
                                title="Delete file"
                                className="p-1.5 rounded-lg border border-destructive/20 bg-card text-destructive hover:bg-destructive/10 transition-colors"
                                onClick={() => remove(singleKey)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            )}

                            {/* Expandable: Delete All */}
                            {isExpandable && completeCount > 0 && isEditing && (
                              <button
                                type="button"
                                title="Delete all files"
                                className="p-1.5 rounded-lg border border-destructive/20 bg-card text-destructive hover:bg-destructive/10 transition-colors"
                                onClick={() => deleteAll(type)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            )}

                            {/* Delete Document Type */}
                            {!PROTECTED_IDS.includes(type.id) && onRemoveType && (
                              <button
                                type="button"
                                title="Delete Document Type"
                                className="p-1.5 rounded-lg border border-destructive/20 bg-card text-destructive hover:bg-destructive/10 transition-colors"
                                onClick={() => onRemoveType?.(type)}
                              >
                                <Trash className="h-3.5 w-3.5" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>

                      {/* Expandable Sub-Rows */}
                      {isExpandable && isExpanded && (
                        <tr key={`${type.id}-expanded`}>
                          {type.id === "salarySlips" ? (
                            <td colSpan={5} className="bg-secondary/10 px-6 py-4 border-t border-b border-border/40">
                              <div className="rounded-xl border border-border/80 bg-background overflow-hidden shadow-inner p-4">
                                {/* Month-wise filter */}
                                <div className="flex flex-wrap items-center gap-4 mb-4 pb-4 border-b border-border/60">
                                  <div className="flex flex-col gap-1">
                                    <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
                                      Select Year
                                    </label>
                                    <select
                                      value={selectedSlipYear}
                                      onChange={(e) => setSelectedSlipYear(Number(e.target.value))}
                                      className="h-9 rounded-lg border border-border bg-card px-3 text-xs font-bold text-foreground"
                                    >
                                      {[0, 1, 2, 3, 4].map((offset) => {
                                        const y = now.getFullYear() - offset;
                                        return (
                                          <option key={y} value={y}>
                                            {y}
                                          </option>
                                        );
                                      })}
                                    </select>
                                  </div>

                                  <div className="flex flex-col gap-1">
                                    <label className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
                                      Select Month
                                    </label>
                                    <select
                                      value={selectedSlipMonth}
                                      onChange={(e) => setSelectedSlipMonth(Number(e.target.value))}
                                      className="h-9 rounded-lg border border-border bg-card px-3 text-xs font-bold text-foreground"
                                    >
                                      {[
                                        "January", "February", "March", "April", "May", "June",
                                        "July", "August", "September", "October", "November", "December",
                                      ].map((m, idx) => (
                                        <option key={idx} value={idx}>
                                          {m}
                                        </option>
                                      ))}
                                    </select>
                                  </div>

                                  <div className="ml-auto text-xs font-semibold text-muted-foreground">
                                    Total Slips Uploaded:{" "}
                                    <span className="font-black text-foreground">{completeCount}</span>
                                  </div>
                                </div>

                                {/* Selected month slip */}
                                {(() => {
                                  const key = `salarySlips_${selectedSlipYear}-${String(selectedSlipMonth + 1).padStart(2, "0")}`;
                                  const meta = docs[key];
                                  const pct = progress[key] || 0;
                                  const monthName = [
                                    "January", "February", "March", "April", "May", "June",
                                    "July", "August", "September", "October", "November", "December",
                                  ][selectedSlipMonth];

                                  return (
                                    <div className="flex flex-col gap-3">
                                      <div className="flex items-center justify-between">
                                        <h4 className="text-xs font-bold text-foreground">
                                          Salary Slip for {monthName} {selectedSlipYear}
                                        </h4>
                                      </div>

                                      {meta?.fileName ? (
                                        <div className="flex items-center justify-between gap-2 rounded-xl border border-border bg-secondary/20 p-3">
                                          <div className="flex min-w-0 items-center gap-2">
                                            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-600">
                                              <FileCheck2 className="h-4 w-4" />
                                            </div>
                                            <div className="min-w-0">
                                              <p className="truncate text-xs font-bold text-foreground font-mono">
                                                {meta.fileName}
                                              </p>
                                              <p className="text-[10px] font-medium text-muted-foreground">
                                                Uploaded · {formatBytes(meta.sizeBytes)}
                                              </p>
                                            </div>
                                          </div>
                                          <div className="flex flex-shrink-0 items-center gap-1.5">
                                            <button
                                              type="button"
                                              title="Preview"
                                              className="p-1.5 rounded-lg border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 transition-colors"
                                              onClick={() => previewDocument(meta)}
                                            >
                                              <Eye className="h-4 w-4" />
                                            </button>
                                            <button
                                              type="button"
                                              title="Download"
                                              className="p-1.5 rounded-lg border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 transition-colors"
                                              onClick={() => download(meta)}
                                            >
                                              <Download className="h-4 w-4" />
                                            </button>
                                            {isEditing && (
                                              <button
                                                type="button"
                                                title="Delete"
                                                className="p-1.5 rounded-lg border border-destructive/20 bg-card text-destructive hover:bg-destructive/10 transition-colors"
                                                onClick={() => remove(key)}
                                              >
                                                <Trash2 className="h-4 w-4" />
                                              </button>
                                            )}
                                          </div>
                                        </div>
                                      ) : (
                                        <div className="rounded-xl border border-dashed border-border bg-secondary/5 p-4 text-center">
                                          <span className="text-xs text-muted-foreground italic">
                                            No slip uploaded for this month
                                          </span>
                                        </div>
                                      )}

                                      {pct > 0 && pct < 100 && (
                                        <div className="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                                          <div
                                            className="h-full bg-primary transition-all duration-300"
                                            style={{ width: `${pct}%` }}
                                          />
                                        </div>
                                      )}

                                      {isEditing && (
                                        <label className="cursor-pointer mt-1">
                                          <span className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg border border-dashed border-border bg-card text-xs font-bold text-muted-foreground hover:bg-secondary/50 hover:text-foreground transition-all w-full">
                                            <UploadCloud className="h-4 w-4" />
                                            {meta ? "Replace Slip" : "Upload Salary Slip"}
                                          </span>
                                          <input
                                            type="file"
                                            accept={accept}
                                            className="hidden"
                                            onChange={(e) => {
                                              const f = e.target.files?.[0];
                                              if (f) readFile(f, key, type);
                                              e.target.value = "";
                                            }}
                                          />
                                        </label>
                                      )}
                                    </div>
                                  );
                                })()}
                              </div>
                            </td>
                          ) : (
                            <td colSpan={5} className="bg-secondary/10 px-6 py-4 border-t border-b border-border/40">
                              <div className="rounded-xl border border-border/80 bg-background overflow-hidden shadow-inner">
                                <table className="w-full border-collapse text-left text-xs">
                                  <thead>
                                    <tr className="bg-secondary/20 border-b border-border/70 text-[10px] font-black uppercase tracking-wider text-muted-foreground select-none">
                                      <th className="px-4 py-2.5 w-1/4">Side / File Slot</th>
                                      <th className="px-4 py-2.5 w-2/5">File Details</th>
                                      <th className="px-4 py-2.5 text-right pr-4">Actions</th>
                                    </tr>
                                  </thead>
                                  <tbody className="divide-y divide-border/50">
                                    {typeStorageKeys.map((storageKey) => {
                                      const side = parseStorageKey(storageKey, type.id);
                                      const meta = docs[storageKey];
                                      const pct = progress[storageKey] || 0;
                                      const sideTitle = sideLabel(side);

                                      return (
                                        <tr key={storageKey} className="hover:bg-secondary/5 transition-colors">
                                          <td className="px-4 py-3 font-semibold text-foreground">
                                            {sideTitle || "File Slot"}
                                          </td>

                                          <td className="px-4 py-3">
                                            {meta?.fileName ? (
                                              <div className="flex flex-col min-w-0">
                                                <span className="font-bold text-foreground truncate max-w-sm font-mono">
                                                  {meta.fileName}
                                                </span>
                                                <span className="text-[10px] text-muted-foreground mt-0.5">
                                                  Size: {formatBytes(meta.sizeBytes)}
                                                </span>
                                              </div>
                                            ) : (
                                              <span className="text-muted-foreground italic font-medium">
                                                No file uploaded
                                              </span>
                                            )}
                                            {pct > 0 && pct < 100 && (
                                              <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                                                <div
                                                  className="h-full bg-primary transition-all duration-300"
                                                  style={{ width: `${pct}%` }}
                                                />
                                              </div>
                                            )}
                                          </td>

                                          <td className="px-4 py-3 text-right pr-4">
                                            <div className="flex items-center justify-end gap-1.5">
                                              {meta?.fileName && (
                                                <>
                                                  <button
                                                    type="button"
                                                    title="Preview"
                                                    className="p-1 rounded border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 transition-colors"
                                                    onClick={() => previewDocument(meta)}
                                                  >
                                                    <Eye className="h-3.5 w-3.5" />
                                                  </button>
                                                  <button
                                                    type="button"
                                                    title="Download"
                                                    className="p-1 rounded border border-border bg-card text-muted-foreground hover:text-foreground hover:bg-secondary/40 transition-colors"
                                                    onClick={() => download(meta)}
                                                  >
                                                    <Download className="h-3.5 w-3.5" />
                                                  </button>
                                                </>
                                              )}

                                              {isEditing && (
                                                <label className="cursor-pointer">
                                                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded border border-dashed border-border bg-card text-[10px] font-bold text-muted-foreground hover:bg-secondary/50 hover:text-foreground transition-all">
                                                    <UploadCloud className="h-3 w-3" />
                                                    {meta ? "Replace" : "Upload"}
                                                  </span>
                                                  <input
                                                    type="file"
                                                    accept={accept}
                                                    className="hidden"
                                                    onChange={(e) => {
                                                      const f = e.target.files?.[0];
                                                      if (f) readFile(f, storageKey, type);
                                                      e.target.value = "";
                                                    }}
                                                  />
                                                </label>
                                              )}

                                              {isEditing && (type.uploadType === "multiple" || meta) && (
                                                <button
                                                  type="button"
                                                  title={
                                                    type.uploadType === "multiple" ? "Delete slot" : "Delete file"
                                                  }
                                                  className="p-1 rounded border border-destructive/20 bg-card text-destructive hover:bg-destructive/10 transition-colors"
                                                  onClick={() => {
                                                    if (type.uploadType === "multiple") {
                                                      removeSlot(type.id, storageKey);
                                                    } else {
                                                      remove(storageKey);
                                                    }
                                                  }}
                                                >
                                                  <Trash2 className="h-3.5 w-3.5" />
                                                </button>
                                              )}
                                            </div>
                                          </td>
                                        </tr>
                                      );
                                    })}
                                  </tbody>
                                </table>
                                {type.uploadType === "multiple" && isEditing && (
                                  <div className="px-4 py-2.5 border-t border-border/50 bg-secondary/5">
                                    <button
                                      type="button"
                                      onClick={() => addSlot(type.id)}
                                      className="inline-flex items-center gap-1.5 text-[11px] font-bold text-primary hover:underline"
                                    >
                                      <span className="text-base leading-none">+</span> Add Document
                                    </button>
                                  </div>
                                )}
                              </div>
                            </td>
                          )}
                        </tr>
                      )}
                    </>
                  );
                })}

                {filteredDocumentTypes.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-10 text-center text-sm font-semibold text-muted-foreground">
                      No documents found in this category
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Single document preview modal */}
      {previewMeta ? (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/55 p-4"
          onClick={() => setPreviewMeta(null)}
        >
          <div
            className="flex h-[88vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-4">
              <div className="min-w-0">
                <h3 className="truncate text-sm font-black uppercase tracking-widest text-foreground">
                  Document Preview
                </h3>
                <p className="mt-0.5 truncate text-xs font-medium text-muted-foreground">{previewMeta.fileName}</p>
              </div>
              <div className="flex flex-shrink-0 items-center gap-2">
                <button
                  type="button"
                  title="Download"
                  className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border hover:bg-secondary"
                  onClick={() => download(previewMeta)}
                >
                  <Download className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  title="Close"
                  className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border hover:bg-secondary"
                  onClick={() => setPreviewMeta(null)}
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
            <div className="min-h-0 flex-1 bg-secondary/20 p-4">
              {getPreviewKind(previewMeta.fileName) === "image" ? (
                <div className="flex h-full items-center justify-center overflow-auto rounded-xl bg-background">
                  <img
                    src={previewMeta.dataUrl}
                    alt={previewMeta.fileName || "Document preview"}
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
              ) : (
                <iframe
                  title={previewMeta.fileName || "Document preview"}
                  src={previewMeta.dataUrl}
                  className="h-full w-full rounded-xl border border-border bg-background"
                />
              )}
            </div>
          </div>
        </div>
      ) : null}

      {/* Front / Back side-by-side preview modal */}
      {frontBackPreview ? (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/55 p-4"
          onClick={() => setFrontBackPreview(null)}
        >
          <div
            className="flex h-[88vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-4">
              <div className="min-w-0">
                <h3 className="truncate text-sm font-black uppercase tracking-widest text-foreground">
                  {frontBackPreview.docName}
                </h3>
                <p className="mt-0.5 text-xs font-medium text-muted-foreground">Front &amp; Back</p>
              </div>
              <button
                type="button"
                title="Close"
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border hover:bg-secondary"
                onClick={() => setFrontBackPreview(null)}
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="min-h-0 flex-1 grid grid-cols-2 gap-4 bg-secondary/20 p-4">
              {(["front", "back"] as const).map((side) => {
                const meta = frontBackPreview[side];
                return (
                  <div key={side} className="flex flex-col gap-2 overflow-hidden rounded-xl border border-border bg-background">
                    <p className="px-3 pt-3 text-[10px] font-black uppercase tracking-widest text-muted-foreground">
                      {side === "front" ? "Front Side" : "Back Side"}
                    </p>
                    {meta?.dataUrl ? (
                      getPreviewKind(meta.fileName) === "image" ? (
                        <div className="flex flex-1 items-center justify-center overflow-auto p-2">
                          <img
                            src={meta.dataUrl}
                            alt={meta.fileName || side}
                            className="max-h-full max-w-full object-contain"
                          />
                        </div>
                      ) : (
                        <iframe
                          title={meta.fileName || side}
                          src={meta.dataUrl}
                          className="h-full w-full border-0"
                        />
                      )
                    ) : (
                      <div className="flex flex-1 items-center justify-center text-xs text-muted-foreground italic">
                        No file uploaded
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}