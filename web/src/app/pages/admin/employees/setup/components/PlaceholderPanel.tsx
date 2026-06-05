import { User, Building2, Wallet, MapPin, Search, ChevronRight } from "lucide-react";
import { useState } from "react";

const PLACEHOLDERS = [
  {
    category: "Employee",
    icon: User,
    color: "text-blue-500",
    bg: "bg-blue-500/10",
    items: [
      { label: "Employee Name", value: "{{employee_name}}" },
      { label: "Employee Number", value: "{{employee_number}}" },
      { label: "Designation", value: "{{designation}}" },
      { label: "Department", value: "{{department}}" },
      { label: "Joining Date", value: "{{joining_date}}" },
    ]
  },
  {
    category: "Company",
    icon: Building2,
    color: "text-emerald-500",
    bg: "bg-emerald-500/10",
    items: [
      { label: "Company Name", value: "{{company_name}}" },
      { label: "Company Address", value: "{{company_address}}" },
      { label: "HR Manager Name", value: "{{hr_name}}" },
    ]
  },
  {
    category: "Payroll",
    icon: Wallet,
    color: "text-amber-500",
    bg: "bg-amber-500/10",
    items: [
      { label: "Monthly Gross", value: "{{salary}}" },
      { label: "Annual CTC", value: "{{annual_ctc}}" },
      { label: "Bonus Amount", value: "{{bonus}}" },
      { label: "PF Contribution", value: "{{pf_amount}}" },
    ]
  },
  {
    category: "Address",
    icon: MapPin,
    color: "text-purple-500",
    bg: "bg-purple-500/10",
    items: [
      { label: "City", value: "{{city}}" },
      { label: "State", value: "{{state}}" },
      { label: "Postal Code", value: "{{pincode}}" },
    ]
  }
];

export function PlaceholderPanel() {
  const [search, setSearch] = useState("");

  const copyToClipboard = (val: string) => {
    navigator.clipboard.writeText(val);
    // You could add a toast here
  };

  const filtered = PLACEHOLDERS.map(cat => ({
    ...cat,
    items: cat.items.filter(item => 
      item.label.toLowerCase().includes(search.toLowerCase()) || 
      item.value.toLowerCase().includes(search.toLowerCase())
    )
  })).filter(cat => cat.items.length > 0);

  return (
    <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-xl flex flex-col h-full animate-in fade-in slide-in-from-left-4 duration-500">
      <div className="p-4 bg-secondary/20 border-b border-border space-y-3">
        <div className="flex items-center justify-between">
           <h3 className="text-[10px] font-black text-foreground uppercase tracking-[0.2em]">Available Placeholders</h3>
           <span className="text-[9px] font-bold text-primary uppercase">Click to Copy</span>
        </div>
        <div className="relative">
           <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
           <input 
            type="text" 
            placeholder="Search variables..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 bg-background border border-border rounded-lg text-[10px] font-bold focus:ring-1 focus:ring-primary outline-none transition-all"
           />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6 no-scrollbar">
        {filtered.map(cat => (
          <div key={cat.category} className="space-y-3">
            <div className="flex items-center gap-2">
               <div className={`w-6 h-6 rounded-lg ${cat.bg} ${cat.color} flex items-center justify-center`}>
                  <cat.icon size={12} />
               </div>
               <span className="text-[10px] font-black text-foreground uppercase tracking-widest">{cat.category}</span>
            </div>
            <div className="space-y-1.5 pl-8">
               {cat.items.map(item => (
                 <button 
                  key={item.value}
                  onClick={() => copyToClipboard(item.value)}
                  className="w-full flex items-center justify-between group hover:bg-secondary/50 p-1.5 rounded-lg transition-all text-left"
                 >
                    <div className="space-y-0.5">
                       <p className="text-[10px] font-bold text-foreground truncate">{item.label}</p>
                       <code className="text-[9px] text-primary font-bold opacity-70">{item.value}</code>
                    </div>
                    <ChevronRight size={10} className="text-muted-foreground opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0" />
                 </button>
               ))}
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <div className="py-12 text-center">
             <p className="text-[10px] font-bold text-muted-foreground uppercase">No matches found</p>
          </div>
        )}
      </div>

      <div className="p-4 bg-primary/5 border-t border-primary/10">
         <p className="text-[9px] text-primary/80 font-bold leading-relaxed">
            PRO TIP: You can use these placeholders in the Word template file or custom field descriptions.
         </p>
      </div>
    </div>
  );
}
