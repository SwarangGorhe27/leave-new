import { 
  Wifi, 
  WifiOff, 
  Battery, 
  BatteryLow, 
  BatteryWarning, 
  MapPin, 
  MoreVertical,
  Activity,
  Settings,
  Power,
  Shield,
  RefreshCw

} from "lucide-react";
import { cn } from "../../ui/utils";
import { DeviceHealth } from "../../../modules/attendance/types";
import { Button } from "../../ui/button";
import { KebabMenu } from "../../ui/KebabMenu";
import { toast } from "sonner";

interface DeviceHealthMonitorProps {
  devices: DeviceHealth[];
  onManageDevices: () => void;
}

export function DeviceHealthMonitor({ devices, onManageDevices }: DeviceHealthMonitorProps) {
  const getBatteryIcon = (level: number) => {
    if (level === 0) return <BatteryLow className="w-3.5 h-3.5 text-red-500" />;
    if (level < 20) return <BatteryWarning className="w-3.5 h-3.5 text-amber-500" />;
    return <Battery className="w-3.5 h-3.5 text-emerald-500" />;
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm flex flex-col">
      <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-emerald-500" />
          <h4 className="text-[11px] font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest">Device Network</h4>
        </div>
        <button className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors">
          <RefreshCw className="w-3.5 h-3.5 text-slate-400" />
        </button>
      </div>

      <div className="p-2 space-y-1">
        {devices.map((device) => (
          <div 
            key={device.id} 
            className="p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-all group border border-transparent hover:border-slate-100 dark:hover:border-slate-800"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-3">
                <div className={cn(
                  "p-2 rounded-lg border",
                  device.status === "Online" 
                    ? "bg-emerald-50 text-emerald-600 border-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400" 
                    : "bg-red-50 text-red-600 border-red-100 dark:bg-red-500/10 dark:text-red-400"
                )}>
                  {device.status === "Online" ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
                </div>
                <div>
                  <h5 className="text-[11px] font-bold text-slate-900 dark:text-slate-100">{device.name}</h5>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <MapPin className="w-2.5 h-2.5 text-slate-400" />
                    <span className="text-[9px] font-medium text-slate-500 uppercase">{device.location}</span>
                  </div>
                </div>
              </div>
              <div onClick={(e) => e.stopPropagation()}>
                <KebabMenu 
                  size="sm"
                  items={[
                    { label: "Device Settings", icon: Settings, onClick: () => toast.info(`Settings for ${device.name}`) },
                    { label: "Update Firmware", icon: Shield, onClick: () => toast.loading("Checking for updates...") },
                    { label: "Reboot Device", icon: RefreshCw, onClick: () => toast.success("Reboot command sent") },
                    { label: "Power Off", icon: Power, variant: "destructive", separator: true, onClick: () => {
                      if (confirm("Shut down this biometric device?")) toast.error("Device powered off");
                    }},
                  ]}
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800/50">
              <div className="flex items-center gap-2">
                <span className={cn(
                  "w-1.5 h-1.5 rounded-full",
                  device.status === "Online" ? "bg-emerald-500 animate-pulse" : "bg-red-500"
                )} />
                <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">
                  {device.status === "Online" ? "Active Now" : "Disconnected"}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  {getBatteryIcon(device.batteryStatus)}
                  <span className="text-[9px] font-bold text-slate-600 dark:text-slate-400">{device.batteryStatus}%</span>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-[8px] font-bold text-slate-400 uppercase tracking-widest">Last Sync</span>
                  <span className="text-[9px] font-medium text-slate-500">{device.lastSyncTime.split(' ').slice(1).join(' ')}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-slate-100 dark:border-slate-800 mt-auto">
        <Button 
          variant="outline" 
          className="w-full h-8 text-[10px] font-black tracking-widest border-slate-200 dark:border-slate-800 uppercase hover:bg-emerald-50 hover:text-emerald-600 dark:hover:bg-emerald-500/10"
          onClick={onManageDevices}
        >
          MANAGE ALL DEVICES
        </Button>
      </div>
    </div>
  );
}
