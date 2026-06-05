import { Link } from "react-router";
import { Button } from "../../../../components/ui/button";
 
export function SuperadminSettings() {
  return (
    <div className="space-y-4">
      <div className="flat-card bg-card p-4">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-sm font-semibold text-foreground">Settings</h2>
          <Button asChild size="sm" className="h-8 rounded-lg">
            <Link to="/superadmin/masters">Master Management</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}