export function SuperadminSystemSettings() {
  return (
    <div className="flat-card bg-card p-6 space-y-4">
      <h2 className="text-sm font-semibold text-foreground">System Settings</h2>
      {/* <p className="text-xs text-muted-foreground">Global leave control flags for superadmin governance.</p> */}
      <div className="space-y-3">
        {[
          "Allow superadmin override on all request states",
          "Enable force approve / reject / cancel with audit logging",
          "Allow soft delete and restore for leave requests",
          "Enable cross-department visibility for superadmin role",
        ].map((item) => (
          <div key={item} className="p-3 rounded-lg border border-border bg-secondary/40 text-sm text-foreground">
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}

