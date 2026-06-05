import { format } from "date-fns";
import { 
  Calendar as CalendarIcon, 
  List, 
  ClipboardCheck,
  History,
  ChevronLeft, 
  ChevronRight, 
  Search,
} from "lucide-react";

interface FiltersProps {
  view: "calendar" | "list" | "regularization" | "regularization-history";
  onViewChange: (view: "calendar" | "list" | "regularization" | "regularization-history") => void;
  currentDate: Date;
  onDateChange: (date: Date) => void;
  searchTerm: string;
  onSearchChange: (term: string) => void;
}

export function Filters({ 
  view, 
  onViewChange, 
  currentDate, 
  onDateChange, 
  searchTerm, 
  onSearchChange,
}: FiltersProps) {
  
  const handlePrevMonth = () => {
    onDateChange(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    onDateChange(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const handleToday = () => {
    onDateChange(new Date());
  };

  return (
    <div className="attendance-filterbar flex flex-col md:flex-row items-center justify-between gap-4 p-3">
      <div className="flex items-center gap-3">
        {/* View Switcher */}
        <div className="attendance-segment flex p-1">
          {[
            { id: "calendar", icon: CalendarIcon, label: "Calendar" },
            { id: "list", icon: List, label: "List" },
            { id: "regularization", icon: ClipboardCheck, label: "Regularization" },
            { id: "regularization-history", icon: History, label: "History" },
          ].map((v) => (
            <button
              key={v.id}
              onClick={() => onViewChange(v.id as any)}
              className={`attendance-segment-button flex items-center gap-2 px-4 py-2 text-xs font-semibold transition-all ${
                view === v.id 
                  ? "is-active" 
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <v.icon size={14} />
              <span className="hidden sm:inline">{v.label}</span>
            </button>
          ))}
        </div>

        {/* Date Navigator */}
        {view !== "regularization" && view !== "regularization-history" && (
          <div className="attendance-month-nav flex items-center gap-2 p-1">
            <button 
              onClick={handlePrevMonth}
              className="attendance-nav-button p-2 transition-all"
            >
              <ChevronLeft size={16} />
            </button>
            <h3 className="text-sm font-semibold text-foreground min-w-[120px] text-center">
              {format(currentDate, "MMMM yyyy")}
            </h3>
            <button 
              onClick={handleNextMonth}
              className="attendance-nav-button p-2 transition-all"
            >
              <ChevronRight size={16} />
            </button>
            <div className="w-[1px] h-4 bg-foreground/10 mx-1" />
            <button 
              onClick={handleToday}
              className="attendance-today-button px-3 py-1.5 text-[10px] font-semibold transition-all uppercase tracking-widest"
            >
              Today
            </button>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3 w-full md:w-auto">
        {/* Search */}
        <div className="relative flex-1 md:flex-none">
          <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input 
            type="text" 
            placeholder={view === "regularization-history" ? "Search date, status, shift..." : "        Search date, status, shift..."}
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            className="attendance-search-input w-full md:w-64 pl-12 pr-4 py-3 text-xs font-medium"
          />
        </div>

        {/* AI Insights removed per request */}
      </div>
    </div>
  );
}
