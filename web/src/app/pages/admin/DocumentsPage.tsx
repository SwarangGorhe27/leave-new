import { useState } from "react";
import {
  FileText, Image, Table2, Upload, Search, Folder,
  Download, Trash2, Eye, LayoutList, Grid3x3,
} from "lucide-react";
import { documents as initialDocs, Document, DocCategory } from "../../components/employees/mockAdminData";

const CATEGORY_BADGE: Record<DocCategory, string> = {
  Policy:      "bg-[#212529] text-[#F8F9FA]",
  Contract:    "bg-[#343A40] text-[#F8F9FA]",
  Certificate: "bg-[#495057] text-[#F8F9FA]",
  "ID Proof":  "bg-[#6C757D] text-white",
  Payslip:     "bg-[#ADB5BD] text-[#212529]",
  Other:       "bg-[#E9ECEF] text-[#212529] border border-[#DEE2E6]",
};

const TYPE_ICON: Record<Document["type"], React.ElementType> = {
  PDF:  FileText,
  DOC:  FileText,
  XLSX: Table2,
  IMG:  Image,
};

const CATEGORIES: (DocCategory | "All")[] = [
  "All", "Policy", "Contract", "Certificate", "ID Proof", "Payslip", "Other",
];

export function DocumentsPage() {
  const [docs, setDocs]               = useState<Document[]>(initialDocs);
  const [search, setSearch]           = useState("");
  const [filterCategory, setFilterCategory] = useState<DocCategory | "All">("All");
  const [viewMode, setViewMode]       = useState<"grid" | "list">("list");

  const filtered = docs.filter((d) => {
    const matchSearch = !search
      || d.name.toLowerCase().includes(search.toLowerCase())
      || (d.employeeName?.toLowerCase().includes(search.toLowerCase()) ?? false);
    const matchCat = filterCategory === "All" || d.category === filterCategory;
    return matchSearch && matchCat;
  });

  const deleteDoc = (id: string) => {
    if (window.confirm("Delete this document?")) {
      setDocs((prev) => prev.filter((d) => d.id !== id));
    }
  };

  const downloadDoc = (doc: Document) => {
    const element = document.createElement("a");
    const file = new Blob([`Mock document content for: ${doc.name}\nCategory: ${doc.category}\nUploaded By: ${doc.uploadedBy}`], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    const extension = doc.type.toLowerCase();
    element.download = doc.name.toLowerCase().endsWith(`.${extension}`) ? doc.name : `${doc.name}.${extension}`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const viewDoc = (doc: Document) => {
    const win = window.open("", "_blank");
    if (win) {
      win.document.write(`
        <html>
          <head>
            <title>Preview - \${doc.name}</title>
            <style>
              body { font-family: sans-serif; padding: 40px; background: #f8f9fa; color: #333; }
              .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); max-width: 600px; margin: auto; }
              h1 { margin-top: 0; color: #111; font-size: 24px; border-bottom: 2px solid #eee; padding-bottom: 12px; }
              .meta { font-size: 14px; color: #666; margin-bottom: 20px; line-height: 1.6; }
              .content { background: #f1f3f5; padding: 20px; border-radius: 8px; font-family: monospace; white-space: pre-wrap; }
            </style>
          </head>
          <body>
            <div class="card">
              <h1>📄 \${doc.name}</h1>
              <div class="meta">
                <strong>Category:</strong> \${doc.category}<br/>
                <strong>Uploaded By:</strong> \${doc.uploadedBy}<br/>
                <strong>Date:</strong> \${new Date(doc.uploadDate).toLocaleDateString()}<br/>
                <strong>Size:</strong> \${doc.size}
              </div>
              <div class="content">--- Mock Preview of \${doc.type} Document ---</div>
            </div>
          </body>
        </html>
      `);
      win.document.close();
    }
  };

  const categoryCounts = CATEGORIES.reduce<Record<string, number>>((acc, cat) => {
    acc[cat] = cat === "All" ? docs.length : docs.filter((d) => d.category === cat).length;
    return acc;
  }, {});

  return (
    <div className="portal-page admin-dashboard">

      {/* ── Header row ──────────────────────────────────── */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Category filter pills */}
        <div className="flex flex-wrap items-center gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCategory(cat)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                transition-all duration-150 border ${
                  filterCategory === cat
                    ? "bg-foreground text-primary-foreground border-transparent"
                    : "bg-card text-muted-foreground border-border hover:bg-secondary hover:text-foreground"
                }`}
            >
              {cat !== "All" && <Folder className="w-3 h-3" />}
              {cat}
              <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                filterCategory === cat ? "bg-primary-foreground/20 text-primary-foreground" : "bg-secondary text-muted-foreground"
              }`}>
                {categoryCounts[cat]}
              </span>
            </button>
          ))}
        </div>

        <button className="flex items-center gap-2 px-4 py-2 bg-foreground text-primary-foreground text-sm font-medium rounded-lg
          hover:bg-accent transition-colors">
          <Upload className="w-4 h-4" /> Upload Document
        </button>
      </div>

      {/* ── Main card ───────────────────────────────────── */}
      <div className="flat-card bg-card overflow-hidden">
        {/* Toolbar */}
        <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-4 border-b border-border">
          <h2 className="text-sm font-semibold text-foreground">
            All Documents
            <span className="ml-2 text-xs font-normal text-muted-foreground">({filtered.length} files)</span>
          </h2>
          <div className="flex items-center gap-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search documents…"
                className="flat-input dark:bg-slate-900 dark:text-white dark:border-slate-700 dark:placeholder:text-slate-400 pl-12 pr-4 py-2 text-sm w-52"
              />
            </div>
            {/* View toggle */}
            <div className="flex bg-secondary border border-border rounded-lg p-1 gap-1">
              {(["list", "grid"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setViewMode(m)}
                  className={`p-1.5 rounded-md transition-all duration-150 ${
                    viewMode === m
                      ? "bg-card border border-border text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                  title={m === "list" ? "List view" : "Grid view"}
                >
                  {m === "list" ? <LayoutList className="w-4 h-4" /> : <Grid3x3 className="w-4 h-4" />}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* ── List view ─────────────────────────────────── */}
        {viewMode === "list" ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-secondary border-b border-border">
                  {["File Name", "Category", "Employee", "Uploaded By", "Date", "Size", "Actions"].map((h) => (
                    <th key={h} className="text-left px-6 py-3 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map((doc) => {
                  const Icon = TYPE_ICON[doc.type];
                  return (
                    <tr key={doc.id} className="hover:bg-secondary transition-colors duration-150">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-secondary border border-border rounded-md flex items-center justify-center flex-shrink-0">
                            <Icon className="w-4 h-4 text-muted-foreground" />
                          </div>
                          <span className="text-sm font-medium text-foreground">{doc.name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`text-xs px-2 py-0.5 rounded-md font-medium ${CATEGORY_BADGE[doc.category]}`}>
                          {doc.category}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{doc.employeeName || "—"}</td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{doc.uploadedBy}</td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">
                        {new Date(doc.uploadDate).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "2-digit" })}
                      </td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{doc.size}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => viewDoc(doc)}
                            className="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-border transition-colors"
                            title="View"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => downloadDoc(doc)}
                            className="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-border transition-colors"
                            title="Download"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => deleteDoc(doc.id)}
                            className="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-border transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={7} className="text-center py-12">
                      <div className="flex flex-col items-center text-muted-foreground">
                        <FileText className="w-10 h-10 mb-3 opacity-20" />
                        <p className="text-sm font-medium">No documents found.</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        ) : (
          /* ── Grid view ─────────────────────────────────── */
          <div className="p-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {filtered.map((doc) => {
              const Icon = TYPE_ICON[doc.type];
              return (
                <div
                  key={doc.id}
                  className="border border-border rounded-lg p-4 bg-background hover:border-foreground/30 hover:shadow-sm
                    transition-all duration-150 group cursor-pointer flex flex-col"
                >
                  <div className="w-10 h-10 rounded-lg bg-secondary border border-border flex items-center justify-center mb-3
                    group-hover:scale-105 transition-transform duration-150">
                    <Icon className="w-5 h-5 text-muted-foreground" />
                  </div>
                  <p className="text-sm font-medium text-foreground truncate mb-0.5" title={doc.name}>{doc.name}</p>
                  <p className="text-xs text-muted-foreground mb-3">{doc.size}</p>
                  <div className="mt-auto flex items-center justify-between">
                    <span className={`text-[10px] px-2 py-0.5 rounded-md font-medium ${CATEGORY_BADGE[doc.category]}`}>
                      {doc.category}
                    </span>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                      <button
                        onClick={(e) => { e.stopPropagation(); viewDoc(doc); }}
                        className="p-1 rounded text-muted-foreground hover:text-foreground transition-colors"
                        title="View"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); downloadDoc(doc); }}
                        className="p-1 rounded text-muted-foreground hover:text-foreground transition-colors"
                        title="Download"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); deleteDoc(doc.id); }}
                        className="p-1 rounded text-muted-foreground hover:text-foreground transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
            {filtered.length === 0 && (
              <div className="col-span-full py-12 flex flex-col items-center text-muted-foreground">
                <FileText className="w-12 h-12 mb-3 opacity-20" />
                <p className="text-sm font-medium">No documents found.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
