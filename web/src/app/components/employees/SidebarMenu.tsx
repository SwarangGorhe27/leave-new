import {
  User,
  CreditCard,
  Users,
  Globe,
  Briefcase,
  Building2,
  LogOut,
  Key,
  FileText,
  IndianRupee,
  GraduationCap,
  ShieldCheck,
  Monitor,
} from "lucide-react";

export type SidebarSection =
  | "profile"
  | "education"
  | "family"
  | "nominee"
  | "insurance"
  | "work"
  | "position"
  | "bank"
  | "passport"
  | "background"
  | "assets"
  | "access"
  | "documents"
  | "salary";

interface MenuItem {
  id: SidebarSection;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const menuItems: MenuItem[] = [
  { id: "profile", label: "Employee Profile", icon: User },
  { id: "education", label: "Education Details", icon: GraduationCap },
  { id: "family", label: "Family Details", icon: Users },
  { id: "nominee", label: "Nominee Details", icon: Users },
  { id: "insurance", label: "Insurance Details", icon: ShieldCheck },
  { id: "work", label: "Work Experience", icon: Building2 },
  { id: "position", label: "Position History", icon: Briefcase },
  { id: "bank", label: "Bank / PF / ESI", icon: CreditCard },
  { id: "passport", label: "Passport & Visa", icon: Globe },
  { id: "background", label: "Background Check", icon: ShieldCheck },
  { id: "assets", label: "Asset Management", icon: Monitor },
  { id: "access", label: "Access Card Details", icon: Key },
  { id: "documents", label: "Employee Documents", icon: FileText },
  { id: "salary", label: "Employee Salary", icon: IndianRupee },
];

interface SidebarMenuProps {
  activeSection: SidebarSection;
  onSectionChange: (section: SidebarSection) => void;
}

export function SidebarMenu({ activeSection, onSectionChange }: SidebarMenuProps) {
  return (
    <aside className="w-60 min-w-[240px] bg-card border-r border-border flex flex-col overflow-y-auto flex-shrink-0">
      <div className="py-5 px-3">
        <p className="px-3 pb-3 text-[10px] uppercase tracking-widest text-muted-foreground font-semibold">
          Employee Sections
        </p>
        <nav className="space-y-0.5">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSectionChange(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 text-left rounded-lg relative
                  transition-all duration-150 text-sm font-medium
                  ${
                    isActive
                      ? "bg-secondary text-foreground font-semibold"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                  }`}
              >
                {isActive && (
                  <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-foreground rounded-r-full" />
                )}
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">{item.label}</span>
                {isActive && (
                  <span className="ml-auto w-1.5 h-1.5 rounded-full bg-foreground flex-shrink-0" />
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
