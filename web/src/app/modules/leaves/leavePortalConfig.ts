export type LeavePortalRole = "employee" | "manager";

export function leavePortalBasePath(role: LeavePortalRole): string {
  return role === "manager" ? "/manager/leaves" : "/employee/leaves";
}

export function leavePortalTabs(basePath: string) {
  return [
    { label: "Apply Leave", path: `${basePath}/apply` },
    { label: "My Applications", path: `${basePath}/applications` },
    { label: "Leave Balance", path: `${basePath}/balance` },
    { label: "Holiday Calendar", path: `${basePath}/holidays` },
    { label: "Leave Policy", path: `${basePath}/policy` },
    { label: "Notifications", path: `${basePath}/notifications` },
  ];
}

export function leaveApplyNavTabs(basePath: string) {
  return [
    { label: "Apply", path: `${basePath}/apply` },
    { label: "Pending", path: `${basePath}/applications` },
    { label: "History", path: `${basePath}/applications` },
  ];
}
