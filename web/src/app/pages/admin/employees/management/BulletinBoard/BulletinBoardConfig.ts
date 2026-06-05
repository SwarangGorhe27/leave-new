import { BulletinCategoryMaster, EmployeeFilterMaster } from "./types";

export const BULLETIN_CATEGORIES: BulletinCategoryMaster[] = [
  { id: "general", label: "General" },
  { id: "notification", label: "Notification" },
  { id: "hr-campaign", label: "H&R Campaign" },
];

export const EMPLOYEE_FILTERS: EmployeeFilterMaster[] = [
  { id: "all", label: "All Employees" },
  { id: "above-5-years", label: "Above 5 years" },
  { id: "all-current", label: "All Current Employees" },
  { id: "all-past", label: "All Past Employees" },
  { id: "bangalore", label: "Bangalore Employees" },
  { id: "3-5-years", label: "Between 3 – 5 years" },
  { id: "confirmed", label: "Confirmed Employees" },
  { id: "contract", label: "Contract Emp" },
  { id: "partially-vaccinated", label: "Partially Vaccinated Employees" },
  { id: "probation", label: "Probation Emp" },
  { id: "sales", label: "Sales Department" },
  { id: "trainee", label: "Trainee Employees" },
  { id: "upto-3-years", label: "Upto 3 years service" },
];

export const SUPPORTED_FILE_EXTENSIONS = [
  "pdf", "xls", "xlsx", "doc", "docx", "txt", "ppt", "pptx", "gif", "jpg", "png"
];
