import { useRef, useState } from 'react';
import { FileText, FileUp, Search, Trash2, Upload, X } from 'lucide-react';
import { useMyDocuments, useUploadDocument, useAllDocuments, useAdminUploadDocument, useDeleteDocument } from '@hooks/useDocuments';
import { Badge } from '@components/ui/Badge';
import { useUIStore } from '@store/uiStore';
import { cn } from '@utils/utils';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
interface Document {
  id: string;
  title: string;
  description: string;
  category: string;
  status: string;
  version: number;
  file_name: string;
  file_size: number;
  mime_type: string;
  file: string;
  created_at: string;
}

const CATEGORY_LABELS: Record<string, string> = {
  COMPANY: 'Company',
  POLICY: 'Policy',
  TEMPLATE: 'Template',
  LETTER: 'Letter',
  CERTIFICATE: 'Certificate',
  OTHER: 'Other',
};

function formatSize(bytes: number) {
  if (bytes >= 1_000_000) return `${(bytes / 1_000_000).toFixed(1)} MB`;
  if (bytes >= 1_000) return `${(bytes / 1_000).toFixed(0)} KB`;
  return `${bytes} B`;
}

/* ------------------------------------------------------------------ */
/*  Upload area                                                        */
/* ------------------------------------------------------------------ */
function UploadArea() {
  const fileRef = useRef<HTMLInputElement>(null);
  const uploadMut = useUploadDocument();
  const [dragOver, setDragOver] = useState(false);
  const [title, setTitle] = useState('');

  function doUpload(file: File) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('title', title || file.name);
    fd.append('category', 'OTHER');
    uploadMut.mutate(fd);
    setTitle('');
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) doUpload(file);
  }

  function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) doUpload(file);
    e.target.value = '';
  }

  return (
    <div className="space-y-3">
      <input
        type="text"
        placeholder="Document title (optional)"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="w-full rounded-xl border border-surface-300/70 bg-surface-0 px-3 py-2.5 text-sm text-surface-900 placeholder-surface-400 focus:border-brand-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder-white/30"
      />
      <div
        role="button"
        tabIndex={0}
        onClick={() => fileRef.current?.click()}
        onKeyDown={(e) => e.key === 'Enter' && fileRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        className={cn(
          'flex cursor-pointer flex-col items-center justify-center gap-2 rounded-2xl border-2 border-dashed py-8 transition-colors',
          dragOver
            ? 'border-brand-400 bg-brand-50 dark:border-brand-500 dark:bg-brand-900/20'
            : 'border-surface-200 hover:border-brand-300 hover:bg-surface-50 dark:border-white/15 dark:hover:border-brand-500 dark:hover:bg-white/5',
        )}
      >
        <FileUp className="h-8 w-8 text-surface-400 dark:text-white/30" />
        <p className="text-sm font-medium text-surface-700 dark:text-white/60">
          {uploadMut.isPending ? 'Uploading…' : 'Drop file here or click to browse'}
        </p>
        <p className="text-xs text-surface-400 dark:text-white/30">PDF, DOCX, XLSX, PNG, JPG up to 20 MB</p>
        <input ref={fileRef} type="file" className="hidden" accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg" onChange={onFile} />
      </div>

      {uploadMut.isSuccess && (
        <div className="flex items-center gap-2 rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400">
          ✓ Document uploaded successfully
        </div>
      )}
      {uploadMut.isError && (
        <div className="flex items-center gap-2 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-900/20 dark:text-red-400">
          Upload failed — please try again
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Document row                                                       */
/* ------------------------------------------------------------------ */
function DocRow({ doc }: { doc: Document }) {
  return (
    <div className="flex items-center gap-4 rounded-xl border border-surface-200/70 bg-surface-0 px-4 py-3.5 shadow-xs dark:border-white/10 dark:bg-white/5">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-surface-100 dark:bg-white/10">
        <FileText className="h-5 w-5 text-surface-500 dark:text-white/45" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-surface-900 dark:text-white">{doc.title}</p>
        <div className="mt-0.5 flex items-center gap-2 text-xs text-surface-500 dark:text-white/40">
          <span>{doc.file_name}</span>
          {doc.file_size > 0 && <span>· {formatSize(doc.file_size)}</span>}
        </div>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <Badge variant="info">{CATEGORY_LABELS[doc.category] ?? doc.category}</Badge>
        <span className="hidden text-xs text-surface-400 dark:text-white/30 sm:block">v{doc.version}</span>
        {doc.file && (
          <a
            href={doc.file}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg border border-surface-200 px-2.5 py-1.5 text-xs font-medium text-surface-700 transition-colors hover:border-brand-400 hover:text-brand-600 dark:border-white/10 dark:text-white/60 dark:hover:border-brand-500 dark:hover:text-brand-400"
            onClick={(e) => e.stopPropagation()}
          >
            View
          </a>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Admin: Policy / Document Management                               */
/* ------------------------------------------------------------------ */

const CATEGORY_OPTIONS = [
  { value: 'POLICY', label: 'Policy' },
  { value: 'COMPANY', label: 'Company' },
  { value: 'TEMPLATE', label: 'Template' },
  { value: 'LETTER', label: 'Letter' },
  { value: 'CERTIFICATE', label: 'Certificate' },
  { value: 'OTHER', label: 'Other' },
];

function AdminUploadArea() {
  const fileRef = useRef<HTMLInputElement>(null);
  const uploadMut = useAdminUploadDocument();
  const [dragOver, setDragOver] = useState(false);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('POLICY');

  function doUpload(file: File) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('title', title || file.name);
    fd.append('category', category);
    uploadMut.mutate(fd, {
      onSuccess: () => { setTitle(''); setCategory('POLICY'); },
    });
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) doUpload(file);
  }

  function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) doUpload(file);
    e.target.value = '';
  }

  const inputCls = 'w-full rounded-xl border border-surface-300/70 bg-surface-0 px-3 py-2.5 text-sm text-surface-900 placeholder-surface-400 focus:border-brand-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder-white/30';

  return (
    <div className="space-y-4 p-4">
      <div className="rounded-2xl border border-surface-200/70 bg-surface-0 p-5 shadow-xs dark:border-white/10 dark:bg-white/5">
        <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-surface-900 dark:text-white">
          <Upload className="h-4 w-4 text-brand-500" /> Upload Document / Policy
        </h3>
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Document title (required)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className={inputCls}
          />
          <select value={category} onChange={(e) => setCategory(e.target.value)} className={inputCls}>
            {CATEGORY_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
          <div
            role="button"
            tabIndex={0}
            onClick={() => fileRef.current?.click()}
            onKeyDown={(e) => e.key === 'Enter' && fileRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            className={cn(
              'flex cursor-pointer flex-col items-center justify-center gap-2 rounded-2xl border-2 border-dashed py-8 transition-colors',
              dragOver
                ? 'border-brand-400 bg-brand-50 dark:border-brand-500 dark:bg-brand-900/20'
                : 'border-surface-200 hover:border-brand-300 hover:bg-surface-50 dark:border-white/15 dark:hover:border-brand-500 dark:hover:bg-white/5',
            )}
          >
            <FileUp className="h-8 w-8 text-surface-400 dark:text-white/30" />
            <p className="text-sm font-medium text-surface-700 dark:text-white/60">
              {uploadMut.isPending ? 'Uploading…' : 'Drop file here or click to browse'}
            </p>
            <p className="text-xs text-surface-400 dark:text-white/30">PDF, DOCX, XLSX, PNG, JPG up to 20 MB</p>
            <input ref={fileRef} type="file" className="hidden" accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg" onChange={onFile} />
          </div>
          {uploadMut.isSuccess && (
            <div className="flex items-center gap-2 rounded-xl bg-emerald-50 px-3 py-2 text-sm text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400">
              ✓ Document uploaded and published to all employees
            </div>
          )}
          {uploadMut.isError && (
            <div className="flex items-center gap-2 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-900/20 dark:text-red-400">
              Upload failed — please try again
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function AdminDocList() {
  const { data: allDocs = [], isLoading } = useAllDocuments();
  const deleteMut = useDeleteDocument();
  const [search, setSearch] = useState('');
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  interface AdminDoc {
    id: string; title: string; description: string; category: string;
    status: string; version: number; file_name: string; file_size: number;
    mime_type: string; file: string; created_at: string;
  }
  const docs = allDocs as unknown as AdminDoc[];
  const filtered = search
    ? docs.filter((d) => d.title.toLowerCase().includes(search.toLowerCase()) || d.file_name?.toLowerCase().includes(search.toLowerCase()))
    : docs;

  if (isLoading) {
    return (
      <div className="space-y-3 p-4">
        {[1, 2, 3].map((i) => <div key={i} className="h-16 animate-pulse rounded-xl bg-surface-100 dark:bg-white/10" />)}
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-surface-400 dark:text-white/30" />
          <input
            type="search"
            placeholder="Search documents…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-surface-300/70 bg-surface-0 py-2.5 pl-9 pr-3 text-sm text-surface-900 placeholder-surface-400 focus:border-brand-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder-white/30"
          />
        </div>
        <span className="shrink-0 rounded-lg bg-surface-100 px-2.5 py-1 text-xs text-surface-500 dark:bg-white/5 dark:text-white/40">
          {filtered.length} docs
        </span>
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center py-16 text-center">
          <FileText className="h-10 w-10 text-surface-300 dark:text-white/20" />
          <p className="mt-3 text-sm text-surface-500 dark:text-white/40">No documents found</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map((doc) => (
            <div key={doc.id} className="flex items-center gap-4 rounded-xl border border-surface-200/70 bg-surface-0 px-4 py-3.5 shadow-xs dark:border-white/10 dark:bg-white/5">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-surface-100 dark:bg-white/10">
                <FileText className="h-5 w-5 text-surface-500 dark:text-white/45" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium text-surface-900 dark:text-white">{doc.title}</p>
                <div className="mt-0.5 flex flex-wrap items-center gap-2 text-xs text-surface-500 dark:text-white/40">
                  <span>{doc.file_name}</span>
                  {doc.file_size > 0 && <span>· {formatSize(doc.file_size)}</span>}
                  <span>· v{doc.version}</span>
                  <span>· {new Date(doc.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
                </div>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <Badge variant="info">{CATEGORY_LABELS[doc.category] ?? doc.category}</Badge>
                {doc.file && (
                  <a href={doc.file} target="_blank" rel="noopener noreferrer"
                    className="rounded-lg border border-surface-200 px-2.5 py-1.5 text-xs font-medium text-surface-700 transition-colors hover:border-brand-400 hover:text-brand-600 dark:border-white/10 dark:text-white/60 dark:hover:border-brand-500"
                    onClick={(e) => e.stopPropagation()}>
                    View
                  </a>
                )}
                {confirmDelete === doc.id ? (
                  <div className="flex items-center gap-1">
                    <button type="button" onClick={() => { deleteMut.mutate(doc.id); setConfirmDelete(null); }}
                      className="rounded-lg bg-red-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-red-700">
                      Delete
                    </button>
                    <button type="button" onClick={() => setConfirmDelete(null)}
                      className="rounded-lg border border-surface-200 px-2.5 py-1.5 text-xs font-medium text-surface-600 dark:border-white/10 dark:text-white/50">
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button type="button" onClick={() => setConfirmDelete(doc.id)}
                    className="flex h-8 w-8 items-center justify-center rounded-lg text-surface-400 transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20 dark:hover:text-red-400">
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main export                                                        */
/* ------------------------------------------------------------------ */
type Tab = 'browse' | 'upload';
type AdminTab = 'all-docs' | 'upload-policy';

export function DocumentPanel() {
  const activeModule = useUIStore((s) => s.activeModule);
  const portal = useUIStore((s) => s.portal);
  const rawModuleView = useUIStore((s) => s.moduleViews[activeModule] ?? 'employee');
  const moduleView = portal === 'ess' ? 'employee' : rawModuleView;
  const isAdmin = moduleView === 'admin';

  const [tab, setTab] = useState<Tab>('browse');
  const [adminTab, setAdminTab] = useState<AdminTab>('all-docs');
  const [search, setSearch] = useState('');
  const { data: allDocs = [], isLoading } = useMyDocuments();
  const typedDocs = allDocs as unknown as Document[];
  const filtered = search
    ? typedDocs.filter(
        (d) =>
          d.title.toLowerCase().includes(search.toLowerCase()) ||
          d.file_name.toLowerCase().includes(search.toLowerCase()),
      )
    : typedDocs;

  /* ── HRMS admin view ─────────────────────────── */
  if (isAdmin) {
    const adminTabs: { key: AdminTab; label: string }[] = [
      { key: 'all-docs', label: 'All Documents' },
      { key: 'upload-policy', label: 'Upload Policy' },
    ];
    return (
      <div className="space-y-5 p-1">
        <div className="flex gap-1 rounded-xl border border-surface-200/70 bg-surface-50 p-1 dark:border-white/10 dark:bg-white/5">
          {adminTabs.map((t) => (
            <button key={t.key} type="button" onClick={() => setAdminTab(t.key)}
              className={cn('flex-1 rounded-lg px-4 py-2 text-sm font-medium transition-colors',
                adminTab === t.key
                  ? 'bg-surface-0 text-surface-900 shadow-sm dark:bg-white/10 dark:text-white'
                  : 'text-surface-500 hover:text-surface-800 dark:text-white/40 dark:hover:text-white/70')}>
              {t.label}
            </button>
          ))}
        </div>
        {adminTab === 'all-docs' ? <AdminDocList /> : <AdminUploadArea />}
      </div>
    );
  }

  /* ── ESS / Employee view ────────────────────── */
  const tabs: { key: Tab; label: string }[] = [
    { key: 'browse', label: 'My Documents' },
    { key: 'upload', label: 'Upload Document' },
  ];

  return (
    <div className="space-y-5 p-1">
      {/* Tab bar */}
      <div className="flex gap-1 rounded-xl border border-surface-200/70 bg-surface-50 p-1 dark:border-white/10 dark:bg-white/5">
        {tabs.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setTab(t.key)}
            className={cn(
              'flex-1 rounded-lg px-4 py-2 text-sm font-medium transition-colors',
              tab === t.key
                ? 'bg-surface-0 text-surface-900 shadow-sm dark:bg-white/10 dark:text-white'
                : 'text-surface-500 hover:text-surface-800 dark:text-white/40 dark:hover:text-white/70',
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'browse' && (
        <div className="space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-surface-400 dark:text-white/30" />
            <input
              type="search"
              placeholder="Search documents…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-xl border border-surface-300/70 bg-surface-0 py-2.5 pl-9 pr-9 text-sm text-surface-900 placeholder-surface-400 focus:border-brand-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder-white/30"
            />
            {search && (
              <button type="button" onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600">
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Documents list */}
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-16 animate-pulse rounded-xl bg-surface-100 dark:bg-white/5" />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center py-16 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-surface-100 dark:bg-white/5">
                <FileText className="h-6 w-6 text-surface-400 dark:text-white/25" />
              </div>
              <p className="mt-4 text-sm font-medium text-surface-700 dark:text-white/60">
                {search ? 'No matching documents' : 'No documents available'}
              </p>
              <p className="mt-1 text-xs text-surface-400 dark:text-white/30">
                {search ? 'Try a different search term.' : 'Upload company documents to share with employees.'}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {filtered.map((doc) => (
                <DocRow key={doc.id} doc={doc} />
              ))}
            </div>
          )}
        </div>
      )}

      {tab === 'upload' && <UploadArea />}
    </div>
  );
}
