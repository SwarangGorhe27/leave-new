import { Settings2 } from "lucide-react";
import { SuperadminSettings } from "./leave/sections/SuperadminSettings";

export function AdminSettingsPage() {
  return (
    <div className="portal-page admin-dashboard">
      <div className="flex items-center gap-4">
        <div className="rounded-2xl bg-secondary p-3">
          <Settings2 className="w-5 h-5 text-foreground" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-foreground">Settings</h1>
          {/* <p className="text-sm text-muted-foreground mt-1">
            Manage admin configuration and system preferences from here.
          </p> */}
        </div>
      </div>

      <SuperadminSettings />
    </div>
  );
}
