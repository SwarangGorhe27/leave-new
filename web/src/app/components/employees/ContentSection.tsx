import { Employee } from "./mockData";
import { SidebarSection } from "./SidebarMenu";
import { EmployeeProfile } from "./sections/EmployeeProfile";
import { EducationDetails } from "./sections/EducationDetails";
import { BackgroundCheck } from "./sections/BackgroundCheck";
import { BankDetails } from "./sections/BankDetails";
import { FamilyDetails } from "./sections/FamilyDetails";
import { NomineeDetails } from "./sections/NomineeDetails";
import { InsuranceDetails } from "./sections/InsuranceDetails";
import { AssetManagement } from "./sections/AssetManagement";
import { PassportVisa } from "./sections/PassportVisa";
import { PositionHistory } from "./sections/PositionHistory";
import { WorkExperience } from "./sections/WorkExperience";
import { SalarySummary } from "./sections/SalarySummary";
import { AccessCardDetails } from "./sections/AccessCardDetails";
import { EmployeeDocumentsSection } from "./sections/EmployeeDocumentsSection";

interface Props {
  employee: Employee;
  activeSection: SidebarSection;
  showAddButtons?: boolean;
  /** ESS employee/manager — sections are view-only; edits via My Request */
  essReadOnly?: boolean;
  /** Allow "Add New Document" on admin views where other add buttons stay hidden */
  allowDocumentTypeManagement?: boolean;
  /** Add New on Education / Family / Nominee / Work Experience (admin employee information disables this) */
  showRecordAddButtons?: boolean;
  disableBankEdit?: boolean;
  showAssetAccessActions?: boolean;
  showSalaryActions?: boolean;
  isFinalSubmitted?: boolean;
}

export function ContentSection({
  employee,
  activeSection,
  showAddButtons = true,
  essReadOnly = false,
  allowDocumentTypeManagement = false,
  showRecordAddButtons = true,
  disableBankEdit = false,
  showAssetAccessActions = true,
  showSalaryActions = true,
  isFinalSubmitted = false,
}: Props) {
  const locked = essReadOnly || isFinalSubmitted;
  const allowRecordAdd = showRecordAddButtons && showAddButtons && !essReadOnly;
  switch (activeSection) {
    case "profile":
      return <EmployeeProfile employee={employee} isFinalSubmitted={locked} />;
    case "bank":
      return <BankDetails employee={employee} disableEdit={disableBankEdit} showAddButton />;
    case "family":
      return <FamilyDetails employee={employee} showAddButton={allowRecordAdd} />;
    case "nominee":
      return <NomineeDetails employee={employee} showAddButton={allowRecordAdd} />;
    case "insurance":
      return <InsuranceDetails employee={employee} showAddButton={showAddButtons && !essReadOnly} />;
    case "assets":
      return <AssetManagement employee={employee} showActions={showAssetAccessActions && !essReadOnly} />;
    case "passport":
      return <PassportVisa employee={employee} />;
    case "position":
      return <PositionHistory employee={employee} showAddButton={showAddButtons && !essReadOnly} />;
    case "work":
      return <WorkExperience employee={employee} showAddButton={allowRecordAdd} />;
    case "education":
      return <EducationDetails employee={employee} showAddButton={allowRecordAdd} />;
    case "background":
      return <BackgroundCheck employee={employee} showActions={!essReadOnly} />;
    case "access":
      return <AccessCardDetails employee={employee} showActions={showAssetAccessActions} />;
    case "documents":
      return (
        <EmployeeDocumentsSection
          employee={employee}
          showAddButton={showAddButtons || allowDocumentTypeManagement}
        />
      );
    case "salary":
      return <SalarySummary employee={employee} showActions={showSalaryActions} />;
    default:
      return <EmployeeProfile employee={employee} />;
  }
}
