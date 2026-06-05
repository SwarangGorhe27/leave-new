import { useRef, useState } from "react";
import { Camera, Trash2, User } from "lucide-react";

const MAX_BYTES = 3 * 1024 * 1024;
const ACCEPT = "image/jpeg,image/png,image/webp";

function validateImage(file: File): string | null {
  if (!file.type.startsWith("image/")) return "Please choose a JPG, PNG, or WebP image.";
  if (file.size > MAX_BYTES) return "Image must be 3 MB or smaller.";
  return null;
}

type Props = {
  value?: string;
  readOnly: boolean;
  onChange: (dataUrl: string) => void;
  onRemove: () => void;
  nameHint?: string;
};

export function ProfileImageUploader({ value, readOnly, onChange, onRemove, nameHint }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const openPicker = () => {
    if (readOnly) return;
    setErr(null);
    inputRef.current?.click();
  };

  const onFile = (file: File | undefined) => {
    if (!file) return;
    const e = validateImage(file);
    if (e) {
      setErr(e);
      return;
    }
    setBusy(true);
    setErr(null);
    const reader = new FileReader();
    reader.onload = () => {
      onChange(String(reader.result || ""));
      setBusy(false);
    };
    reader.onerror = () => {
      setErr("Could not read the file.");
      setBusy(false);
    };
    reader.readAsDataURL(file);
  };

  const showImg = value && (value.startsWith("data:") || value.startsWith("http"));

  return (
    <div className="relative shrink-0">
      <div
        className="relative h-24 w-24 sm:h-28 sm:w-28 rounded-full border-2 border-border bg-secondary overflow-hidden shadow-sm"
        title={nameHint}
      >
        {showImg ? (
          <img src={value} alt="" className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-muted-foreground">
            <User className="h-10 w-10 opacity-40" />
          </div>
        )}

        {!readOnly && (
          <div className="absolute inset-0 flex items-end justify-center gap-1 bg-gradient-to-t from-black/55 to-transparent pb-1.5 opacity-0 hover:opacity-100 transition-opacity duration-200">
            <button
              type="button"
              onClick={openPicker}
              disabled={busy}
              className="rounded-full bg-white/95 p-1.5 text-foreground shadow hover:bg-white disabled:opacity-50"
              title="Upload or change photo"
            >
              <Camera className="h-4 w-4" />
            </button>
            {showImg ? (
              <button
                type="button"
                onClick={() => {
                  onRemove();
                  setErr(null);
                }}
                disabled={busy}
                className="rounded-full bg-white/95 p-1.5 text-destructive shadow hover:bg-white disabled:opacity-50"
                title="Remove photo"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            ) : null}
          </div>
        )}
      </div>

      {!readOnly && (
        <button
          type="button"
          onClick={openPicker}
          className="absolute -bottom-0.5 -right-0.5 flex h-9 w-9 items-center justify-center rounded-full border border-border bg-card text-foreground shadow-md hover:bg-secondary transition-colors"
          title="Edit photo"
        >
          <Camera className="h-4 w-4" />
        </button>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        className="hidden"
        onChange={(ev) => {
          const f = ev.target.files?.[0];
          onFile(f);
          ev.target.value = "";
        }}
      />

      {err ? <p className="absolute left-0 top-full mt-1 w-48 text-[11px] text-destructive">{err}</p> : null}
    </div>
  );
}
