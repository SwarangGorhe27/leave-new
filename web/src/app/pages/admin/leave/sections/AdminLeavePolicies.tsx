import { Plus } from "lucide-react";

export function AdminLeavePolicies({ onAddNewPolicy }: { onAddNewPolicy?: () => void }) {
  return (
    <div className="space-y-5">
      <div className="flat-card bg-card p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-semibold text-foreground">Leave Policy Management</h2>
            {/* <p className="text-sm text-muted-foreground mt-1">
              Manage policy rules, accrual logic, carry-forward, eligibility, and workflow settings.
            </p> */}
          </div>
          <button
            type="button"
            onClick={onAddNewPolicy}
            className="px-3 py-2 rounded-lg text-xs font-semibold bg-foreground text-primary-foreground hover:bg-accent transition-colors inline-flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add New Policy
          </button>
        </div>
      </div>
    </div>
  );
}

