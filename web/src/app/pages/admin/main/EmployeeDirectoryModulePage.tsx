import React from "react";
import { Box, Settings, Puzzle, ShieldCheck } from "lucide-react";

export function EmployeeDirectoryModulePage() {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center animate-in fade-in duration-700">
      <div className="w-20 h-20 rounded-[2.5rem] bg-indigo-500/10 flex items-center justify-center text-indigo-500 mb-6 shadow-2xl shadow-indigo-500/10">
        <Box size={40} />
      </div>
      <h2 className="text-2xl font-black text-foreground tracking-tight">Employee Directory Module</h2>
      <p className="text-muted-foreground mt-2 max-w-md font-medium"> Configure advanced directory settings, custom views, and access permissions for the organization directory.</p>
      
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-12 w-full max-w-3xl">
        {[
          { label: "Directory Setup", desc: "Configure fields and visibility", icon: Settings },
          { label: "Integrations", desc: "Sync with Active Directory/Slack", icon: Puzzle },
          { label: "Access Control", desc: "Role-based visibility rules", icon: ShieldCheck },
        ].map((m, i) => (
          <div key={i} className="flat-card p-6 border border-border bg-card hover:border-indigo-500/50 transition-all cursor-pointer group">
            <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center mx-auto mb-4 group-hover:bg-indigo-500 group-hover:text-white transition-colors">
              <m.icon size={20} />
            </div>
            <h4 className="text-sm font-black text-foreground">{m.label}</h4>
            <p className="text-xs text-muted-foreground mt-1">{m.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
