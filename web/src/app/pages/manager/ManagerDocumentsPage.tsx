import { FileText, Download, FileCheck, UploadCloud, Folder } from "lucide-react";
import { KPI_ICON_TONES } from "@/components/design-system/DashboardKit";

const STATUS_BADGE: Record<string, string> = {
  Verified: "bg-[#212529] text-[#F8F9FA]",
  Pending:  "bg-[#6C757D] text-white",
};

const DOCUMENTS = [
  { id: 1, name: "Offer Letter.pdf",         category: "Onboarding",          date: "Jan 15, 2026", size: "2.4 MB", status: "Verified" },
  { id: 2, name: "PAN Card.jpg",              category: "KYC",                 date: "Jan 16, 2026", size: "1.1 MB", status: "Verified" },
  { id: 3, name: "Aadhaar Card.pdf",          category: "KYC",                 date: "Jan 16, 2026", size: "3.5 MB", status: "Verified" },
  { id: 4, name: "Relieving Letter.pdf",      category: "Previous Employment", date: "Jan 18, 2026", size: "1.8 MB", status: "Pending"  },
  { id: 5, name: "Degree Certificate.pdf",    category: "Education",           date: "Jan 18, 2026", size: "4.2 MB", status: "Pending"  },
];

const STATS = [
  { label: "KYC",           count: 2, icon: FileCheck },
  { label: "Education",     count: 1, icon: Folder    },
  { label: "Onboarding",    count: 1, icon: FileText  },
  { label: "Previous Emp.", count: 1, icon: Folder    },
];

export function ManagerDocumentsPage() {
  const categoryColorMap: Record<string, "purple" | "green" | "orange" | "red"> = {
    "KYC": "purple",
    "Education": "green",
    "Onboarding": "orange",
    "Previous Emp.": "red",
  };

  return (
    <div className="portal-page admin-dashboard">

      {/* ── Category Stats ──────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {STATS.map(({ label, count, icon: Icon }) => {
          const tone = categoryColorMap[label] || "purple";
          const color = KPI_ICON_TONES[tone];

          return (
            <div key={label} className="flat-card flat-card-hover bg-card p-4 flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 text-white [&_svg]:stroke-white"
                style={{
                  background: color.background,
                  boxShadow: `0 4px 12px ${color.boxShadow}`,
                }}
              >
                <Icon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-sm font-semibold text-foreground">{label}</p>
                <p className="text-xs text-muted-foreground">{count} file{count !== 1 ? "s" : ""}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Documents Table ─────────────────────────────── */}
      <div className="flat-card bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-secondary border-b border-border">
                {["Document Name", "Category", "Upload Date", "Status", "Actions"].map((h) => (
                  <th key={h} className={`px-6 py-3 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider ${h === "Actions" ? "text-right" : ""}`}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {DOCUMENTS.map((doc) => (
                <tr key={doc.id} className="hover:bg-secondary transition-colors duration-150">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-secondary border border-border flex items-center justify-center flex-shrink-0">
                        <FileText className="w-4 h-4 text-muted-foreground" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-foreground">{doc.name}</p>
                        <p className="text-xs text-muted-foreground">{doc.size}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{doc.category}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{doc.date}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-md font-medium ${STATUS_BADGE[doc.status] || ""}`}>
                      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-60" />
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      className="p-2 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-border transition-colors"
                      title="Download"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Upload Button ──────────────────────────────── */}
      <div className="flex justify-end">
        <button className="flex items-center gap-2 px-4 py-2.5 bg-foreground text-primary-foreground text-sm font-medium rounded-lg
          hover:bg-accent transition-colors">
          <UploadCloud className="w-4 h-4" /> Upload New
        </button>
      </div>
    </div>
  );
}
