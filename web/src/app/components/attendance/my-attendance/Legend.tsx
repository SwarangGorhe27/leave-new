export function Legend() {
  const items = [
    { label: "Present", color: "#10B981", bgColor: "bg-emerald-500" },
    { label: "Absent", color: "#EF4444", bgColor: "bg-red-500" },
    { label: "Half Day", color: "#F97316", bgColor: "bg-orange-500" },
    { label: "Leave", color: "#9ca3af", bgColor: "bg-blue-500" },
    { label: "Holiday", color: "#a6ff00", bgColor: "bg-blue-500" },
    { label: "Week Off", color: "#9CA3AF", bgColor: "bg-gray-400" },
    { label: "Late In", color: "#FACC15", bgColor: "bg-yellow-400" },
    // { label: "Regularization", color: "#EAB308", bgColor: "bg-yellow-500" },
    // { label: "Pending", color: "#8B5CF6", bgColor: "bg-purple-500" },
  ];

  return (
    <div className="attendance-legend flex flex-wrap items-center justify-center gap-6 p-5">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2">
          <div
            className="attendance-status-dot w-2.5 h-2.5 rounded-full shadow-sm border border-black/10 dark:border-white/10"
            style={{ backgroundColor: item.color }}
          />
          <span className="text-[10px] font-semibold text-muted-foreground dark:text-muted-foreground uppercase tracking-widest">
            {item.label}
          </span>
        </div>
      ))}
    </div>
  );
}