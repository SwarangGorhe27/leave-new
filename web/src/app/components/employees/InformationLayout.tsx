import { useState } from "react";
import { useNavigate, useParams } from "react-router";
import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import { SidebarMenu, SidebarSection } from "./SidebarMenu";
import { ContentSection } from "./ContentSection";
import { useEmployee } from "../../context/EmployeeContext";
import { useAdminEmployeeModuleProfile } from "../../../hooks/useEmployeeModuleProfile";
import { cacheEmployeeInRedux } from "../../services/employeeProfilePersistence";
import { useDispatch } from "react-redux";
import { AppDispatch } from "../../../store";
import { useEffect } from "react";

export function InformationLayout() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { clearSelection } = useEmployee();
  const dispatch = useDispatch<AppDispatch>();
  const [activeSection, setActiveSection] = useState<SidebarSection>("profile");

  const { data: employee, isLoading, isError, error, refetch } = useAdminEmployeeModuleProfile(id);

  useEffect(() => {
    if (employee) cacheEmployeeInRedux(dispatch, employee);
  }, [dispatch, employee]);

  const sectionLabels: Record<SidebarSection, string> = {
    profile: "Employee Profile",
    education: "Education Details",
    family: "Family Details",
    nominee: "Nominee Details",
    insurance: "Insurance Details",
    work: "Work Experience",
    position: "Position History",
    bank: "Bank / PF / ESI",
    passport: "Passport & Visa",
    background: "Background Check",
    assets: "Asset Management",
    access: "Access Card Details",
    documents: "Employee Documents",
    salary: "Employee Salary",
  };

  const statusStyle: Record<string, string> = {
    Active: "bg-[#212529] text-[#F8F9FA]",
    "On Leave": "bg-[#6C757D] text-white",
    Inactive: "bg-[#CED4DA] text-[#212529]",
  };

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading employee…
      </div>
    );
  }

  if (isError || !employee) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center">
        <p className="text-sm font-semibold text-foreground">Unable to load employee</p>
        <p className="text-xs text-muted-foreground max-w-md">
          {(error as Error)?.message ?? "Employee record not found or API unavailable."}
        </p>
        <button
          type="button"
          onClick={() => refetch()}
          className="rounded-lg border border-border px-3 py-1.5 text-xs font-bold hover:bg-secondary"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-background">
      <div className="flex flex-shrink-0 items-center justify-between border-b border-border bg-card px-6 py-3">
        <div className="flex flex-wrap items-center gap-1.5 text-sm text-muted-foreground">
          <button
            onClick={() => {
              clearSelection();
              navigate("/admin/employees");
            }}
            className="-ml-2.5 flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm font-semibold text-foreground transition-colors hover:bg-secondary"
          >
            <ChevronLeft className="h-4 w-4" />
            Back to Employee List
          </button>
          <ChevronRight className="h-3.5 w-3.5 text-border" />
          <span className="font-medium">Employees</span>
          <ChevronRight className="h-3.5 w-3.5 text-border" />
          <span className="font-semibold text-foreground">{employee.name}</span>
          <ChevronRight className="h-3.5 w-3.5 text-border" />
          <span className="rounded-md border border-border bg-secondary px-2.5 py-0.5 text-xs font-semibold text-foreground">
            {sectionLabels[activeSection]}
          </span>
        </div>

        <span
          className={`rounded-md px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest ${
            statusStyle[employee.status] ?? "bg-secondary text-muted-foreground"
          }`}
        >
          {employee.status}
        </span>
      </div>

      <div className="relative flex flex-1 overflow-hidden">
        <SidebarMenu activeSection={activeSection} onSectionChange={setActiveSection} />
        <main className="flex-1 overflow-y-auto p-6">
          <ContentSection
            employee={employee}
            activeSection={activeSection}
            showAddButtons
            showRecordAddButtons={false}
            allowDocumentTypeManagement
          />
        </main>
      </div>
    </div>
  );
}
