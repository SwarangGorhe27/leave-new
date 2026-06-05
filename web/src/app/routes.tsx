import { createBrowserRouter, Navigate, useParams } from "react-router";
import { lazy, Suspense } from "react";

function LeaveRouteError() {
  return (
    <div className="p-8 mx-auto max-w-3xl text-center rounded-2xl border border-border bg-card shadow-sm">
      <h1 className="text-xl font-semibold text-foreground">Unable to open leave portal</h1>
      <p className="mt-3 text-sm text-muted-foreground">
        There was a problem loading the leave page. Please refresh the page or contact support if this keeps happening.
      </p>
    </div>
  );
}

// Auth
import { LoginPage } from "./pages/LoginPage";

// Admin
import { AdminLayout } from "./pages/admin/AdminLayout";
import { DashboardPage } from "./pages/admin/DashboardPage";
import { AttendanceLayout } from "./pages/admin/attendance/AttendanceLayout";
import { AttendanceDashboard } from "./pages/admin/attendance/AttendanceDashboard";
import { WhosInPage } from "./pages/admin/attendance/WhosInPage";
import { ShiftRosterPage } from "./pages/admin/attendance/ShiftRosterPage";
import { SwipeLogsPage } from "./pages/admin/attendance/SwipeLogsPage";
const AttendanceMatrixPage = lazy(() => import("./pages/admin/attendance/AttendanceMatrixPage").then(m => ({ default: m.AttendanceMatrixPage })));
const AttendanceRequestsPage = lazy(() => import("./pages/admin/attendance/AttendanceRequestsPage").then(m => ({ default: m.AttendanceRequestsPage })));
import { LeavePage } from "./pages/admin/LeavePage";
import { PayrollPage } from "./pages/admin/PayrollPage";
import { PayrollLayout } from "./pages/admin/payroll/PayrollLayout";
import { DocumentsPage } from "./pages/admin/DocumentsPage";
import { AdminSettingsPage } from "./pages/admin/SettingsPage";
import { EmployeesShell } from "./pages/admin/employees/EmployeesShell";
import { AddEmployeePage } from "./pages/admin/employees/AddEmployeePage";
import { EmployeeManagementLayout } from "./pages/admin/employees/EmployeeManagementLayout";
import { EmployeeSetupLayout } from "./pages/admin/employees/EmployeeSetupLayout";
import { LettersPoliciesLayout } from "./pages/admin/letters-policies/LettersPoliciesLayout";
import { CommunicationCenterLayout } from "./pages/admin/communication-center/CommunicationCenterLayout";
import { MASTER_CATEGORIES } from "./modules/masters/config";
// import { MainShell } from "./pages/admin/main/MainShell";
// import { AnalyticsHubPage } from "./pages/admin/main/AnalyticsHubPage";
// import { EmployeeDirectoryPage } from "./pages/admin/main/EmployeeDirectoryPage";
// import { EmployeeDirectoryModulePage } from "./pages/admin/main/EmployeeDirectoryModulePage";

// Superadmin
import { SuperadminMastersPage } from "./pages/admin/masters/SuperadminMastersPage";
import { OffboardingPage } from "./pages/admin/employees/offboarding/OffboardingPage";

// Management Pages (Lazy Loaded)
const GenerateLetterPage = lazy(() => import("./pages/admin/employees/management/GenerateLetterPage").then(m => ({ default: m.GenerateLetterPage })));
const BulletinBoardPage = lazy(() => import("./pages/admin/employees/management/BulletinBoardPage").then(m => ({ default: m.BulletinBoardPage })));
const MassCommunicationPage = lazy(() => import("./pages/admin/employees/management/MassCommunicationPage").then(m => ({ default: m.MassCommunicationPage })));
const IdentityVerificationPage = lazy(() => import("./pages/admin/employees/management/IdentityVerificationPage").then(m => ({ default: m.IdentityVerificationPage })));
const ContractDetailsPage = lazy(() => import("./pages/admin/employees/management/ContractDetailsPage").then(m => ({ default: m.ContractDetailsPage })));

// Setup Pages (Lazy Loaded)
const LetterTemplatePage = lazy(() => import("./pages/admin/employees/setup/LetterTemplatePage").then(m => ({ default: m.LetterTemplatePage })));
const PoliciesFormsPage = lazy(() => import("./pages/admin/employees/setup/PoliciesFormsPage").then(m => ({ default: m.PoliciesFormsPage })));
const EmployeeSegmentPage = lazy(() => import("./pages/admin/employees/setup/EmployeeSegmentPage").then(m => ({ default: m.EmployeeSegmentPage })));
const EmployeeRolesPage = lazy(() => import("./pages/admin/employees/setup/EmployeeRolesPage").then(m => ({ default: m.EmployeeRolesPage })));
const EmployeeFilterPage = lazy(() => import("./pages/admin/employees/setup/EmployeeFilterPage").then(m => ({ default: m.EmployeeFilterPage })));
const FinesDamagesPage = lazy(() => import("./pages/admin/employees/setup/FinesDamagesPage").then(m => ({ default: m.FinesDamagesPage })));
const OrganizationChartPage = lazy(() => import("./pages/admin/employees/OrganizationChartPage").then(m => ({ default: m.OrganizationChartPageWrapper })));

// Employee module components
import { EmployeeDirectory } from "./components/employees/EmployeeDirectory";
import { InformationLayout } from "./components/employees/InformationLayout";

// Employee portal
import { ManagerLayout } from "./pages/manager/ManagerLayout";
import { ManagerDashboard } from "./pages/manager/ManagerDashboard";
import { ManagerAttendancePage } from "./pages/manager/ManagerAttendancePage";
import { ManagerTeamAttendancePage } from "./pages/manager/ManagerTeamAttendancePage";
import { ManagerLeavesLayout } from "./pages/manager/leaves/ManagerLeavesLayout";
import { ManagerLeaveApplyPage } from "./pages/manager/leaves/ManagerLeaveApplyPage";
import { ManagerLeaveApplicationsPage } from "./pages/manager/leaves/ManagerLeaveApplicationsPage";
import { ManagerLeaveBalancePage } from "./pages/manager/leaves/ManagerLeaveBalancePage";
import { ManagerLeaveHolidaysPage } from "./pages/manager/leaves/ManagerLeaveHolidaysPage";
import { ManagerLeaveTeamCalendarPage } from "./pages/manager/leaves/ManagerLeaveTeamCalendarPage";
import { ManagerLeavePolicyPage } from "./pages/manager/leaves/ManagerLeavePolicyPage";
import { ManagerLeaveNotificationsPage } from "./pages/manager/leaves/ManagerLeaveNotificationsPage";
import { ManagerPayslipsPage } from "./pages/manager/ManagerPayslipsPage";
import { ManagerDocumentsPage } from "./pages/manager/ManagerDocumentsPage";
import { ManagerProfilePage } from "./pages/manager/ManagerProfilePage";
import { ManagerApprovalsLayout } from "./pages/manager/approvals/ManagerApprovalsLayout";
import ManagerApprovalsRequestsPage from "./pages/manager/approvals/ManagerApprovalsRequestsPage";
import { EmployeeLayout } from "./pages/employee/EmployeeLayout";
import { EmployeeDashboard } from "./pages/employee/EmployeeDashboard";
import { EmployeeAttendancePage } from "./pages/employee/EmployeeAttendancePage";
import { EmployeeLeavesLayout } from "./pages/employee/leaves/EmployeeLeavesLayout";
import { EmployeeLeaveApplyPage } from "./pages/employee/leaves/EmployeeLeaveApplyPage";
import { EmployeeLeaveApplicationsPage } from "./pages/employee/leaves/EmployeeLeaveApplicationsPage";
import { EmployeeLeaveBalancePage } from "./pages/employee/leaves/EmployeeLeaveBalancePage";
import { EmployeeLeaveHolidaysPage } from "./pages/employee/leaves/EmployeeLeaveHolidaysPage";
import { EmployeeLeaveTeamCalendarPage } from "./pages/employee/leaves/EmployeeLeaveTeamCalendarPage";
import { EmployeeLeavePolicyPage } from "./pages/employee/leaves/EmployeeLeavePolicyPage";
import { EmployeeLeaveNotificationsPage } from "./pages/employee/leaves/EmployeeLeaveNotificationsPage";
import { EmployeePayslipsPage } from "./pages/employee/EmployeePayslipsPage";
import { EmployeeDocumentsPage } from "./pages/employee/EmployeeDocumentsPage";
import { EmployeeCanteenPage } from "./pages/employee/EmployeeCanteenPage";
import { EmployeeProfilePage } from "./pages/employee/EmployeeProfilePage";
import { ProfileChangeRequestsPage } from "./pages/admin/ProfileChangeRequestsPage";
import { AdminProfilePage } from "./pages/admin/AdminProfilePage";

// Leave admin/components (lazy — avoid crashing login on import errors)
const AdminLeaveTypes = lazy(() => import("../pages/admin/leave/AdminLeaveTypes"));
const AdminLeaveMappings = lazy(() => import("../pages/admin/leave/AdminLeaveMappings"));
const ManagerLeaveApprovals = lazy(() => import("../pages/leave/ManagerLeaveApprovals"));
const EmployeeLeaveDashboard = lazy(() => import("../pages/leave/EmployeeLeaveDashboard"));

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/login" replace />,
  },
  {
    path: "/login",
    Component: LoginPage,
  },
  {
    path: "/leave/dashboard",
    element: <Navigate to="/employee/leaves/dashboard" replace />,
  },
  {
    path: "/leave/approvals",
    element: <Navigate to="/manager/approvals/leave" replace />,
  },
  {
    path: "/admin",
    Component: AdminLayout,
    children: [
      { index: true, element: <Navigate to="/admin/dashboard" replace /> },
      { path: "dashboard", Component: DashboardPage },
      {
        path: "attendance",
        Component: AttendanceLayout,
        children: [
          { index: true, element: <Navigate to="dashboard" replace /> },
          { path: "dashboard", Component: AttendanceDashboard },
          { path: "whos-in", Component: WhosInPage },
          { path: "roster", Component: ShiftRosterPage },
          { path: "swipe-logs", Component: SwipeLogsPage },
          { path: "matrix", element: <Suspense fallback={<div className="p-8 text-center animate-pulse font-bold text-slate-400">Loading Matrix...</div>}><AttendanceMatrixPage /></Suspense> },
          { path: "requests", element: <Suspense fallback={<div className="p-8 text-center animate-pulse font-bold text-slate-400">Loading Requests...</div>}><AttendanceRequestsPage /></Suspense> },
        ]
      },
      { path: "leave", Component: LeavePage },
      {
        path: "leave/types",
        element: (
          <Suspense fallback={<ManagementSkeleton />}>
            <AdminLeaveTypes />
          </Suspense>
        ),
      },
      {
        path: "leave/mappings",
        element: (
          <Suspense fallback={<ManagementSkeleton />}>
            <AdminLeaveMappings />
          </Suspense>
        ),
      },
      {
        path: "payroll",
        Component: PayrollLayout,
        children: [
          { index: true, element: <Navigate to="overview" replace /> },
          { path: "overview", Component: PayrollPage },
          { path: "fines-damages", element: <Suspense fallback={<ManagementSkeleton />}><FinesDamagesPage /></Suspense> },
        ]
      },
      {
        path: "letters-policies",
        Component: LettersPoliciesLayout,
        children: [
          { index: true, element: <Navigate to="generate-letter" replace /> },
          { path: "generate-letter", element: <Suspense fallback={<ManagementSkeleton />}><GenerateLetterPage /></Suspense> },
          { path: "policies", element: <Suspense fallback={<ManagementSkeleton />}><PoliciesFormsPage /></Suspense> },
        ]
      },
      {
        path: "communication-center",
        Component: CommunicationCenterLayout,
        children: [
          { index: true, element: <Navigate to="bulletin-board" replace /> },
          { path: "bulletin-board", element: <Suspense fallback={<ManagementSkeleton />}><BulletinBoardPage /></Suspense> },
          { path: "communication", element: <Suspense fallback={<ManagementSkeleton />}><MassCommunicationPage /></Suspense> },
        ]
      },
      { path: "documents", Component: DocumentsPage },
      { path: "settings", Component: AdminSettingsPage },
      { path: "profile", Component: AdminProfilePage },
      { path: "profile-requests", Component: ProfileChangeRequestsPage },
      {
        path: "employees",
        Component: EmployeesShell,
        children: [
          { index: true, Component: EmployeeDirectory },
          // {
          //   path: "main",
          //   Component: MainShell,
          //   children: [
          //     { index: true, element: <Navigate to="directory" replace /> },
          //     { path: "analytics", Component: AnalyticsHubPage },
          //     { path: "directory", Component: EmployeeDirectoryPage },
          //     { path: "directory-module", Component: EmployeeDirectoryModulePage },
          //   ],
          // },
          { path: "add", Component: AddEmployeePage },
          { path: "import", element: <Navigate to="/admin/letters-policies/generate-letter" replace /> },
          { path: "information/:id", Component: InformationLayout },
          {
            path: "management",
            Component: EmployeeManagementLayout,
            children: [
              { index: true, element: <Navigate to="verification" replace /> },
              { path: "verification", element: <Suspense fallback={<ManagementSkeleton />}><IdentityVerificationPage /></Suspense> },
              { path: "contracts", element: <Suspense fallback={<ManagementSkeleton />}><ContractDetailsPage /></Suspense> },
              { path: "excel-import", element: <Navigate to="/admin/letters-policies/generate-letter" replace /> },
              { path: "photo-upload", element: <Navigate to="/admin/letters-policies/generate-letter" replace /> },
              { path: "data-drive", element: <Navigate to="/admin/letters-policies/generate-letter" replace /> },
            ]
          },
          {
            path: "setup",
            Component: EmployeeSetupLayout,
            children: [
              { index: true, element: <Navigate to="segment" replace /> },
              { path: "segment", element: <Suspense fallback={<ManagementSkeleton />}><EmployeeSegmentPage /></Suspense> },
              { path: "roles", element: <Suspense fallback={<ManagementSkeleton />}><EmployeeRolesPage /></Suspense> },
              { path: "filter", element: <Suspense fallback={<ManagementSkeleton />}><EmployeeFilterPage /></Suspense> },
            ]
          },
          { path: "reports", element: <div className="p-8 text-center text-muted-foreground font-medium">Employee Reports Module (Coming Soon)</div> },
          {
            path: "org-chart",
            element: (
              <Suspense fallback={<OrgChartSkeleton />}>
                <OrganizationChartPage />
              </Suspense>
            ),
          },
          { path: "offboarding", Component: OffboardingPage },
        ],
      },
    ],
  },
  {
    path: "/manager",
    Component: ManagerLayout,
    children: [
      { index: true, element: <Navigate to="/manager/dashboard" replace /> },
      { path: "dashboard", Component: ManagerDashboard },
      { path: "profile", Component: ManagerProfilePage },
      { path: "attendance", Component: ManagerAttendancePage },
      {
        path: "leaves",
        Component: ManagerLeavesLayout,
        children: [
          { index: true, element: <Navigate to="apply" replace /> },
          { path: "dashboard", element: <Navigate to="/manager/leaves/apply" replace /> },
          { path: "dashboard-redirect", element: <Navigate to="/manager/leaves/apply" replace /> },
          { path: "apply", Component: ManagerLeaveApplyPage },
          { path: "applications", Component: ManagerLeaveApplicationsPage },
          { path: "balance", Component: ManagerLeaveBalancePage },
          { path: "holidays", Component: ManagerLeaveHolidaysPage },
          { path: "team", Component: ManagerLeaveTeamCalendarPage },
          { path: "policy", Component: ManagerLeavePolicyPage },
          { path: "notifications", Component: ManagerLeaveNotificationsPage },
        ],
      },
      { path: "payslips", Component: ManagerPayslipsPage },
      { path: "documents", Component: ManagerDocumentsPage },
      { path: "team-dashboard", element: <div className="p-8 text-center text-muted-foreground font-medium">Team Dashboard (Coming Soon)</div> },
      { path: "team-attendance", Component: ManagerTeamAttendancePage },
      {
        path: "approvals",
        Component: ManagerApprovalsLayout,
        children: [
          { index: true, element: <Navigate to="requests" replace /> },
          { path: "requests", Component: ManagerApprovalsRequestsPage },
          { path: "leave", element: <Suspense fallback={<ManagementSkeleton />}><ManagerLeaveApprovals /></Suspense> },
        ],
      },
      { path: "reports", element: <div className="p-8 text-center text-muted-foreground font-medium">Reports (Coming Soon)</div> },
      { path: "org-chart", element: <div className="p-8 text-center text-muted-foreground font-medium">Organization Chart (Coming Soon)</div> },
    ],
  },
  {
    path: "/employee",
    Component: EmployeeLayout,
    children: [
      { index: true, element: <Navigate to="/employee/dashboard" replace /> },
      { path: "dashboard", Component: EmployeeDashboard },
      { path: "profile", Component: EmployeeProfilePage },
      { path: "attendance", Component: EmployeeAttendancePage },
      {
        path: "leaves",
        Component: EmployeeLeavesLayout,
        errorElement: <LeaveRouteError />,
        children: [
          { index: true, element: <Navigate to="apply" replace /> },
          { path: "dashboard", element: <Suspense fallback={<ManagementSkeleton />}><EmployeeLeaveDashboard /></Suspense> },
          { path: "apply", Component: EmployeeLeaveApplyPage },
          { path: "applications", Component: EmployeeLeaveApplicationsPage },
          { path: "balance", Component: EmployeeLeaveBalancePage },
          { path: "holidays", Component: EmployeeLeaveHolidaysPage },
          { path: "team", Component: EmployeeLeaveTeamCalendarPage },
          { path: "policy", Component: EmployeeLeavePolicyPage },
          { path: "notifications", Component: EmployeeLeaveNotificationsPage },
        ],
      },
      { path: "payslips", Component: EmployeePayslipsPage },
      { path: "documents", Component: EmployeeDocumentsPage },
      { path: "canteen", Component: EmployeeCanteenPage },
    ],
  },
  {
    path: "/employees/*",
    element: <Navigate to="/admin/employees" replace />,
  },
  {
    path: "/superadmin",
    Component: AdminLayout,
    children: [
      {
        path: "masters",
        children: [
          {
            index: true,
            element: (
              <Navigate
                to={`${MASTER_CATEGORIES[0]?.key}/${MASTER_CATEGORIES[0]?.masters[0]?.key}`}
                replace
              />
            ),
          },
          {
            path: ":category",
            element: <SuperadminMastersCategoryRedirect />,
          },
          {
            path: ":category/:masterName",
            Component: SuperadminMastersPage,
          },
        ],
      },
    ],
  },
]);

function SuperadminMastersCategoryRedirect() {
  const { category: categoryParam } = useParams();
  const category = MASTER_CATEGORIES.find((item) => item.key === categoryParam);
  const master = category?.masters[0] ?? MASTER_CATEGORIES[0]?.masters[0];
  const categoryKey = category?.key ?? MASTER_CATEGORIES[0]?.key;

  if (!categoryKey || !master) return <div className="p-6">No masters configured.</div>;
  return <Navigate to={`/superadmin/masters/${categoryKey}/${master.key}`} replace />;
}

function ManagementSkeleton() {
  return (
    <div className="p-8 space-y-6 animate-pulse">
      <div className="h-20 bg-secondary rounded-2xl w-full" />
      <div className="grid grid-cols-3 gap-6">
        <div className="h-64 bg-secondary rounded-2xl" />
        <div className="h-64 bg-secondary rounded-2xl col-span-2" />
      </div>
    </div>
  );
}

function OrgChartSkeleton() {
  return (
    <div className="flex h-full min-h-0 flex-col bg-background">
      <div className="h-[86px] shrink-0 animate-pulse border-b border-border bg-card" />
      <div className="flex min-h-0 flex-1 animate-pulse gap-4 p-6">
        <div className="min-w-0 flex-1 rounded-lg bg-secondary" />
        <div className="w-[254px] shrink-0 rounded-lg bg-secondary" />
      </div>
    </div>
  );
}
