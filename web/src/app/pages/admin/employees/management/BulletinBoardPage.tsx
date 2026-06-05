import React, { useState, useMemo } from "react";
import { 
  Megaphone, 
  Calendar, 
  Users, 
  Eye, 
  Edit3, 
  Trash2, 
  Plus, 
  RefreshCw, 
  Filter, 
  Clock, 
  ShieldCheck, 
  Download,
  Info,
  Database,
  Tag,
  ArrowRight,
  Search,
  MoreVertical,
  Layers,
  Star
} from "lucide-react";
import { Button } from "../../../../components/ui/button";
import { Input } from "../../../../components/ui/input";
import { Badge } from "../../../../components/ui/badge";
import { cn } from "../../../../components/ui/utils";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "../../../../components/ui/select";
import { Bulletin, BulletinStatus } from "./BulletinBoard/types";
import { AddBulletinModal } from "./BulletinBoard/AddBulletinModal";
import { BULLETIN_CATEGORIES } from "./BulletinBoard/BulletinBoardConfig";

export function BulletinBoardPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editBulletin, setEditBulletin] = useState<Bulletin | null>(null);
  const [statusFilter, setStatusFilter] = useState<BulletinStatus>("Open");
  const [payrollMonth, setPayrollMonth] = useState(new Date().toISOString().slice(0, 7));
  const [searchQuery, setSearchQuery] = useState("");

  const [bulletins, setBulletins] = useState<Bulletin[]>([
    {
      id: "1",
      category: "hr-campaign",
      title: "Annual Townhall 2026 - Save the Date!",
      content: "All employees are requested to join the annual townhall meeting on Friday.",
      postedDate: "2026-05-10T10:00:00Z",
      startDate: "2026-05-10",
      expiryDate: "2026-05-20",
      rank: 1,
      isHidden: false,
      attachments: [],
      employeeFilters: ["all"],
      status: "Open"
    },
    {
      id: "2",
      category: "notification",
      title: "New Policy Update: Flexible Working Hours",
      content: "The company has updated the remote work policy. Please check the attachment.",
      postedDate: "2026-05-08T14:30:00Z",
      startDate: "2026-05-08",
      expiryDate: "2026-06-01",
      rank: 2,
      isHidden: false,
      attachments: [],
      employeeFilters: ["bangalore", "sales"],
      status: "Open"
    },
    {
      id: "3",
      category: "general",
      title: "Cafeteria Maintenance Schedule",
      content: "The cafeteria will be closed for maintenance on Sunday.",
      postedDate: "2026-05-01T09:15:00Z",
      startDate: "2026-05-01",
      expiryDate: "2026-05-05",
      rank: 5,
      isHidden: true,
      attachments: [],
      employeeFilters: ["all-current"],
      status: "Closed"
    }
  ]);

  const filteredBulletins = useMemo(() => {
    return bulletins.filter(b => {
      const matchesStatus = b.status === statusFilter;
      const matchesSearch = b.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                           b.category.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesStatus && matchesSearch;
    }).sort((a, b) => a.rank - b.rank);
  }, [bulletins, statusFilter, searchQuery]);

  const handleSave = (data: Partial<Bulletin>) => {
    if (editBulletin) {
      setBulletins(bulletins.map(b => b.id === editBulletin.id ? { ...b, ...data } as Bulletin : b));
    } else {
      const newBulletin: Bulletin = {
        ...data,
        id: Math.random().toString(36).substr(2, 9),
        postedDate: new Date().toISOString(),
      } as Bulletin;
      setBulletins([newBulletin, ...bulletins]);
    }
    setIsModalOpen(false);
    setEditBulletin(null);
  };

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this bulletin?")) {
      setBulletins(bulletins.filter(b => b.id !== id));
    }
  };

  const handleEdit = (bulletin: Bulletin) => {
    setEditBulletin(bulletin);
    setIsModalOpen(true);
  };

  return (
    <div className="flex flex-col h-full bg-background/30 overflow-hidden">
      {/* Header */}
      <div className="px-8 py-6 border-b border-border bg-card/50 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4 sticky top-0 z-20 shadow-sm">
        {/* <div className="space-y-1">
          <h1 className="text-xl font-black text-foreground tracking-tight uppercase flex items-center gap-2">
            <Megaphone className="w-5 h-5 text-primary" />
            Bulletin Board
          </h1>
          <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest opacity-60">
            Manage announcements, notifications, and company campaigns
          </p>
        </div> */}
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-1.5 bg-secondary/50 rounded-xl border border-border mr-2 shadow-inner">
            <Calendar className="w-4 h-4 text-primary" />
            <Input 
              type="month" 
              value={payrollMonth} 
              onChange={(e) => setPayrollMonth(e.target.value)} 
              className="h-8 w-32 border-none bg-transparent text-xs font-bold p-0 focus-visible:ring-0" 
            />
          </div>
          <Button 
            onClick={() => {
              setEditBulletin(null);
              setIsModalOpen(true);
            }}
            className="h-11 px-8 rounded-2xl bg-primary text-white hover:opacity-90 text-xs font-black uppercase tracking-widest shadow-xl shadow-primary/20"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Bulletin
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-[1400px] mx-auto space-y-8">
          
          {/* Quick Filters & Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="md:col-span-3 bg-card border border-border rounded-[2.5rem] p-8 flex items-center justify-between shadow-sm">
               <div className="flex items-center gap-6">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest px-1">Bulletin Status</label>
                    <div className="flex p-1 bg-secondary/50 rounded-2xl border border-border">
                      {(["Open", "Closed"] as BulletinStatus[]).map(s => (
                        <button 
                          key={s} 
                          onClick={() => setStatusFilter(s)}
                          className={cn(
                            "px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all",
                            statusFilter === s ? "bg-background shadow-lg text-primary" : "text-muted-foreground hover:bg-secondary"
                          )}
                        >
                          {s} Bulletins
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="h-12 w-px bg-border mx-2" />

                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest px-1">Global Search</label>
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input 
                        placeholder="Search title or tags..." 
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10 h-11 w-64 bg-secondary/30 border-none rounded-xl text-xs font-bold shadow-inner" 
                      />
                    </div>
                  </div>
               </div>

               <Button variant="ghost" size="icon" className="h-11 w-11 rounded-2xl bg-secondary/50 hover:bg-primary/10 hover:text-primary transition-all">
                 <RefreshCw className="w-5 h-5" />
               </Button>
            </div>

            <div className="bg-primary border border-primary/20 rounded-[2.5rem] p-8 text-white shadow-xl shadow-primary/20 flex flex-col justify-center">
              <div className="flex items-center justify-between mb-2">
                 <p className="text-[10px] font-black uppercase tracking-[0.2em] opacity-60">Active Pulse</p>
                 <Star className="w-4 h-4 fill-white/20 text-white/40" />
              </div>
              <div className="flex items-baseline gap-2">
                <p className="text-4xl font-black">{bulletins.filter(b => b.status === "Open").length}</p>
                <p className="text-xs font-bold uppercase opacity-80">Live Bulletins</p>
              </div>
            </div>
          </div>

          {/* Table Section */}
          <div className="space-y-6">
            <div className="flex items-center justify-between px-2">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-primary/10 flex items-center justify-center">
                  <Database className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="text-lg font-black text-foreground uppercase tracking-tight">Announcement Inventory</h3>
                  <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest opacity-60">
                    Showing {filteredBulletins.length} items based on current filters
                  </p>
                </div>
              </div>
              <Button variant="outline" className="h-10 px-5 rounded-xl border-border text-[10px] font-black uppercase tracking-widest shadow-sm">
                <Download className="w-4 h-4 mr-2" />
                Export CSV
              </Button>
            </div>

            <div className="bg-card border border-border rounded-[3rem] overflow-hidden shadow-2xl">
              <table className="w-full text-left">
                <thead className="bg-muted/50 border-b border-border">
                  <tr>
                    <th className="px-10 py-6 text-[10px] font-black text-muted-foreground uppercase tracking-widest">Category</th>
                    <th className="px-10 py-6 text-[10px] font-black text-muted-foreground uppercase tracking-widest">Announcement Title</th>
                    <th className="px-10 py-6 text-[10px] font-black text-muted-foreground uppercase tracking-widest">Posted Date</th>
                    <th className="px-10 py-6 text-[10px] font-black text-muted-foreground uppercase tracking-widest">Rank</th>
                    <th className="px-10 py-6 text-[10px] font-black text-muted-foreground uppercase tracking-widest text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {filteredBulletins.map((bulletin) => (
                    <tr key={bulletin.id} className="hover:bg-secondary/20 transition-all group">
                      <td className="px-10 py-6">
                        <div className="flex items-center gap-3">
                           <div className={cn(
                             "w-10 h-10 rounded-xl flex items-center justify-center shadow-inner",
                             bulletin.category === "general" ? "bg-blue-500/10 text-blue-600" :
                             bulletin.category === "notification" ? "bg-amber-500/10 text-amber-600" :
                             "bg-emerald-500/10 text-emerald-600"
                           )}>
                             <Tag className="w-5 h-5" />
                           </div>
                           <div>
                             <p className="text-xs font-black text-foreground uppercase tracking-tight">
                               {BULLETIN_CATEGORIES.find(c => c.id === bulletin.category)?.label}
                             </p>
                             <p className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest opacity-60">Category ID: {bulletin.category}</p>
                           </div>
                        </div>
                      </td>
                      <td className="px-10 py-6">
                        <div className="space-y-1.5 max-w-md">
                          <p className="text-sm font-black text-foreground leading-tight group-hover:text-primary transition-colors">
                            {bulletin.title}
                          </p>
                          <div className="flex items-center gap-2">
                             <Badge variant="outline" className="text-[9px] font-black uppercase bg-background border-border/50 text-muted-foreground">
                               {bulletin.employeeFilters.length} Target Groups
                             </Badge>
                             {bulletin.isHidden && (
                               <Badge className="bg-rose-500/10 text-rose-600 border-none text-[9px] font-black uppercase">Hidden</Badge>
                             )}
                          </div>
                        </div>
                      </td>
                      <td className="px-10 py-6">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-secondary/50 flex items-center justify-center">
                            <Clock className="w-4 h-4 text-muted-foreground" />
                          </div>
                          <div>
                            <p className="text-xs font-black text-foreground uppercase tracking-tight">
                               {new Date(bulletin.postedDate).toLocaleDateString("en-US", { day: '2-digit', month: 'short' })}
                            </p>
                            <p className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest opacity-60">
                               {new Date(bulletin.postedDate).getFullYear()}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-10 py-6">
                         <div className="w-10 h-10 rounded-full bg-secondary/30 border border-border flex items-center justify-center">
                            <span className="text-xs font-black text-foreground">#{bulletin.rank}</span>
                         </div>
                      </td>
                      <td className="px-10 py-6 text-right">
                        <div className="flex items-center justify-end gap-3 opacity-0 group-hover:opacity-100 transition-all scale-95 group-hover:scale-100">
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => {
                              const win = window.open("", "_blank");
                              if (win) {
                                win.document.write(`
                                  <html>
                                    <head>
                                      <title>Preview Announcement - \${bulletin.title}</title>
                                      <style>
                                        body { font-family: sans-serif; padding: 40px; background: #f8f9fa; color: #333; line-height: 1.6; }
                                        .card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); max-width: 650px; margin: auto; }
                                        h1 { color: #111; font-size: 24px; margin-top: 0; border-bottom: 2px solid #eee; padding-bottom: 15px; }
                                        .meta { font-size: 13px; color: #666; margin: 15px 0 25px 0; }
                                        .content { font-size: 16px; color: #444; background: #f8f9fa; padding: 25px; border-radius: 12px; border: 1px solid #e9ecef; }
                                        .badge { display: inline-block; padding: 4px 10px; border-radius: 8px; font-weight: bold; background: #e7f5ff; color: #228be6; font-size: 11px; }
                                      </style>
                                    </head>
                                    <body>
                                      <div class="card">
                                        <span class="badge">\${bulletin.category.toUpperCase()}</span>
                                        <h1>📢 \${bulletin.title}</h1>
                                        <div class="meta">
                                          <strong>Posted Date:</strong> \${new Date(bulletin.postedDate).toLocaleDateString()}<br/>
                                          <strong>Priority Rank:</strong> #\${bulletin.rank}<br/>
                                          <strong>Target Groups:</strong> \${bulletin.employeeFilters.join(", ") || "All Employees"}
                                        </div>
                                        <div class="content">
                                          \${bulletin.description || "No description provided for this bulletin board announcement."}
                                        </div>
                                      </div>
                                    </body>
                                  </html>
                                `);
                                win.document.close();
                              }
                            }}
                            className="h-10 w-10 rounded-xl bg-background border border-border shadow-sm text-blue-500 hover:bg-blue-50 hover:text-blue-600"
                            title="View Announcement"
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => {
                              const element = document.createElement("a");
                              const contentText = `HRMS BULLETIN ANNOUNCEMENT\n\nTitle: ${bulletin.title}\nCategory: ${bulletin.category}\nPosted Date: ${bulletin.postedDate}\nRank: #${bulletin.rank}\n\nDescription:\n${bulletin.description || "No description."}`;
                              const file = new Blob([contentText], { type: 'text/plain' });
                              element.href = URL.createObjectURL(file);
                              element.download = `${bulletin.title.replace(/\s+/g, "_")}.txt`;
                              document.body.appendChild(element);
                              element.click();
                              document.body.removeChild(element);
                            }}
                            className="h-10 w-10 rounded-xl bg-background border border-border shadow-sm text-emerald-500 hover:bg-emerald-50 hover:text-emerald-600"
                            title="Download Announcement text"
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => handleEdit(bulletin)}
                            className="h-10 w-10 rounded-xl bg-background border border-border shadow-sm text-amber-500 hover:bg-amber-50 hover:text-amber-600"
                            title="Edit"
                          >
                            <Edit3 className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => handleDelete(bulletin.id)}
                            className="h-10 w-10 rounded-xl bg-background border border-border shadow-sm text-rose-500 hover:bg-rose-50 hover:text-rose-600"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {filteredBulletins.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-10 py-20 text-center">
                        <div className="flex flex-col items-center justify-center gap-4">
                          <Layers className="w-16 h-16 text-muted-foreground opacity-10" />
                          <div className="space-y-1">
                             <p className="text-lg font-black text-foreground uppercase tracking-tight">No Bulletins Found</p>
                             <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest opacity-60">Adjust your filters or create a new announcement</p>
                          </div>
                          <Button onClick={() => setIsModalOpen(true)} className="mt-4 bg-primary rounded-xl h-10 px-8 text-[10px] font-black uppercase tracking-widest">
                            Create First Bulletin
                          </Button>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <AddBulletinModal 
        isOpen={isModalOpen} 
        onClose={() => {
          setIsModalOpen(false);
          setEditBulletin(null);
        }}
        onSave={handleSave}
        editData={editBulletin}
      />
    </div>
  );
}
