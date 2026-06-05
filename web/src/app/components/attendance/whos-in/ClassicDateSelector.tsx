import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, RefreshCw } from "lucide-react";
import { format, addDays, subDays, isToday, isAfter, startOfDay } from "date-fns";
import { Button } from "../../ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "../../ui/popover";
import { Calendar } from "../../ui/calendar";
import { cn } from "../../ui/utils";

interface ClassicDateSelectorProps {
  selectedDate: Date;
  onDateChange: (date: Date) => void;
  onRefresh: () => void;
}

export function ClassicDateSelector({ selectedDate, onDateChange, onRefresh }: ClassicDateSelectorProps) {
  const isSelectedToday = isToday(selectedDate);
  const isFuture = isAfter(startOfDay(selectedDate), startOfDay(new Date()));

  return (
    <div className="flex flex-wrap items-center gap-3 bg-card p-3 rounded-xl border border-border shadow-sm">
      {/* Date Picker Field */}
      <div className="flex flex-col gap-1.5">
        <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider px-1">Select Date</label>
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={cn(
                "w-[220px] justify-between text-left font-semibold h-10 px-3 rounded-lg border-border bg-secondary/20 hover:bg-secondary/30 transition-all",
                !selectedDate && "text-muted-foreground"
              )}
            >
              <span className="text-sm">{format(selectedDate, "dd MMM yyyy")}</span>
              <CalendarIcon className="h-4 w-4 text-muted-foreground" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <Calendar
              mode="single"
              selected={selectedDate}
              onSelect={(d) => d && onDateChange(d)}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-end h-full pt-5">
        <div className="flex items-center bg-secondary/20 rounded-lg p-1 border border-border">
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-8 w-8 rounded-md hover:bg-card"
            onClick={() => onDateChange(subDays(selectedDate, 1))}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          
          <div className="h-4 w-px bg-border mx-1" />
          
          <Button 
            variant="ghost" 
            className={cn(
              "h-8 px-4 text-xs font-bold rounded-md hover:bg-card",
              isSelectedToday && "text-primary bg-card shadow-sm"
            )}
            onClick={() => onDateChange(new Date())}
          >
            Today
          </Button>

          <div className="h-4 w-px bg-border mx-1" />

          <Button 
            variant="ghost" 
            size="icon" 
            className="h-8 w-8 rounded-md hover:bg-card"
            onClick={() => onDateChange(addDays(selectedDate, 1))}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Status & Actions */}
      <div className="flex items-end h-full pt-5 ml-2 gap-3">
        {isSelectedToday && (
          <div className="flex items-center gap-2 px-3 h-10 rounded-lg bg-green-500/10 border border-green-500/20">
            <div className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </div>
            <span className="text-[10px] font-bold text-green-600 uppercase tracking-tight">Live Monitoring</span>
          </div>
        )}

        {isFuture && (
          <div className="flex items-center gap-2 px-3 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <CalendarIcon className="w-3.5 h-3.5 text-blue-500" />
            <span className="text-[10px] font-bold text-blue-600 uppercase tracking-tight">Future Schedule</span>
          </div>
        )}

        <Button 
          variant="outline" 
          size="sm" 
          className="h-10 gap-2 font-bold text-xs px-4 rounded-lg border-border"
          onClick={onRefresh}
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </Button>
      </div>
    </div>
  );
}
