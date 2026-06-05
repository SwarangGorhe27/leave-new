import React, { useState, useRef } from "react";
import { 
  Send, Mail, MessageSquare, Bell, Filter, Calendar, History, 
  ChevronRight, FileText, RefreshCw, BarChart2, Trash2, Eye, 
  Plus, X, Upload, Sparkles, Paperclip, AlertCircle, CheckCircle2, 
  ArrowLeft, ArrowRight, Check, List, Layers, ShieldAlert, Bold, Italic, ListIcon, Code, Search
} from "lucide-react";
import { toast } from "sonner";

// Types
interface Broadcast {
  id: string;
  category: string;
  subject: string;
  type: "Email" | "SMS" | "Email + SMS";
  date: string;
  status: "Sent" | "Draft" | "Scheduled";
  priority: "Low" | "Medium" | "High";
  employeeFilters: string[];
  content: string;
  smsMessage: string;
  attachments: { name: string; size: string; type: string }[];
  reachCount: number;
  successRate: number;
}

interface DeliveryLog {
  id: string;
  timestamp: string;
  employeeName: string;
  employeeId: string;
  channel: "Email" | "SMS";
  status: "Delivered" | "Bounced" | "Pending";
  remarks: string;
}

export interface CategoryMaster {
  name: string;
  code: string;
  description: string;
  rank: number;
  status: "Active" | "Inactive";
  visibility: "Internal" | "Employee Visible";
  color: string;
  icon?: string;
  createdDate: string;
}

// Initial Dynamic Masters
const INITIAL_CATEGORIES_OBJ: CategoryMaster[] = [
  {
    name: "General",
    code: "GEN",
    description: "General enterprise updates and circulars.",
    rank: 1,
    status: "Active",
    visibility: "Employee Visible",
    color: "indigo",
    icon: "Layers",
    createdDate: "2026-05-18"
  },
  {
    name: "Notification",
    code: "NOT",
    description: "System updates, policy reviews, and notifications.",
    rank: 2,
    status: "Active",
    visibility: "Employee Visible",
    color: "teal",
    icon: "Bell",
    createdDate: "2026-05-18"
  },
  {
    name: "H&R Campaign",
    code: "HRC",
    description: "Engagement programs, newsletters, and internal activities.",
    rank: 3,
    status: "Active",
    visibility: "Internal",
    color: "rose",
    icon: "Megaphone",
    createdDate: "2026-05-18"
  }
];

const INITIAL_CATEGORIES = ["General", "Notification", "H&R Campaign"];

const EMPLOYEE_FILTERS = [
  "All Employees",
  "Above 5 years",
  "All Current Employees",
  "All Past Employees",
  "Bangalore Employees",
  "Between 3 – 5 years",
  "Confirmed Employees",
  "Contract Emp",
  "Partially Vaccinated Employees",
  "Probation Emp",
  "Sales Department",
  "Trainee Employees",
  "Upto 3 years service"
];

// Initial mock data of past broadcasts
const INITIAL_BROADCASTS: Broadcast[] = [
  {
    id: "bc-1",
    category: "H&R Campaign",
    subject: "Annual Wellness Program 2026 Registration",
    type: "Email + SMS",
    date: "2026-05-18 10:30",
    status: "Sent",
    priority: "High",
    employeeFilters: ["All Current Employees", "Confirmed Employees"],
    content: "<h3>Dear Team,</h3><p>We are excited to announce that registration for the <strong>Annual Wellness Program 2026</strong> is now officially open! Join us for a year of physical health challenges, mental wellness seminars, and customized dietary sessions.</p><p>Please submit your registration by May 25th.</p>",
    smsMessage: "Wellness Program 2026 registrations are open! Please check your email for the detailed schedule and register before May 25th.",
    attachments: [
      { name: "wellness_brochure_2026.pdf", size: "2.4 MB", type: "pdf" },
      { name: "wellness_faq.docx", size: "1.1 MB", type: "docx" }
    ],
    reachCount: 840,
    successRate: 98.5
  },
  {
    id: "bc-2",
    category: "Notification",
    subject: "Scheduled Office Maintenance Checklist",
    type: "Email",
    date: "2026-05-19 22:00",
    status: "Scheduled",
    priority: "Medium",
    employeeFilters: ["Bangalore Employees"],
    content: "<p>Hello Bangalore Team,</p><p>Please note that the main office facility will undergo scheduled server rack maintenance this coming Saturday. Desktop internet services and backup drives may experience minor disruptions.</p>",
    smsMessage: "",
    attachments: [],
    reachCount: 420,
    successRate: 0.0
  },
  {
    id: "bc-3",
    category: "General",
    subject: "Draft Announcement regarding payroll updates",
    type: "SMS",
    date: "2026-05-15 14:15",
    status: "Draft",
    priority: "Low",
    employeeFilters: ["Contract Emp", "Trainee Employees"],
    content: "",
    smsMessage: "Draft Reminder: Please upload your timesheets by the end of today to avoid payroll delay.",
    attachments: [],
    reachCount: 180,
    successRate: 0.0
  }
];

const INITIAL_DELIVERY_LOGS: DeliveryLog[] = [
  { id: "log-1", timestamp: "2026-05-18 10:31", employeeName: "Rahul Sharma", employeeId: "EMP001", channel: "Email", status: "Delivered", remarks: "Delivered successfully to inbox." },
  { id: "log-2", timestamp: "2026-05-18 10:31", employeeName: "Rahul Sharma", employeeId: "EMP001", channel: "SMS", status: "Delivered", remarks: "SMS delivered to device." },
  { id: "log-3", timestamp: "2026-05-18 10:31", employeeName: "Priya Patel", employeeId: "EMP005", channel: "Email", status: "Delivered", remarks: "Delivered successfully to inbox." },
  { id: "log-4", timestamp: "2026-05-18 10:31", employeeName: "Amit Kumar", employeeId: "EMP008", channel: "Email", status: "Bounced", remarks: "Mailbox full / Temporary outage." },
  { id: "log-5", timestamp: "2026-05-18 10:31", employeeName: "Neha Gupta", employeeId: "EMP012", channel: "SMS", status: "Delivered", remarks: "SMS delivered to device." }
];

export function MassCommunicationPage() {
  const [activeTab, setActiveTab] = useState<"list" | "categories">("list");
  
  // Dynamic Masters State (Persisted in localStorage as CategoryMaster[])
  const [categories, setCategories] = useState<CategoryMaster[]>(() => {
    const saved = localStorage.getItem("hrms_comm_categories_obj");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0 && typeof parsed[0] === 'object') {
          return parsed;
        }
      } catch (e) {
        // Fallback
      }
    }
    
    // Check if old simple categories exist and migrate them
    const oldSaved = localStorage.getItem("hrms_comm_categories");
    if (oldSaved) {
      try {
        const parsed = JSON.parse(oldSaved);
        if (Array.isArray(parsed) && parsed.length > 0 && typeof parsed[0] === 'string') {
          const migrated = parsed.map((name, i) => ({
            name,
            code: name.substring(0, 3).toUpperCase(),
            description: `${name} communication category`,
            rank: i + 1,
            status: "Active" as const,
            visibility: "Employee Visible" as const,
            color: "indigo",
            icon: "Layers",
            createdDate: "2026-05-18"
          }));
          localStorage.setItem("hrms_comm_categories_obj", JSON.stringify(migrated));
          return migrated;
        }
      } catch (e) {
        // Fallback
      }
    }

    return INITIAL_CATEGORIES_OBJ;
  });
  
  // Only active categories appear in dropdowns for Compose
  const activeCategories = React.useMemo(() => {
    return categories.filter(c => c.status === "Active");
  }, [categories]);

  // Category Form States
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<CategoryMaster | null>(null);
  
  const [catName, setCatName] = useState("");
  const [catCode, setCatCode] = useState("");
  const [catDescription, setCatDescription] = useState("");
  const [catRank, setCatRank] = useState(1);
  const [catStatus, setCatStatus] = useState<"Active" | "Inactive">("Active");
  const [catVisibility, setCatVisibility] = useState<"Internal" | "Employee Visible">("Employee Visible");
  const [catColor, setCatColor] = useState("indigo");
  const [catIcon, setCatIcon] = useState("Layers");

  const [categorySearchQuery, setCategorySearchQuery] = useState("");
  const [newCategoryName, setNewCategoryName] = useState("");
  
  // Broadcast State (Persisted in localStorage)
  const [broadcasts, setBroadcasts] = useState<Broadcast[]>(() => {
    const saved = localStorage.getItem("hrms_comm_broadcasts");
    return saved ? JSON.parse(saved) : INITIAL_BROADCASTS;
  });
  const [deliveryLogs, setDeliveryLogs] = useState<DeliveryLog[]>(INITIAL_DELIVERY_LOGS);
  
  // Grid filters, search & pagination
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState("All");
  const [selectedTypeFilter, setSelectedTypeFilter] = useState("All");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  // View modal, Compose modal state
  const [isComposeOpen, setIsComposeOpen] = useState(false);
  const [isViewOpen, setIsViewOpen] = useState(false);
  const [selectedBroadcast, setSelectedBroadcast] = useState<Broadcast | null>(null);

  // Composer Form States
  const [composerCategory, setComposerCategory] = useState("General");
  const [composerFilters, setComposerFilters] = useState<string[]>([]);
  const [composerMode, setComposerMode] = useState<"Email" | "SMS" | "Email + SMS">("Email");
  const [composerPriority, setComposerPriority] = useState<"Low" | "Medium" | "High">("Medium");
  const [composerSubject, setComposerSubject] = useState("");
  const [composerContent, setComposerContent] = useState("");
  const [composerSms, setComposerSms] = useState("");
  const [composerSchedule, setComposerSchedule] = useState("");
  const [composerAttachments, setComposerAttachments] = useState<{ name: string; size: string; type: string }[]>([]);

  // Drag and drop attachment ref
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Edit State
  const [editingBroadcastId, setEditingBroadcastId] = useState<string | null>(null);

  // Dynamic Reach Calculator (Simulated)
  const calculateReach = (filters: string[]) => {
    if (filters.length === 0 || filters.includes("All Employees")) return 1248;
    let reach = 0;
    filters.forEach(f => {
      if (f.includes("Bangalore")) reach += 310;
      else if (f.includes("Sales")) reach += 240;
      else if (f.includes("5 years")) reach += 180;
      else if (f.includes("Probation")) reach += 95;
      else reach += 140;
    });
    return Math.min(reach, 1248);
  };

  // Drag and Drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(e.target.files);
    }
  };

  const processFiles = (files: FileList) => {
    const allowedExtensions = ["pdf", "xls", "xlsx", "doc", "docx", "txt", "ppt", "pptx", "gif", "jpg", "png"];
    const maxSizeBytes = 5 * 1024 * 1024; // 5 MB

    const validNewFiles: { name: string; size: string; type: string }[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const ext = file.name.split('.').pop()?.toLowerCase() || "";
      if (!allowedExtensions.includes(ext)) {
        toast.error(`Invalid file type for: ${file.name}. Only PDF, Excel, Word, PPT, TXT & Images are allowed.`);
        continue;
      }
      if (file.size > maxSizeBytes) {
        toast.error(`File size exceeds 5MB limit: ${file.name}`);
        continue;
      }
      const sizeStr = (file.size / (1024 * 1024)).toFixed(1) + " MB";
      validNewFiles.push({ name: file.name, size: sizeStr, type: ext });
    }
    if (validNewFiles.length > 0) {
      setComposerAttachments(prev => [...prev, ...validNewFiles]);
      toast.success(`${validNewFiles.length} file(s) attached successfully!`);
    }
  };

  const removeAttachment = (index: number) => {
    setComposerAttachments(prev => prev.filter((_, i) => i !== index));
    toast.success("Attachment removed.");
  };

  // Add format tags into editor content
  const applyTextFormat = (tag: string) => {
    if (tag === "bold") setComposerContent(prev => prev + "<strong></strong>");
    if (tag === "italic") setComposerContent(prev => prev + "<em></em>");
    if (tag === "list") setComposerContent(prev => prev + "<ul>\n  <li>Item 1</li>\n</ul>");
    if (tag === "code") setComposerContent(prev => prev + "<code></code>");
  };

  // Composer submit handlers
  const handleComposeSubmit = (status: "Sent" | "Draft" | "Scheduled") => {
    if (composerFilters.length === 0) {
      toast.warning("Please select at least one target Employee Filter.");
      return;
    }
    
    if (composerMode !== "SMS") {
      if (!composerSubject.trim()) {
        toast.warning("Subject Line is required for Mail communications.");
        return;
      }
      if (!composerContent.trim()) {
        toast.warning("Email Content is required.");
        return;
      }
    }

    if (composerMode !== "Email") {
      if (!composerSms.trim()) {
        toast.warning("SMS Message is required.");
        return;
      }
    }

    const reach = calculateReach(composerFilters);
    const newBroadcast: Broadcast = {
      id: editingBroadcastId || `bc-${Date.now()}`,
      category: composerCategory,
      subject: composerMode === "SMS" ? "(SMS Communication)" : composerSubject,
      type: composerMode,
      date: composerSchedule ? composerSchedule.replace("T", " ") : new Date().toISOString().slice(0, 16).replace("T", " "),
      status: status,
      priority: composerPriority,
      employeeFilters: composerFilters,
      content: composerContent,
      smsMessage: composerSms,
      attachments: composerAttachments,
      reachCount: reach,
      successRate: status === "Sent" ? 98.8 : 0.0
    };

    let updatedList = [...broadcasts];
    if (editingBroadcastId) {
      updatedList = broadcasts.map(b => b.id === editingBroadcastId ? newBroadcast : b);
      toast.success("Communication draft updated successfully!");
    } else {
      updatedList = [newBroadcast, ...broadcasts];
      toast.success(status === "Sent" ? "Communication broadcast sent!" : status === "Scheduled" ? "Communication scheduled successfully!" : "Draft announcement saved!");
    }
    
    setBroadcasts(updatedList);
    localStorage.setItem("hrms_comm_broadcasts", JSON.stringify(updatedList));

    // Reset filters to guarantee the newly composed communication is immediately visible
    setSelectedCategoryFilter("All");
    setSelectedTypeFilter("All");
    setSearchTerm("");
    setCurrentPage(1);

    // Add mock delivery logs if sent
    if (status === "Sent") {
      const newLogs: DeliveryLog[] = [
        { id: `log-${Date.now()}-1`, timestamp: new Date().toISOString().slice(0, 16).replace("T", " "), employeeName: "Rahul Sharma", employeeId: "EMP001", channel: composerMode.includes("Email") ? "Email" : "SMS", status: "Delivered", remarks: "Delivered successfully." },
        { id: `log-${Date.now()}-2`, timestamp: new Date().toISOString().slice(0, 16).replace("T", " "), employeeName: "Priya Patel", employeeId: "EMP005", channel: composerMode.includes("SMS") ? "SMS" : "Email", status: "Delivered", remarks: "Delivered successfully." }
      ];
      setDeliveryLogs(prev => [...newLogs, ...prev]);
    }

    resetComposer();
  };

  const resetComposer = () => {
    setIsComposeOpen(false);
    setEditingBroadcastId(null);
    setComposerCategory("General");
    setComposerFilters([]);
    setComposerMode("Email");
    setComposerPriority("Medium");
    setComposerSubject("");
    setComposerContent("");
    setComposerSms("");
    setComposerSchedule("");
    setComposerAttachments([]);
  };

  const openComposeForEdit = (bc: Broadcast) => {
    setEditingBroadcastId(bc.id);
    setComposerCategory(bc.category);
    setComposerFilters(bc.employeeFilters);
    setComposerMode(bc.type);
    setComposerPriority(bc.priority);
    setComposerSubject(bc.subject);
    setComposerContent(bc.content);
    setComposerSms(bc.smsMessage);
    setComposerSchedule(bc.date.replace(" ", "T"));
    setComposerAttachments(bc.attachments);
    setIsComposeOpen(true);
  };

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this communication log?")) {
      const updatedList = broadcasts.filter(b => b.id !== id);
      setBroadcasts(updatedList);
      localStorage.setItem("hrms_comm_broadcasts", JSON.stringify(updatedList));
      toast.error("Communication record deleted.");
    }
  };

  const handleResend = (bc: Broadcast) => {
    const updated = {
      ...bc,
      status: "Sent" as const,
      date: new Date().toISOString().slice(0, 16).replace("T", " "),
      successRate: 99.2
    };
    const updatedList = broadcasts.map(b => b.id === bc.id ? updated : b);
    setBroadcasts(updatedList);
    localStorage.setItem("hrms_comm_broadcasts", JSON.stringify(updatedList));
    toast.success(`Queued & resent: "${bc.subject || "SMS Message"}" to targets successfully!`);
  };

  const resetCategoryForm = () => {
    setEditingCategory(null);
    setCatName("");
    setCatCode("");
    setCatDescription("");
    setCatRank(categories.length + 1);
    setCatStatus("Active");
    setCatVisibility("Employee Visible");
    setCatColor("indigo");
    setCatIcon("Layers");
    setIsCategoryModalOpen(false);
  };

  const openCategoryForEdit = (cat: CategoryMaster) => {
    setEditingCategory(cat);
    setCatName(cat.name);
    setCatCode(cat.code);
    setCatDescription(cat.description);
    setCatRank(cat.rank);
    setCatStatus(cat.status);
    setCatVisibility(cat.visibility);
    setCatColor(cat.color);
    setCatIcon(cat.icon || "Layers");
    setIsCategoryModalOpen(true);
  };

  const handleCategoryFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!catName.trim()) {
      toast.warning("Category Name is required.");
      return;
    }
    if (!catCode.trim()) {
      toast.warning("Category Code is required.");
      return;
    }

    const newCat: CategoryMaster = {
      name: catName.trim(),
      code: catCode.trim().toUpperCase(),
      description: catDescription.trim(),
      rank: Number(catRank),
      status: catStatus,
      visibility: catVisibility,
      color: catColor,
      icon: catIcon,
      createdDate: editingCategory ? editingCategory.createdDate : new Date().toISOString().split("T")[0]
    };

    let updatedCats = [...categories];
    if (editingCategory) {
      updatedCats = categories.map(c => c.name.toLowerCase() === editingCategory.name.toLowerCase() ? newCat : c);
      toast.success(`Category "${newCat.name}" updated successfully!`);
    } else {
      if (categories.some(c => c.name.toLowerCase() === newCat.name.toLowerCase())) {
        toast.warning("A category with this name already exists.");
        return;
      }
      if (categories.some(c => c.code.toLowerCase() === newCat.code.toLowerCase())) {
        toast.warning("A category with this code already exists.");
        return;
      }
      updatedCats = [...categories, newCat];
      toast.success(`Category "${newCat.name}" registered successfully!`);
    }

    setCategories(updatedCats);
    localStorage.setItem("hrms_comm_categories_obj", JSON.stringify(updatedCats));
    localStorage.setItem("hrms_comm_categories", JSON.stringify(updatedCats.map(c => c.name)));

    resetCategoryForm();
  };

  const handleCategoryStatusToggle = (cat: CategoryMaster) => {
    const updatedStatus = cat.status === "Active" ? "Inactive" : "Active";
    const updatedCats = categories.map(c => c.name === cat.name ? { ...c, status: updatedStatus as any } : c);
    setCategories(updatedCats);
    localStorage.setItem("hrms_comm_categories_obj", JSON.stringify(updatedCats));
    localStorage.setItem("hrms_comm_categories", JSON.stringify(updatedCats.map(c => c.name)));
    toast.success(`Category "${cat.name}" is now ${updatedStatus}!`);
  };

  const handleCategoryDelete = (catName: string) => {
    if (confirm(`Are you sure you want to delete category "${catName}"? This will not affect existing broadcasts.`)) {
      const updatedCats = categories.filter(c => c.name !== catName);
      setCategories(updatedCats);
      localStorage.setItem("hrms_comm_categories_obj", JSON.stringify(updatedCats));
      localStorage.setItem("hrms_comm_categories", JSON.stringify(updatedCats.map(c => c.name)));
      toast.error(`Category "${catName}" removed from masters.`);
    }
  };

  // Filtered lists
  const filteredBroadcasts = broadcasts.filter(b => {
    const matchesSearch = b.subject.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          b.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          b.smsMessage.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategoryFilter === "All" || b.category === selectedCategoryFilter;
    const matchesType = selectedTypeFilter === "All" || b.type === selectedTypeFilter;
    return matchesSearch && matchesCategory && matchesType;
  });

  // Pagination calculations
  const totalPages = Math.ceil(filteredBroadcasts.length / itemsPerPage) || 1;
  const currentBroadcasts = filteredBroadcasts.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const reachedTotal = broadcasts.reduce((sum, b) => sum + (b.status === "Sent" ? b.reachCount : 0), 0);
  const activeDraftsCount = broadcasts.filter(b => b.status === "Draft").length;
  const scheduledCount = broadcasts.filter(b => b.status === "Scheduled").length;

  return (
    <div className="portal-page admin-dashboard">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-card p-6 rounded-xl border border-border shadow-sm">
        {/* <div className="space-y-1">
          <h2 className="text-2xl font-black text-foreground flex items-center gap-2">
            <Send className="w-6 h-6 text-indigo-500 animate-pulse" />
            Mass Communication Center
          </h2>
          <p className="text-sm text-muted-foreground">Broadcast responsive emails, SMS messages, and campaign notifications to target groups dynamically.</p>
        </div> */}
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsComposeOpen(true)}
            className="flex items-center gap-2 px-5 py-2.5 bg-primary text-primary-foreground text-sm font-bold rounded-lg hover:opacity-90 transition-all shadow-lg shadow-primary/20"
          >
            <Plus className="w-4 h-4" />
            Compose Communication
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center border-b border-border">
        <button
          onClick={() => setActiveTab("list")}
          className={`px-6 py-3 text-sm font-bold flex items-center gap-2 transition-all border-b-2 ${
            activeTab === "list" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <List className="w-4 h-4" />
          Broadcast Directory
        </button>
        <button
          onClick={() => setActiveTab("categories")}
          className={`px-6 py-3 text-sm font-bold flex items-center gap-2 transition-all border-b-2 ${
            activeTab === "categories" ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          <Layers className="w-4 h-4" />
          Category Masters Manager
        </button>
      </div>

      {activeTab === "list" ? (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main List */}
          <div className="lg:col-span-3 space-y-6">
            {/* Filters panel */}
            <div className="bg-card p-5 rounded-xl border border-border shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
              <div className="flex items-center gap-3 flex-wrap w-full md:w-auto">
                <div className="relative flex-1 md:w-64">
                  <Filter className="w-4 h-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Search subject or contents..."
                    value={searchTerm}
                    onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                    className="w-full pl-9 pr-4 py-2 bg-secondary/50 border border-border rounded-lg text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary/20"
                  />
                </div>

                <select
                  value={selectedCategoryFilter}
                  onChange={(e) => { setSelectedCategoryFilter(e.target.value); setCurrentPage(1); }}
                  className="px-3 py-2 bg-secondary/50 border border-border rounded-lg text-xs font-bold text-foreground outline-none cursor-pointer"
                >
                  <option value="All">All Categories</option>
                  {categories.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
                </select>

                <select
                  value={selectedTypeFilter}
                  onChange={(e) => { setSelectedTypeFilter(e.target.value); setCurrentPage(1); }}
                  className="px-3 py-2 bg-secondary/50 border border-border rounded-lg text-xs font-bold text-foreground outline-none cursor-pointer"
                >
                  <option value="All">All Types</option>
                  <option value="Email">Email</option>
                  <option value="SMS">SMS</option>
                  <option value="Email + SMS">Email + SMS</option>
                </select>
              </div>

              <div className="text-xs font-bold text-muted-foreground">
                Showing {filteredBroadcasts.length} Broadcasts
              </div>
            </div>

            {/* Broadcast Table */}
            <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-muted/40 border-b border-border">
                      <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Category</th>
                      <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Subject / Details</th>
                      <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Type</th>
                      <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Date / Time</th>
                      <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Status</th>
                      <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {currentBroadcasts.map((bc) => (
                      <tr key={bc.id} className="hover:bg-secondary/20 transition-colors group">
                        <td className="px-6 py-4">
                          <span className="px-2.5 py-1 rounded-md text-[10px] font-black uppercase tracking-wider bg-indigo-50 text-indigo-600 border border-indigo-100">
                            {bc.category}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div>
                            <div className="text-sm font-bold text-foreground truncate max-w-[280px]">
                              {bc.type === "SMS" ? bc.smsMessage : bc.subject}
                            </div>
                            {bc.type === "Email + SMS" && (
                              <div className="text-[10px] text-muted-foreground font-semibold truncate max-w-[280px] italic mt-0.5">
                                SMS: "{bc.smsMessage}"
                              </div>
                            )}
                            <div className="text-[11px] text-muted-foreground mt-1">
                              Reach: <strong className="text-foreground">{bc.reachCount} emp</strong>
                              {bc.status === "Sent" && ` • Success: ${bc.successRate}%`}
                              {bc.priority === "High" && <span className="ml-2 text-rose-500 font-extrabold uppercase text-[9px] tracking-wider bg-rose-50 px-1 py-0.5 rounded">High Priority</span>}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-1.5 text-xs font-semibold text-foreground">
                            {bc.type.includes("Email") && <Mail className="w-3.5 h-3.5 text-indigo-500" />}
                            {bc.type.includes("SMS") && <MessageSquare className="w-3.5 h-3.5 text-teal-500" />}
                            <span>{bc.type}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-xs font-bold text-muted-foreground">{bc.date}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            bc.status === "Sent" ? "bg-emerald-500/10 text-emerald-600 border border-emerald-500/20" :
                            bc.status === "Scheduled" ? "bg-amber-500/10 text-amber-600 border border-amber-500/20" :
                            "bg-zinc-500/10 text-zinc-600 border border-zinc-500/20"
                          }`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${
                              bc.status === "Sent" ? "bg-emerald-500" :
                              bc.status === "Scheduled" ? "bg-amber-500" :
                              "bg-zinc-400"
                            }`} />
                            {bc.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => { setSelectedBroadcast(bc); setIsViewOpen(true); }}
                              className="p-1.5 rounded-md hover:bg-secondary text-muted-foreground hover:text-foreground transition-all"
                              title="View Details"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            {bc.status === "Draft" ? (
                              <button
                                onClick={() => openComposeForEdit(bc)}
                                className="p-1.5 rounded-md hover:bg-secondary text-muted-foreground hover:text-foreground transition-all"
                                title="Edit Draft"
                              >
                                <History className="w-4 h-4 text-blue-500" />
                              </button>
                            ) : (
                              <button
                                onClick={() => handleResend(bc)}
                                className="p-1.5 rounded-md hover:bg-emerald-50 text-emerald-600 transition-all"
                                title="Resend Announcement"
                              >
                                <RefreshCw className="w-4 h-4" />
                              </button>
                            )}
                            <button
                              onClick={() => handleDelete(bc.id)}
                              className="p-1.5 rounded-md hover:bg-rose-50 text-rose-600 transition-all"
                              title="Delete Record"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {filteredBroadcasts.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-6 py-12 text-center text-muted-foreground text-sm font-semibold">
                          No matching broadcasts found in this master directory.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* Pagination controls */}
              {totalPages > 1 && (
                <div className="px-6 py-4 border-t border-border bg-muted/20 flex items-center justify-between">
                  <span className="text-xs text-muted-foreground font-semibold">
                    Page <strong className="text-foreground">{currentPage}</strong> of {totalPages}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="p-1.5 border border-border rounded hover:bg-secondary disabled:opacity-50 transition-colors"
                    >
                      <ArrowLeft className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="p-1.5 border border-border rounded hover:bg-secondary disabled:opacity-50 transition-colors"
                    >
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar reach & delivery metrics */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
              <h3 className="text-xs font-black text-foreground uppercase tracking-widest flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-primary" />
                Live Broadcast Reach
              </h3>

              <div className="space-y-3 pt-2">
                <div className="p-3 bg-indigo-50/40 rounded-lg border border-indigo-100 space-y-1">
                  <p className="text-[10px] font-black text-indigo-500 uppercase tracking-wide">Delivered Successfully</p>
                  <p className="text-2xl font-black text-indigo-900">{reachedTotal}</p>
                </div>
                <div className="p-3 bg-amber-50/40 rounded-lg border border-amber-100 space-y-1">
                  <p className="text-[10px] font-black text-amber-500 uppercase tracking-wide">Scheduled Announcements</p>
                  <p className="text-2xl font-black text-amber-900">{scheduledCount}</p>
                </div>
                <div className="p-3 bg-zinc-50/50 rounded-lg border border-zinc-100 space-y-1">
                  <p className="text-[10px] font-black text-zinc-500 uppercase tracking-wide font-mono">Draft Campaigns</p>
                  <p className="text-2xl font-black text-zinc-800">{activeDraftsCount}</p>
                </div>
              </div>
            </div>


          </div>
        </div>
      ) : (
        /* Upgraded Categories Masters Tab */
        <div className="space-y-6">
          {/* Header Action Bar */}
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <h3 className="text-base font-extrabold text-foreground flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-500" />
                Dynamic Communication Categories Master
              </h3>
              <p className="text-xs text-muted-foreground">Overhaul and manage custom enterprise category presets across communication layers.</p>
            </div>
            <button
              type="button"
              onClick={() => {
                resetCategoryForm();
                setIsCategoryModalOpen(true);
              }}
              className="px-5 py-2.5 bg-primary text-primary-foreground text-xs font-bold rounded-lg hover:opacity-90 transition-all flex items-center justify-center gap-1.5 shadow-sm shadow-primary/20"
            >
              <Plus className="w-3.5 h-3.5" /> Add New Category
            </button>
          </div>

          {/* Search and Listing table */}
          <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden space-y-4 p-5">
            <div className="flex items-center gap-3 max-w-sm">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search Category Name or Code..."
                  value={categorySearchQuery}
                  onChange={(e) => setCategorySearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 bg-secondary/50 border border-border rounded-lg text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
              </div>
            </div>

            <div className="overflow-x-auto border border-border/60 rounded-lg">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-muted/40 border-b border-border">
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Name & Code</th>
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Description</th>
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground text-center">Rank</th>
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Visibility</th>
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Status</th>
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Created Date</th>
                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {categories
                    .filter(c => 
                      c.name.toLowerCase().includes(categorySearchQuery.toLowerCase()) || 
                      c.code.toLowerCase().includes(categorySearchQuery.toLowerCase())
                    )
                    .map((cat) => (
                      <tr key={cat.name} className="hover:bg-secondary/20 transition-colors group">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <span className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs bg-indigo-50 text-indigo-600 border border-indigo-100">
                              {cat.code}
                            </span>
                            <div>
                              <div className="text-sm font-bold text-foreground">{cat.name}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-xs text-muted-foreground font-semibold max-w-[200px] truncate" title={cat.description}>
                          {cat.description || <span className="italic opacity-60">No description provided</span>}
                        </td>
                        <td className="px-6 py-4 text-xs font-extrabold text-foreground text-center">
                          {cat.rank}
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider ${
                            cat.visibility === "Internal" ? "bg-amber-50 text-amber-600 border border-amber-100" : "bg-teal-50 text-teal-600 border border-teal-100"
                          }`}>
                            {cat.visibility}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <button
                            type="button"
                            onClick={() => handleCategoryStatusToggle(cat)}
                            className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-widest transition-all ${
                              cat.status === "Active" ? "bg-emerald-50 text-emerald-600 border border-emerald-100" : "bg-zinc-100 text-zinc-500 border border-zinc-200"
                            }`}
                          >
                            <span className={`w-1.5 h-1.5 rounded-full ${cat.status === "Active" ? "bg-emerald-500 animate-pulse" : "bg-zinc-400"}`} />
                            {cat.status}
                          </button>
                        </td>
                        <td className="px-6 py-4 text-xs font-bold text-muted-foreground">
                          {cat.createdDate}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              type="button"
                              onClick={() => openCategoryForEdit(cat)}
                              className="p-1.5 rounded-md hover:bg-secondary text-blue-600 hover:text-blue-700 transition-all"
                              title="Edit Category"
                            >
                              <History className="w-4 h-4" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleCategoryDelete(cat.name)}
                              className="p-1.5 rounded-md hover:bg-rose-50 text-rose-500 hover:text-rose-600 transition-all"
                              title="Delete Category"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  {categories.filter(c => 
                    c.name.toLowerCase().includes(categorySearchQuery.toLowerCase()) || 
                    c.code.toLowerCase().includes(categorySearchQuery.toLowerCase())
                  ).length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-6 py-10 text-center text-xs text-muted-foreground font-semibold">
                        No categories match the active filters or search queries.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* DYNAMIC CATEGORY MASTER MODAL */}
          {isCategoryModalOpen && (
            <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <div className="bg-card w-full max-w-md rounded-2xl border border-border shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in-95">
                <div className="p-5 border-b border-border bg-muted/20 flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-black text-foreground flex items-center gap-2">
                      <Layers className="w-4 h-4 text-indigo-500" />
                      {editingCategory ? "Configure Master Category" : "Register Master Category"}
                    </h3>
                    <p className="text-xs text-muted-foreground mt-0.5">Configure systemic tags and priority tags for communications.</p>
                  </div>
                  <button type="button" onClick={resetCategoryForm} className="p-1.5 hover:bg-secondary rounded-lg transition-colors">
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <form onSubmit={handleCategoryFormSubmit} className="p-5 space-y-4 text-xs font-semibold text-foreground">
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Category Name *</label>
                    <input
                      type="text"
                      placeholder="e.g. Health & Safety"
                      value={catName}
                      onChange={(e) => setCatName(e.target.value)}
                      className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Category Code (Short) *</label>
                      <input
                        type="text"
                        placeholder="e.g. H&S"
                        maxLength={10}
                        value={catCode}
                        onChange={(e) => setCatCode(e.target.value.toUpperCase())}
                        className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none"
                        required
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Display Rank / Order</label>
                      <input
                        type="number"
                        min={1}
                        value={catRank}
                        onChange={(e) => setCatRank(Number(e.target.value))}
                        className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Description</label>
                    <textarea
                      placeholder="Enter a brief summary of communications targeting this tag category..."
                      value={catDescription}
                      onChange={(e) => setCatDescription(e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary/20 outline-none resize-none"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Status</label>
                      <select
                        value={catStatus}
                        onChange={(e) => setCatStatus(e.target.value as any)}
                        className="w-full px-3 py-2 bg-background border border-border rounded-lg outline-none cursor-pointer text-xs"
                      >
                        <option value="Active">Active</option>
                        <option value="Inactive">Inactive</option>
                      </select>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Visibility Scope</label>
                      <select
                        value={catVisibility}
                        onChange={(e) => setCatVisibility(e.target.value as any)}
                        className="w-full px-3 py-2 bg-background border border-border rounded-lg outline-none cursor-pointer text-xs"
                      >
                        <option value="Employee Visible">Employee Visible</option>
                        <option value="Internal">Internal Only (HR/Admin)</option>
                      </select>
                    </div>
                  </div>


                  <div className="pt-4 border-t border-border flex items-center justify-end gap-2">
                    <button
                      type="button"
                      onClick={resetCategoryForm}
                      className="px-4 py-2 border border-border rounded-lg text-xs font-bold hover:bg-secondary transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-5 py-2 bg-primary text-primary-foreground rounded-lg text-xs font-bold hover:opacity-90 transition-all shadow-sm"
                    >
                      {editingCategory ? "Save Changes" : "Create Master"}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      )}

      {/* VIEW MODAL */}
      {isViewOpen && selectedBroadcast && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card w-full max-w-2xl rounded-2xl border border-border shadow-2xl overflow-hidden flex flex-col max-h-[85vh] animate-in fade-in zoom-in-95">
            <div className="p-6 border-b border-border bg-muted/20 flex items-center justify-between">
              <div>
                <span className="px-2.5 py-1 rounded text-[10px] font-black uppercase bg-primary/10 text-primary border border-primary/20">
                  {selectedBroadcast.category}
                </span>
                <h3 className="text-base font-black text-foreground mt-2">{selectedBroadcast.subject}</h3>
              </div>
              <button onClick={() => setIsViewOpen(false)} className="p-1.5 hover:bg-secondary rounded-lg transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-6 overflow-y-auto flex-1 text-sm">
              <div className="grid grid-cols-2 gap-4 text-xs bg-secondary/20 p-4 rounded-xl border border-border">
                <div>
                  <p className="text-muted-foreground font-semibold">Dispatch Type:</p>
                  <p className="font-bold text-foreground mt-0.5">{selectedBroadcast.type}</p>
                </div>
                <div>
                  <p className="text-muted-foreground font-semibold">Send Date:</p>
                  <p className="font-bold text-foreground mt-0.5">{selectedBroadcast.date}</p>
                </div>
                <div>
                  <p className="text-muted-foreground font-semibold">Reach Group:</p>
                  <p className="font-bold text-foreground mt-0.5 truncate">{selectedBroadcast.employeeFilters.join(", ")}</p>
                </div>
                <div>
                  <p className="text-muted-foreground font-semibold">Campaign Status:</p>
                  <p className="font-bold text-foreground mt-0.5">{selectedBroadcast.status}</p>
                </div>
              </div>

              {selectedBroadcast.type.includes("Email") && selectedBroadcast.content && (
                <div className="space-y-2">
                  <h4 className="text-xs font-black text-muted-foreground uppercase tracking-widest">Email Content Preview</h4>
                  <div 
                    className="p-5 border border-border rounded-xl bg-background prose prose-sm max-w-none text-foreground"
                    dangerouslySetInnerHTML={{ __html: selectedBroadcast.content }}
                  />
                </div>
              )}

              {selectedBroadcast.type.includes("SMS") && selectedBroadcast.smsMessage && (
                <div className="space-y-2">
                  <h4 className="text-xs font-black text-muted-foreground uppercase tracking-widest">SMS Message Preview</h4>
                  <div className="p-4 border border-border rounded-xl bg-background font-mono text-xs text-foreground">
                    {selectedBroadcast.smsMessage}
                  </div>
                </div>
              )}

              {selectedBroadcast.attachments.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-black text-muted-foreground uppercase tracking-widest">Attachments ({selectedBroadcast.attachments.length})</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {selectedBroadcast.attachments.map((file, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2.5 bg-secondary/30 rounded-lg border border-border text-xs">
                        <div className="flex items-center gap-2">
                          <Paperclip className="w-3.5 h-3.5 text-muted-foreground" />
                          <span className="font-semibold truncate max-w-[140px]">{file.name}</span>
                        </div>
                        <span className="text-[10px] text-muted-foreground font-bold">{file.size}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 border-t border-border bg-muted/20 flex items-center justify-end gap-2">
              <button 
                onClick={() => setIsViewOpen(false)}
                className="px-4 py-2 border border-border text-xs font-bold rounded-lg hover:bg-secondary transition-colors"
              >
                Close Preview
              </button>
              {selectedBroadcast.status !== "Draft" && (
                <button
                  onClick={() => { handleResend(selectedBroadcast); setIsViewOpen(false); }}
                  className="px-4 py-2 bg-primary text-primary-foreground text-xs font-bold rounded-lg hover:opacity-90 transition-all flex items-center gap-1.5"
                >
                  <RefreshCw className="w-3.5 h-3.5" /> Resend Broadcast
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* COMPOSE & EDIT MODAL */}
      {isComposeOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card w-full max-w-3xl rounded-2xl border border-border shadow-2xl overflow-hidden flex flex-col max-h-[92vh] animate-in fade-in zoom-in-95">
            <div className="p-6 border-b border-border bg-muted/20 flex items-center justify-between">
              <div>
                <h3 className="text-base font-black text-foreground flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-indigo-500 animate-spin" />
                  {editingBroadcastId ? "Edit Communication Draft" : "Compose Dynamic Broadcast"}
                </h3>
                <p className="text-xs text-muted-foreground mt-0.5">Define target parameters, customize content modes, and configure files.</p>
              </div>
              <button onClick={resetComposer} className="p-1.5 hover:bg-secondary rounded-lg transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-5 overflow-y-auto flex-1 text-sm">
              {/* Category, Mode, Priority */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-1.5">
                  <div className="flex justify-between items-center">
                    <label className="text-xs font-black text-muted-foreground uppercase tracking-wider">Category (Master)</label>
                    <button
                      type="button"
                      onClick={() => {
                        const newCat = prompt("Enter new category name:");
                        if (newCat && newCat.trim()) {
                          const trimmed = newCat.trim();
                          if (categories.some(c => c.name.toLowerCase() === trimmed.toLowerCase())) {
                            toast.warning("Category already exists.");
                          } else {
                            const newMaster: CategoryMaster = {
                              name: trimmed,
                              code: trimmed.substring(0, 3).toUpperCase(),
                              description: `${trimmed} communications`,
                              rank: categories.length + 1,
                              status: "Active",
                              visibility: "Employee Visible",
                              color: "indigo",
                              icon: "Layers",
                              createdDate: new Date().toISOString().split("T")[0]
                            };
                            const updatedCats = [...categories, newMaster];
                            setCategories(updatedCats);
                            localStorage.setItem("hrms_comm_categories_obj", JSON.stringify(updatedCats));
                            localStorage.setItem("hrms_comm_categories", JSON.stringify(updatedCats.map(c => c.name)));
                            setComposerCategory(trimmed);
                            toast.success(`Category "${trimmed}" added & selected!`);
                          }
                        }
                      }}
                      className="text-[10px] text-primary font-bold hover:underline flex items-center gap-0.5"
                    >
                      <Plus size={10} /> Add New
                    </button>
                  </div>
                  <select
                    value={composerCategory}
                    onChange={(e) => setComposerCategory(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg text-xs font-bold text-foreground outline-none outline-0 cursor-pointer"
                  >
                    {activeCategories.map(c => <option key={c.name} value={c.name}>{c.name}</option>)}
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-black text-muted-foreground uppercase tracking-wider">Communication Mode</label>
                  <select
                    value={composerMode}
                    onChange={(e) => setComposerMode(e.target.value as any)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg text-xs font-bold text-foreground outline-none outline-0 cursor-pointer"
                  >
                    <option value="Email">Email Only</option>
                    <option value="SMS">SMS Only</option>
                    <option value="Email + SMS">Combined (Email + SMS)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-black text-muted-foreground uppercase tracking-wider">Priority Level</label>
                  <div className="flex gap-2">
                    {["Low", "Medium", "High"].map((p) => (
                      <button
                        key={p}
                        type="button"
                        onClick={() => setComposerPriority(p as any)}
                        className={`flex-1 py-2 text-[10px] font-black uppercase tracking-wider rounded-lg border transition-all ${
                          composerPriority === p 
                            ? p === "High" ? "bg-rose-500/10 border-rose-500 text-rose-600" :
                              p === "Medium" ? "bg-amber-500/10 border-amber-500 text-amber-600" :
                              "bg-zinc-500/10 border-zinc-500 text-zinc-600"
                            : "bg-transparent border-border text-muted-foreground hover:bg-secondary/40"
                        }`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Target Audience Filters */}
              <div className="space-y-2">
                <label className="text-xs font-black text-muted-foreground uppercase tracking-wider">Target Employee Groups (Masters)</label>
                <div className="flex flex-wrap gap-1.5 p-3 bg-secondary/30 border border-border rounded-xl min-h-[50px]">
                  {composerFilters.map(f => (
                    <span key={f} className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-indigo-50 border border-indigo-100 text-[11px] font-bold text-indigo-700">
                      {f}
                      <button 
                        type="button" 
                        onClick={() => setComposerFilters(prev => prev.filter(item => item !== f))}
                        className="hover:text-rose-500 transition-colors"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                  {composerFilters.length === 0 && (
                    <span className="text-xs text-muted-foreground italic flex items-center gap-1.5">
                      <AlertCircle className="w-3.5 h-3.5 text-amber-500" /> No audience filters selected. Message will not target any records.
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {EMPLOYEE_FILTERS.map(f => {
                    const isSelected = composerFilters.includes(f);
                    return (
                      <button
                        key={f}
                        type="button"
                        onClick={() => {
                          if (isSelected) {
                            setComposerFilters(prev => prev.filter(item => item !== f));
                          } else {
                            setComposerFilters(prev => [...prev, f]);
                          }
                        }}
                        className={`px-2.5 py-1 rounded text-[10px] font-bold transition-all border ${
                          isSelected 
                            ? "bg-indigo-500 border-indigo-500 text-white" 
                            : "bg-background border-border text-muted-foreground hover:bg-secondary"
                        }`}
                      >
                        {f}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Schedule Send */}
              <div className="space-y-1.5 max-w-sm">
                <label className="text-xs font-black text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-muted-foreground" />
                  Schedule Broadcast Send (Optional)
                </label>
                <input
                  type="datetime-local"
                  value={composerSchedule}
                  onChange={(e) => setComposerSchedule(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg text-xs font-bold text-foreground outline-none"
                />
              </div>

              {/* Dynamic Sections Based on Mode selection */}
              {composerMode !== "SMS" && (
                <div className="space-y-4 p-4 border border-border bg-indigo-50/10 rounded-2xl space-y-3">
                  <h4 className="text-xs font-black text-indigo-500 uppercase tracking-widest flex items-center gap-1.5">
                    <Mail className="w-4 h-4" /> Email Dispatch Body
                  </h4>
                  
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-muted-foreground">Subject Line</label>
                    <input
                      type="text"
                      placeholder="Enter email subject line..."
                      value={composerSubject}
                      onChange={(e) => setComposerSubject(e.target.value)}
                      className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-xs font-semibold focus:ring-2 focus:ring-primary/20 outline-none"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-muted-foreground">Email Rich Text Content</label>
                      <div className="flex gap-1.5 bg-secondary/50 p-1 rounded-lg border border-border">
                        <button type="button" onClick={() => applyTextFormat("bold")} className="p-1 hover:bg-background rounded text-xs font-bold" title="Bold"><Bold size={12} /></button>
                        <button type="button" onClick={() => applyTextFormat("italic")} className="p-1 hover:bg-background rounded text-xs font-bold" title="Italic"><Italic size={12} /></button>
                        <button type="button" onClick={() => applyTextFormat("list")} className="p-1 hover:bg-background rounded text-xs font-bold" title="Bullet List"><ListIcon size={12} /></button>
                        <button type="button" onClick={() => applyTextFormat("code")} className="p-1 hover:bg-background rounded text-xs font-bold" title="Code"><Code size={12} /></button>
                      </div>
                    </div>
                    <textarea
                      rows={5}
                      placeholder="HTML or custom rich text announcement body..."
                      value={composerContent}
                      onChange={(e) => setComposerContent(e.target.value)}
                      className="w-full px-4 py-3 bg-background border border-border rounded-lg text-xs font-semibold font-mono focus:ring-2 focus:ring-primary/20 outline-none resize-none"
                    />
                  </div>

                  {/* Attachment Zone */}
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-muted-foreground">Attachments (Max 5MB)</label>
                    
                    {/* Drag and drop panel */}
                    <div
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                      onClick={triggerFileInput}
                      className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all ${
                        isDragging ? "border-primary bg-primary/5" : "border-border hover:bg-secondary/20"
                      }`}
                    >
                      <input 
                        type="file" 
                        ref={fileInputRef} 
                        onChange={handleFileChange} 
                        multiple 
                        className="hidden" 
                      />
                      <Upload className="w-6 h-6 text-muted-foreground mx-auto mb-2 animate-bounce" />
                      <p className="text-xs font-bold text-foreground">Drag & Drop files here, or click to upload</p>
                      <p className="text-[10px] text-muted-foreground mt-1">Supported: PDF, Excel, Word, PPT, TXT, Images</p>
                    </div>

                    {/* Attachment list */}
                    {composerAttachments.length > 0 && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
                        {composerAttachments.map((file, idx) => (
                          <div key={idx} className="flex items-center justify-between p-2 bg-background border border-border rounded-lg text-xs">
                            <div className="flex items-center gap-2">
                              <Paperclip className="w-3.5 h-3.5 text-indigo-500" />
                              <span className="font-semibold truncate max-w-[150px]">{file.name}</span>
                              <span className="text-[9px] text-muted-foreground uppercase font-bold">({file.type})</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-[9px] font-bold text-muted-foreground">{file.size}</span>
                              <button
                                type="button"
                                onClick={() => removeAttachment(idx)}
                                className="p-1 hover:bg-rose-50 text-rose-500 rounded transition-colors"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {composerMode !== "Email" && (
                <div className="space-y-3 p-4 border border-border bg-teal-50/10 rounded-2xl">
                  <h4 className="text-xs font-black text-teal-600 uppercase tracking-widest flex items-center gap-1.5">
                    <MessageSquare className="w-4 h-4" /> SMS Message body
                  </h4>
                  
                  <textarea
                    rows={3}
                    placeholder="Enter short text message..."
                    value={composerSms}
                    onChange={(e) => setComposerSms(e.target.value)}
                    maxLength={320}
                    className="w-full px-4 py-3 bg-background border border-border rounded-lg text-xs font-semibold focus:ring-2 focus:ring-primary/20 outline-none resize-none font-mono"
                  />
                  <div className="flex items-center justify-between text-[10px] text-muted-foreground font-bold">
                    <span>Character Count: {composerSms.length} / 320</span>
                    <span>SMS segments: {Math.ceil(composerSms.length / 160) || 1} ({Math.ceil(composerSms.length / 160) * 160} chars limit)</span>
                  </div>
                </div>
              )}

              {/* Dynamic Estimated Reach Alert */}
              <div className="p-3 bg-indigo-50 border border-indigo-100 rounded-xl flex items-center gap-2 text-indigo-800 text-xs font-semibold">
                <Check className="w-4 h-4 text-indigo-600" />
                Estimated Reach: <strong className="text-indigo-900 font-extrabold">{calculateReach(composerFilters)} Employees</strong> target matches found.
              </div>
            </div>

            <div className="p-4 border-t border-border bg-muted/20 flex items-center justify-between">
              <button 
                type="button" 
                onClick={resetComposer}
                className="px-4 py-2 border border-border text-xs font-bold rounded-lg hover:bg-secondary transition-colors"
              >
                Cancel
              </button>
              
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleComposeSubmit("Draft")}
                  className="px-4 py-2 bg-secondary text-foreground text-xs font-bold rounded-lg hover:bg-secondary/80 transition-colors"
                >
                  Save Draft
                </button>
                <button
                  type="button"
                  onClick={() => handleComposeSubmit(composerSchedule ? "Scheduled" : "Sent")}
                  className="px-5 py-2 bg-primary text-primary-foreground text-xs font-bold rounded-lg hover:opacity-90 transition-all flex items-center gap-1.5 shadow shadow-primary/20"
                >
                  <Send className="w-3.5 h-3.5" />
                  {composerSchedule ? "Schedule dispatch" : "Send broadcast"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
