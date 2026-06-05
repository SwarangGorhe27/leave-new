import { Link, useLocation, useNavigate, useSearchParams } from "react-router";
import { ApplyLeaveFormEnterprise } from "../../../components/leaves/employee/ApplyLeaveFormEnterprise";
import { MyApplicationsView } from "../../../components/leaves/employee/MyApplicationsView";
// import { leaveApplyNavTabs } from "../../../modules/leaves/leavePortalConfig";
import type { LeavePortalDataContextValue } from "../LeavePortalDataContext";

export function LeaveApplyPage({
  basePath,
  useLeaveData,
}: {
  basePath: string;
  useLeaveData: () => Pick<
    LeavePortalDataContextValue,
    "employeeCode" | "employeeName" | "balances" | "refreshAll"
  >;
}) {
  const navigate = useNavigate();
  const location = useLocation();
  const { employeeCode, employeeName, balances, refreshAll } = useLeaveData();
  const [params] = useSearchParams();
  const prefill = params.get("type") ?? undefined;
  // const navTabs = leaveApplyNavTabs(basePath);

  // Determine if we're on the applications route
  const isApplicationsView = location.pathname.includes("/applications");

  return (
    <div className="space-y-6">
      {/* <header className="rounded-3xl border border-border bg-card p-5 sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-foreground sm:text-2xl">Apply for leave</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Structured request with live balance preview and approval routing context.
            </p>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {navTabs.map((tab) => (
            <Link
              key={tab.label}
              to={tab.path}
              className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${
                location.pathname === tab.path
                  ? "border-foreground bg-foreground text-primary-foreground"
                  : "border-border bg-background text-foreground hover:border-foreground/70"
              }`}
            >
              {tab.label}
            </Link>
          ))}
        </div>
      </header> */}

      <ApplyLeaveFormEnterprise
        employee={{ employee_code: employeeCode, employee_name: employeeName }}
        balances={balances}
        prefillLeaveType={prefill}
        onSuccess={() => {
          refreshAll();
          navigate(`${basePath}/applications`);
        }}
      />
    </div>
  );
}
