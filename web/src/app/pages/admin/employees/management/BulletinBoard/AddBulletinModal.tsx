import React, { useState, useRef, useMemo } from "react";
import { 
  X, 
  Plus, 
  Calendar, 
  Hash, 
  FileText, 
  Paperclip, 
  Users, 
  Save, 
  Eye, 
  EyeOff,
  Trash2,
  AlertCircle,
  FileIcon,
  Search,
  ChevronDown,
  Info
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "../../../../../components/ui/utils";
import { Button } from "../../../../../components/ui/button";
import { Input } from "../../../../../components/ui/input";
import { Textarea } from "../../../../../components/ui/textarea";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle 
} from "../../../../../components/ui/dialog";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "../../../../../components/ui/select";
import { Badge } from "../../../../../components/ui/badge";
import { Checkbox } from "../../../../../components/ui/checkbox";
import { BULLETIN_CATEGORIES, EMPLOYEE_FILTERS, SUPPORTED_FILE_EXTENSIONS } from "./BulletinBoardConfig";
import { Bulletin, BulletinAttachment } from "./types";

interface AddBulletinModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (bulletin: Partial<Bulletin>) => void;
  editData?: Bulletin | null;
}

export function AddBulletinModal({ isOpen, onClose, onSave, editData }: AddBulletinModalProps) {
  const [formData, setFormData] = useState<Partial<Bulletin>>(
    editData || {
      category: "",
      title: "",
      content: "",
      startDate: new Date().toISOString().split("T")[0],
      expiryDate: "",
      rank: 1,
      isHidden: false,
      attachments: [],
      employeeFilters: [],
      status: "Open"
    }
  );

  const [errors, setErrors] = useState<Record<string, string>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.category) newErrors.category = "Category is required";
    if (!formData.title) newErrors.title = "Title is required";
    if (!formData.content) newErrors.content = "Content is required";
    if (!formData.startDate) newErrors.startDate = "Start date is required";
    if (!formData.expiryDate) newErrors.expiryDate = "Expiry date is required";
    if (formData.startDate && formData.expiryDate && formData.expiryDate < formData.startDate) {
      newErrors.expiryDate = "Expiry date cannot be before start date";
    }
    if (formData.rank === undefined || isNaN(formData.rank)) newErrors.rank = "Rank must be a number";
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (validate()) {
      onSave(formData);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    const newAttachments: BulletinAttachment[] = Array.from(files).map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      type: file.type,
      url: URL.createObjectURL(file)
    }));

    setFormData(prev => ({
      ...prev,
      attachments: [...(prev.attachments || []), ...newAttachments]
    }));
  };

  const removeAttachment = (id: string) => {
    setFormData(prev => ({
      ...prev,
      attachments: prev.attachments?.filter(a => a.id !== id)
    }));
  };

  const addEmployeeFilter = (filterId: string) => {
    if (!formData.employeeFilters?.includes(filterId)) {
      setFormData(prev => ({
        ...prev,
        employeeFilters: [...(prev.employeeFilters || []), filterId]
      }));
    }
  };

  const removeEmployeeFilter = (filterId: string) => {
    setFormData(prev => ({
      ...prev,
      employeeFilters: prev.employeeFilters?.filter(f => f !== filterId)
    }));
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-4xl p-0 overflow-hidden bg-card border-border rounded-[2.5rem] gap-0 shadow-2xl">
        <DialogHeader className="px-10 py-8 border-b border-border bg-secondary/20">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-primary/10 rounded-2xl flex items-center justify-center">
              <Plus className="w-6 h-6 text-primary" />
            </div>
            <div>
              <DialogTitle className="text-2xl font-black text-foreground uppercase tracking-tight">
                {editData ? "Edit Bulletin" : "Create New Bulletin"}
              </DialogTitle>
              <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest opacity-60">
                Post announcements and notifications to employees
              </p>
            </div>
          </div>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto max-h-[70vh] p-10">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Left Column */}
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Bulletin Title *</label>
                <div className="relative">
                  <FileText className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground opacity-50" />
                  <Input 
                    placeholder="Enter bulletin title..." 
                    className={cn("pl-11 h-14 bg-secondary/30 rounded-2xl border-border/50", errors.title && "border-rose-500")}
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                  />
                </div>
                {errors.title && <p className="text-[10px] font-bold text-rose-500 uppercase">{errors.title}</p>}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Category *</label>
                  <Select value={formData.category} onValueChange={(v) => setFormData({...formData, category: v})}>
                    <SelectTrigger className={cn("h-14 bg-secondary/30 rounded-2xl border-border/50", errors.category && "border-rose-500")}>
                      <SelectValue placeholder="Select Category" />
                    </SelectTrigger>
                    <SelectContent>
                      {BULLETIN_CATEGORIES.map(cat => (
                        <SelectItem key={cat.id} value={cat.id}>{cat.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.category && <p className="text-[10px] font-bold text-rose-500 uppercase">{errors.category}</p>}
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Display Rank *</label>
                  <div className="relative">
                    <Hash className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground opacity-50" />
                    <Input 
                      type="number"
                      placeholder="e.g. 1" 
                      className={cn("pl-11 h-14 bg-secondary/30 rounded-2xl border-border/50", errors.rank && "border-rose-500")}
                      value={formData.rank}
                      onChange={(e) => setFormData({...formData, rank: parseInt(e.target.value)})}
                    />
                  </div>
                  {errors.rank && <p className="text-[10px] font-bold text-rose-500 uppercase">{errors.rank}</p>}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Start Date *</label>
                  <div className="relative">
                    <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground opacity-50" />
                    <Input 
                      type="date" 
                      className={cn("pl-11 h-14 bg-secondary/30 rounded-2xl border-border/50", errors.startDate && "border-rose-500")}
                      value={formData.startDate}
                      onChange={(e) => setFormData({...formData, startDate: e.target.value})}
                    />
                  </div>
                  {errors.startDate && <p className="text-[10px] font-bold text-rose-500 uppercase">{errors.startDate}</p>}
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Expiry Date *</label>
                  <div className="relative">
                    <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground opacity-50" />
                    <Input 
                      type="date" 
                      className={cn("pl-11 h-14 bg-secondary/30 rounded-2xl border-border/50", errors.expiryDate && "border-rose-500")}
                      value={formData.expiryDate}
                      onChange={(e) => setFormData({...formData, expiryDate: e.target.value})}
                    />
                  </div>
                  {errors.expiryDate && <p className="text-[10px] font-bold text-rose-500 uppercase">{errors.expiryDate}</p>}
                </div>
              </div>

              <div className="flex items-center gap-3 p-4 bg-secondary/20 rounded-2xl border border-border/50">
                <Checkbox 
                  id="hide-bulletin" 
                  checked={formData.isHidden} 
                  onCheckedChange={(checked) => setFormData({...formData, isHidden: !!checked})} 
                />
                <label htmlFor="hide-bulletin" className="flex items-center gap-2 text-xs font-black text-foreground uppercase cursor-pointer">
                  {formData.isHidden ? <EyeOff className="w-4 h-4 text-rose-500" /> : <Eye className="w-4 h-4 text-emerald-500" />}
                  Hide Bulletin Immediately
                </label>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Target Audience (Filters)</label>
                  <Button variant="ghost" size="sm" className="h-6 text-[9px] font-black uppercase text-primary">
                    <Plus className="w-3 h-3 mr-1" />
                    Add Filter
                  </Button>
                </div>
                <Select onValueChange={addEmployeeFilter}>
                  <SelectTrigger className="h-12 bg-secondary/30 rounded-2xl border-border/50">
                    <SelectValue placeholder="Add Target Group..." />
                  </SelectTrigger>
                  <SelectContent>
                    {EMPLOYEE_FILTERS.map(f => (
                      <SelectItem key={f.id} value={f.id} disabled={formData.employeeFilters?.includes(f.id)}>
                        {f.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <div className="flex flex-wrap gap-2 pt-1">
                  {formData.employeeFilters?.map(fId => {
                    const filter = EMPLOYEE_FILTERS.find(f => f.id === fId);
                    return (
                      <Badge key={fId} className="bg-primary/10 text-primary border-none rounded-lg px-3 py-1 flex items-center gap-2 group">
                        <span className="text-[9px] font-black uppercase">{filter?.label}</span>
                        <X className="w-3 h-3 cursor-pointer hover:text-rose-500" onClick={() => removeEmployeeFilter(fId)} />
                      </Badge>
                    );
                  })}
                  {(!formData.employeeFilters || formData.employeeFilters.length === 0) && (
                    <p className="text-[10px] font-bold text-muted-foreground italic px-1">All employees will see this by default.</p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Attachments</label>
                  <p className="text-[9px] font-bold text-muted-foreground uppercase opacity-50">Supported: PDF, XLSX, DOC, etc.</p>
                </div>
                <div 
                  className="border-2 border-dashed border-border rounded-2xl p-6 bg-secondary/10 flex flex-col items-center justify-center gap-3 cursor-pointer hover:bg-primary/5 transition-all"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Paperclip className="w-6 h-6 text-primary" />
                  <p className="text-[10px] font-black text-muted-foreground uppercase">Click or Drag & Drop</p>
                  <input type="file" multiple className="hidden" ref={fileInputRef} onChange={handleFileSelect} />
                </div>
                <div className="space-y-2">
                  {formData.attachments?.map(file => (
                    <div key={file.id} className="flex items-center justify-between p-3 bg-card border border-border rounded-xl shadow-sm">
                      <div className="flex items-center gap-3 overflow-hidden">
                        <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center shrink-0">
                          <FileIcon className="w-4 h-4 text-primary" />
                        </div>
                        <div className="overflow-hidden">
                          <p className="text-[11px] font-black text-foreground truncate">{file.name}</p>
                          <p className="text-[9px] font-bold text-muted-foreground uppercase">{(file.size / 1024).toFixed(1)} KB</p>
                        </div>
                      </div>
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-rose-500" onClick={() => removeAttachment(file.id)}>
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 space-y-2">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Bulletin Content (Rich Text Editor) *</label>
            <div className="bg-secondary/30 rounded-[2rem] border border-border/50 p-6">
               <Textarea 
                placeholder="Write your announcement content here..." 
                className="min-h-[200px] bg-transparent border-none focus-visible:ring-0 text-sm font-medium leading-relaxed resize-none p-0"
                value={formData.content}
                onChange={(e) => setFormData({...formData, content: e.target.value})}
               />
               <div className="flex items-center gap-4 mt-4 pt-4 border-t border-border/30">
                 <div className="flex items-center gap-1">
                    {[1, 2, 3].map(i => <div key={i} className="w-6 h-6 rounded bg-background border border-border flex items-center justify-center text-[10px] font-black cursor-pointer hover:bg-primary hover:text-white transition-colors">B</div>)}
                 </div>
                 <div className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest ml-auto flex items-center gap-2">
                    <Info className="w-3 h-3" />
                    Markdown supported for rich formatting
                 </div>
               </div>
            </div>
            {errors.content && <p className="text-[10px] font-bold text-rose-500 uppercase">{errors.content}</p>}
          </div>
        </div>

        <div className="px-10 py-8 border-t border-border bg-secondary/10 flex items-center justify-end gap-4">
          <Button variant="ghost" onClick={onClose} className="h-12 px-8 rounded-2xl text-xs font-black uppercase tracking-widest text-muted-foreground">
            Close
          </Button>
          <Button 
            onClick={handleSave} 
            className="h-12 px-10 rounded-2xl bg-primary text-white hover:opacity-90 text-xs font-black uppercase tracking-widest shadow-xl shadow-primary/20"
          >
            <Save className="w-4 h-4 mr-2" />
            {editData ? "Update Bulletin" : "Save Bulletin"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
