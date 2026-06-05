import { useState, useRef } from "react";
import {
  Download,
  Eye,
  Trash2,
  UploadCloud,
  X,
  ChevronLeft,
  ChevronRight,
  FileText,
  Calendar,
  CheckCircle2,
} from "lucide-react";
import type { EmployeeDocumentMeta } from "../../components/employees/mockData";

export type SalarySlipsByMonth = Partial<Record<string, EmployeeDocumentMeta>>;
// Key format: "YYYY-MM"

interface Props {
  slips: SalarySlipsByMonth;
  isEditing: boolean;
  onChange: (slips: SalarySlipsByMonth) => void;
}

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

const MONTH_FULL = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function getPreviewKind(fileName?: string) {
  if (!fileName) return "unsupported";
  if (/\.(png|jpe?g|gif|webp)$/i.test(fileName)) return "image";
  if (/\.pdf$/i.test(fileName)) return "pdf";
  return "unsupported";
}

function formatBytes(bytes?: number): string {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function monthKey(year: number, month: number): string {
  return `${year}-${String(month + 1).padStart(2, "0")}`;
}

export function SalarySlipCalendar({ slips, isEditing, onChange }: Props) {
  const now = new Date();
  const [viewYear, setViewYear] = useState(now.getFullYear());
  const [preview, setPreview] = useState<{ meta: EmployeeDocumentMeta; label: string } | null>(null);
  const [uploading, setUploading] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [pendingKey, setPendingKey] = useState<string | null>(null);

  // Generate last 3 years + current for year navigation
  const currentYear = now.getFullYear();
  const minYear = currentYear - 4;

  const triggerUpload = (key: string) => {
    setPendingKey(key);
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !pendingKey) return;
    setUploading(pendingKey);
    const reader = new FileReader();
    reader.onload = () => {
      onChange({
        ...slips,
        [pendingKey]: {
          fileName: file.name,
          dataUrl: String(reader.result || ""),
          uploadedAt: new Date().toISOString(),
          sizeBytes: file.size,
        },
      });
      setUploading(null);
    };
    reader.readAsDataURL(file);
    e.target.value = "";
  };

  const handleRemove = (key: string) => {
    if (!window.confirm("Remove this salary slip?")) return;
    const n = { ...slips };
    delete n[key];
    onChange(n);
  };

  const handleDownload = (meta: EmployeeDocumentMeta) => {
    if (!meta.dataUrl || !meta.fileName) return;
    const a = document.createElement("a");
    a.href = meta.dataUrl;
    a.download = meta.fileName;
    a.click();
  };

  const handlePreview = (meta: EmployeeDocumentMeta, label: string) => {
    if (!meta.dataUrl || !meta.fileName) return;
    if (getPreviewKind(meta.fileName) === "unsupported") {
      handleDownload(meta);
      return;
    }
    setPreview({ meta, label });
  };

  // Count of uploaded slips for this year
  const uploadedThisYear = MONTHS.filter((_, i) => {
    const key = monthKey(viewYear, i);
    return !!slips[key]?.fileName;
  }).length;

  return (
    <>
      {/* Hidden shared file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.jpg,.jpeg,.png"
        className="hidden"
        onChange={handleFileChange}
      />

      <div className="space-y-5">
        {/* Year navigator */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 rounded-xl border border-border bg-card px-1 py-1">
              <button
                type="button"
                onClick={() => setViewYear((y) => Math.max(minYear, y - 1))}
                disabled={viewYear <= minYear}
                className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors disabled:opacity-30 disabled:pointer-events-none"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="min-w-[60px] text-center text-sm font-black text-foreground tabular-nums">
                {viewYear}
              </span>
              <button
                type="button"
                onClick={() => setViewYear((y) => Math.min(currentYear, y + 1))}
                disabled={viewYear >= currentYear}
                className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors disabled:opacity-30 disabled:pointer-events-none"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
            <span className="text-xs font-semibold text-muted-foreground">
              <span className="font-black text-primary">{uploadedThisYear}</span> / 12 slips uploaded
            </span>
          </div>

          <div className="flex items-center gap-2 text-[11px] font-bold text-muted-foreground">
            <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-emerald-700">
              <CheckCircle2 className="h-3 w-3" /> Uploaded
            </span>
            <span className="inline-flex items-center gap-1 rounded-full border border-border bg-card px-2.5 py-1">
              <Calendar className="h-3 w-3" /> Pending
            </span>
          </div>
        </div>

        {/* Month calendar grid */}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
          {MONTHS.map((month, i) => {
            const key = monthKey(viewYear, i);
            const meta = slips[key];
            const hasSlip = !!meta?.fileName;
            const isCurrentMonth = viewYear === currentYear && i === now.getMonth();
            const isFuture = viewYear === currentYear && i > now.getMonth();
            const isUploadingThis = uploading === key;

            return (
              <div
                key={key}
                className={[
                  "relative flex flex-col rounded-xl border p-3 transition-all duration-200",
                  hasSlip
                    ? "border-emerald-200 bg-emerald-50/60 shadow-sm"
                    : isFuture
                    ? "border-border/40 bg-secondary/10 opacity-50"
                    : "border-border bg-card hover:border-primary/30 hover:shadow-sm",
                  isCurrentMonth && !hasSlip ? "ring-2 ring-primary/20" : "",
                ].join(" ")}
              >
                {/* Month label */}
                <div className="mb-2 flex items-center justify-between">
                  <div>
                    <p className={["text-sm font-black", hasSlip ? "text-emerald-700" : "text-foreground"].join(" ")}>
                      {MONTH_FULL[i]}
                    </p>
                    <p className="text-[10px] font-semibold text-muted-foreground">{viewYear}</p>
                  </div>
                  {hasSlip && (
                    <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />
                  )}
                  {isCurrentMonth && !hasSlip && (
                    <span className="rounded-full bg-primary/10 px-1.5 py-0.5 text-[9px] font-black uppercase tracking-wider text-primary">
                      Current
                    </span>
                  )}
                </div>

                {/* Content */}
                {hasSlip ? (
                  <div className="flex flex-col gap-1.5">
                    <div className="flex items-center gap-1.5 min-w-0">
                      <FileText className="h-3.5 w-3.5 shrink-0 text-emerald-600" />
                      <span className="truncate text-[10px] font-semibold text-emerald-700 font-mono">
                        {meta!.fileName}
                      </span>
                    </div>
                    {meta!.sizeBytes && (
                      <span className="text-[9px] text-muted-foreground font-medium">
                        {formatBytes(meta!.sizeBytes)}
                      </span>
                    )}
                    {/* Action buttons */}
                    <div className="mt-1 flex items-center gap-1">
                      <button
                        type="button"
                        title="Preview"
                        onClick={() => handlePreview(meta!, `${MONTH_FULL[i]} ${viewYear}`)}
                        className="flex-1 inline-flex items-center justify-center gap-1 rounded-md border border-emerald-200 bg-white py-1 text-[10px] font-bold text-emerald-700 hover:bg-emerald-50 transition-colors"
                      >
                        <Eye className="h-3 w-3" /> View
                      </button>
                      <button
                        type="button"
                        title="Download"
                        onClick={() => handleDownload(meta!)}
                        className="inline-flex h-6 w-6 items-center justify-center rounded-md border border-emerald-200 bg-white text-emerald-700 hover:bg-emerald-50 transition-colors"
                      >
                        <Download className="h-3 w-3" />
                      </button>
                      {isEditing && (
                        <button
                          type="button"
                          title="Delete"
                          onClick={() => handleRemove(key)}
                          className="inline-flex h-6 w-6 items-center justify-center rounded-md border border-rose-200 bg-white text-rose-500 hover:bg-rose-50 transition-colors"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      )}
                    </div>
                    {isEditing && (
                      <button
                        type="button"
                        onClick={() => triggerUpload(key)}
                        className="mt-0.5 inline-flex items-center justify-center gap-1 rounded-md border border-dashed border-emerald-300 py-0.5 text-[9px] font-bold text-emerald-600 hover:bg-emerald-100 transition-colors"
                      >
                        <UploadCloud className="h-2.5 w-2.5" /> Replace
                      </button>
                    )}
                  </div>
                ) : isFuture ? (
                  <div className="flex flex-1 items-center justify-center py-1">
                    <span className="text-[10px] font-medium text-muted-foreground/60 italic">Not yet</span>
                  </div>
                ) : isUploadingThis ? (
                  <div className="flex flex-1 items-center justify-center py-2">
                    <span className="text-[10px] font-bold text-primary animate-pulse">Uploading…</span>
                  </div>
                ) : (
                  <div className="flex flex-1 flex-col items-center justify-center gap-1.5 py-1">
                    <span className="text-[10px] font-medium text-muted-foreground italic">No slip</span>
                    {isEditing && (
                      <button
                        type="button"
                        onClick={() => triggerUpload(key)}
                        className="inline-flex items-center gap-1 rounded-md border border-dashed border-primary/40 px-2 py-1 text-[10px] font-bold text-primary hover:bg-primary/5 transition-colors"
                      >
                        <UploadCloud className="h-3 w-3" /> Upload
                      </button>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Total summary */}
        <div className="flex items-center gap-4 rounded-xl border border-border bg-secondary/20 px-4 py-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground">
            <Calendar className="h-4 w-4 text-primary" />
            <span>
              Total uploaded:{" "}
              <span className="font-black text-foreground">
                {Object.values(slips).filter((s) => s?.fileName).length}
              </span>{" "}
              salary slip{Object.values(slips).filter((s) => s?.fileName).length !== 1 ? "s" : ""}
            </span>
          </div>
          {Object.values(slips).filter((s) => s?.fileName).length > 0 && (
            <button
              type="button"
              onClick={() => {
                Object.entries(slips).forEach(([, meta]) => {
                  if (meta?.fileName && meta?.dataUrl) handleDownload(meta);
                });
              }}
              className="ml-auto inline-flex items-center gap-1.5 rounded-lg border border-border bg-card px-3 py-1.5 text-xs font-bold text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
            >
              <Download className="h-3.5 w-3.5" /> Download All
            </button>
          )}
        </div>
      </div>

      {/* Preview Modal */}
      {preview && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 p-4 animate-in fade-in duration-200"
          onClick={() => setPreview(null)}
        >
          <div
            className="flex h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-2xl animate-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal header */}
            <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-4">
              <div className="min-w-0">
                <h3 className="text-sm font-black uppercase tracking-widest text-foreground">
                  Salary Slip — {preview.label}
                </h3>
                <p className="mt-0.5 truncate text-xs font-semibold text-muted-foreground">
                  {preview.meta.fileName}
                  {preview.meta.sizeBytes ? ` · ${formatBytes(preview.meta.sizeBytes)}` : ""}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <button
                  type="button"
                  title="Download"
                  onClick={() => handleDownload(preview.meta)}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
                >
                  <Download className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  title="Close"
                  onClick={() => setPreview(null)}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-border hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Preview content */}
            <div className="min-h-0 flex-1 bg-secondary/20 p-4">
              {getPreviewKind(preview.meta.fileName) === "image" ? (
                <div className="flex h-full items-center justify-center overflow-auto rounded-xl bg-background border border-border/80">
                  <img
                    src={preview.meta.dataUrl}
                    alt={preview.meta.fileName || "Salary slip preview"}
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
              ) : (
                <iframe
                  title={preview.meta.fileName || "Salary slip preview"}
                  src={preview.meta.dataUrl}
                  className="h-full w-full rounded-xl border border-border/80 bg-background"
                />
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
