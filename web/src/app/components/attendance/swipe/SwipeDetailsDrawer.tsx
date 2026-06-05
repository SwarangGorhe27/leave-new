import { 
  X, 
  MapPin, 
  ShieldCheck, 
  Clock, 
  Cpu, 
  ArrowRightLeft, 
  User,
  History,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Map as MapIcon,
  Fingerprint
} from "lucide-react";
import { Button } from "../../ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "../../ui/avatar";
import { cn } from "../../ui/utils";
import { SwipeLog } from "../../../modules/attendance/types";
import { Badge } from "../../ui/badge";

interface SwipeDetailsDrawerProps {
  swipe: SwipeLog | null;
  onClose: () => void;
}

export function SwipeDetailsDrawer({ swipe, onClose }: SwipeDetailsDrawerProps) {
  if (!swipe) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-slate-950/20 backdrop-blur-sm z-[100] transition-opacity"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed top-0 right-0 h-full w-[450px] bg-white dark:bg-slate-900 shadow-2xl z-[101] flex flex-col border-l border-slate-200 dark:border-slate-800 animate-in slide-in-from-right duration-300">
        {/* Header */}
        <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-800/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
              <History className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <h3 className="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest">Swipe Intelligence</h3>
              <p className="text-[10px] font-bold text-slate-500 tracking-tight">LOG ID: {swipe.id}</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="rounded-xl hover:bg-red-50 hover:text-red-500 transition-all">
            <X className="w-5 h-5" />
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto no-scrollbar p-6 space-y-8">
          {/* Employee Profile Card */}
          <div className="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-5 border border-slate-100 dark:border-slate-800 space-y-4">
            <div className="flex items-center gap-4">
              <Avatar className="h-16 w-16 border-4 border-white dark:border-slate-800 shadow-lg">
                <AvatarImage src={swipe.avatar} />
                <AvatarFallback className="text-xl font-black">
                  {swipe.employeeName.split(' ').map(n => n[0]).join('')}
                </AvatarFallback>
              </Avatar>
              <div className="space-y-1">
                <h4 className="text-lg font-bold text-slate-900 dark:text-slate-100">{swipe.employeeName}</h4>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-[10px] font-black tracking-widest bg-white dark:bg-slate-900">{swipe.employeeCode}</Badge>
                  <span className="text-[10px] font-bold text-slate-400 uppercase">{swipe.department}</span>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200 dark:border-slate-700">
              <div className="space-y-1">
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">Designation</p>
                <p className="text-xs font-bold text-slate-700 dark:text-slate-300">{swipe.designation}</p>
              </div>
              <div className="space-y-1">
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">Current Shift</p>
                <p className="text-xs font-bold text-slate-700 dark:text-slate-300">{swipe.shiftName}</p>
              </div>
            </div>
          </div>

          {/* Swipe Mechanics */}
          <div className="space-y-4">
            <h5 className="text-[11px] font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest flex items-center gap-2">
              <ArrowRightLeft className="w-3.5 h-3.5 text-emerald-500" /> Swipe Details
            </h5>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm space-y-2">
                <p className="text-[9px] font-bold text-slate-400 uppercase">Timestamp</p>
                <p className="text-xl font-black text-slate-900 dark:text-slate-100">{swipe.swipeTime}</p>
                <p className="text-[10px] font-bold text-slate-500">{swipe.swipeDate}</p>
              </div>
              <div className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm space-y-2">
                <p className="text-[9px] font-bold text-slate-400 uppercase">Direction</p>
                <div className={cn(
                  "inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-black uppercase",
                  swipe.type === "IN" ? "bg-emerald-50 text-emerald-600" : "bg-purple-50 text-purple-600"
                )}>
                  {swipe.type} Entry
                </div>
              </div>
            </div>
          </div>

          {/* Intelligence & Verification */}
          <div className="space-y-4">
            <h5 className="text-[11px] font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest flex items-center gap-2">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-500" /> Security Intelligence
            </h5>
            <div className="bg-slate-900 text-white rounded-2xl p-5 space-y-5 relative overflow-hidden group">
              <div className="flex items-center justify-between relative z-10">
                <div className="space-y-1">
                  <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Verification Method</p>
                  <div className="flex items-center gap-2">
                    <Fingerprint className="w-5 h-5 text-emerald-400" />
                    <span className="text-sm font-bold">{swipe.verificationMethod} Scan</span>
                  </div>
                </div>
                {swipe.faceMatchScore && (
                  <div className="text-right">
                    <p className="text-[10px] font-bold text-slate-400 uppercase">Match Score</p>
                    <p className="text-lg font-black text-emerald-400">{swipe.faceMatchScore}%</p>
                  </div>
                )}
              </div>
              
              <div className="p-3 bg-white/5 rounded-xl border border-white/10 flex items-center gap-3 relative z-10">
                <div className={cn(
                  "w-2 h-2 rounded-full animate-pulse",
                  swipe.spoofDetection === "Safe" ? "bg-emerald-500" : "bg-red-500"
                )} />
                <span className="text-[11px] font-bold uppercase tracking-widest">Spoof Detection: {swipe.spoofDetection}</span>
              </div>

              <ShieldCheck className="absolute -bottom-4 -right-4 w-24 h-24 text-white/5 -rotate-12 group-hover:rotate-0 transition-transform duration-500" />
            </div>
          </div>

          {/* Device & Location */}
          <div className="space-y-4">
            <h5 className="text-[11px] font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest flex items-center gap-2">
              <MapPin className="w-3.5 h-3.5 text-rose-500" /> Access Point
            </h5>
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 space-y-5">
              <div className="flex items-start gap-3">
                <div className="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-500">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-900 dark:text-slate-100">{swipe.deviceName}</p>
                  <p className="text-[10px] font-bold text-slate-500">SN: {swipe.deviceId} • IP: {swipe.ipAddress}</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center gap-3 text-xs">
                  <MapPin className="w-4 h-4 text-slate-400" />
                  <span className="font-medium text-slate-600 dark:text-slate-400">{swipe.branch} • {swipe.doorName}</span>
                </div>
                <div className="h-32 bg-slate-100 dark:bg-slate-800 rounded-xl relative overflow-hidden border border-slate-200 dark:border-slate-700 group cursor-pointer">
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40 z-10">
                    <Button variant="secondary" size="sm" className="h-7 text-[10px] font-black gap-2">
                      <MapIcon className="w-3 h-3" /> VIEW ON MAP
                    </Button>
                  </div>
                  <img 
                    src="https://api.mapbox.com/styles/v1/mapbox/light-v10/static/72.8777,19.0760,14/400x128@2x?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZzeGgifQ.p_X1e1AfExS9SNoI07xkw" 
                    alt="Map Preview"
                    className="w-full h-full object-cover grayscale opacity-50"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-slate-100 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-800/50 backdrop-blur-sm">
          <Button variant="ghost" className="w-full h-11 rounded-xl text-slate-500 font-bold text-xs gap-2 hover:bg-slate-200/50">
            <AlertTriangle className="w-4 h-4 text-amber-500" /> REPORT SUSPICIOUS ACTIVITY
          </Button>
        </div>
      </div>
    </>
  );
}
