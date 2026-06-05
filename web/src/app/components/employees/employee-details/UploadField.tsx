import { Paperclip, Eye, Download } from "lucide-react";

interface UploadFieldProps {
  label: string;
  fileName?: string;
  dataUrl?: string;
  editing: boolean;
  onFileChange?: (fileName: string, dataUrl: string) => void;
  accept?: string;
}

export function UploadField({ label, fileName, dataUrl, editing, onFileChange, accept }: UploadFieldProps) {
  const handleView = () => {
    if (!dataUrl || !fileName) {
      if (fileName) alert(`Viewing functionality is limited for mock files without data. Try uploading a new file.`);
      return;
    }

    const isWord = fileName.toLowerCase().endsWith(".doc") || fileName.toLowerCase().endsWith(".docx");
    if (isWord) {
      handleDownload();
      return;
    }

    try {
      const parts = dataUrl.split(",");
      if (parts.length < 2) throw new Error("Invalid data URL");
      const byteString = atob(parts[1]);
      const mimeString = parts[0].split(":")[1].split(";")[0];
      const ab = new ArrayBuffer(byteString.length);
      const ia = new Uint8Array(ab);
      for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
      }
      const blob = new Blob([ab], { type: mimeString });
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
    } catch (e) {
      console.error("Preview failed:", e);
      window.open(dataUrl, "_blank");
    }
  };

  const handleDownload = () => {
    if (!dataUrl || !fileName) {
      if (fileName) alert(`Download functionality is limited for mock files without data. Try uploading a new file.`);
      return;
    }
    const a = document.createElement("a");
    a.href = dataUrl;
    a.download = fileName;
    a.click();
  };

  if (!editing) {
    return (
      <div className="space-y-1.5">
        <span className="block text-[11px] font-semibold text-muted-foreground tracking-wide">{label}</span>
        <div className="rounded-lg border border-border bg-secondary/30 px-3 py-2 text-sm font-medium text-foreground min-h-[2.5rem] flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 overflow-hidden">
            <Paperclip className="w-4 h-4 text-muted-foreground flex-shrink-0" />
            <span className="truncate">{fileName || "—"}</span>
          </div>
          {fileName && (
            <div className="flex items-center gap-1">
              <button
                onClick={handleView}
                className="p-1.5 hover:bg-secondary rounded-md transition-colors text-muted-foreground hover:text-foreground"
                title="View"
              >
                <Eye className="w-4 h-4" />
              </button>
              <button
                onClick={handleDownload}
                className="p-1.5 hover:bg-secondary rounded-md transition-colors text-muted-foreground hover:text-foreground"
                title="Download"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-1.5">
      <span className="block text-[11px] font-semibold text-muted-foreground tracking-wide">{label}</span>
      <div className="flex flex-col gap-2">
        <label className="cursor-pointer w-fit">
          <span className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-dashed border-border bg-secondary/20 text-xs font-semibold hover:bg-secondary/40 transition-colors">
            <Paperclip className="w-3.5 h-3.5" />
            Choose file
          </span>
          <input
            type="file"
            accept={accept}
            className="sr-only"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) {
                const reader = new FileReader();
                reader.onload = () => {
                  onFileChange?.(f.name, String(reader.result || ""));
                };
                reader.readAsDataURL(f);
              }
            }}
          />
        </label>
        {fileName ? (
          <div className="flex items-center gap-3 px-1">
            <span className="text-xs text-muted-foreground truncate max-w-[200px]">{fileName}</span>
            <div className="flex items-center gap-1">
              <button
                onClick={handleView}
                className="p-1 hover:bg-secondary rounded transition-colors text-muted-foreground hover:text-foreground"
                title="View"
              >
                <Eye className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={handleDownload}
                className="p-1 hover:bg-secondary rounded transition-colors text-muted-foreground hover:text-foreground"
                title="Download"
              >
                <Download className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

