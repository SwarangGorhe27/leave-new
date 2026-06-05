import api from "./client";

export interface Manager {
  id: string;
  name: string;
  employeeCode: string;
  designation: string | null;
  department: string | null;
}

export interface ManagersResponse {
  results: Manager[];
}

/**
 * Fetch all active managers from the ReportingManager table
 * Used for dropdowns in employee forms
 */
export async function fetchManagers(): Promise<Manager[]> {
  try {
    const response = await api.get<ManagersResponse>(
      "/masters/audit-additions/reporting-managers/simple_list/"
    );
    console.log("Fetched managers:", response.data.results);
    return response.data.results || [];
  } catch (error) {
    console.error("Error fetching managers:", error);
    throw error;
  }
}

/**
 * Fetch managers for a specific company
 */
export async function fetchManagersByCompany(companyId: string): Promise<Manager[]> {
  try {
    const response = await api.get<ManagersResponse>(
      "/masters/audit-additions/reporting-managers/simple_list/",
      {
        params: { company_id: companyId },
      }
    );
    return response.data.results || [];
  } catch (error) {
    console.error("Error fetching managers for company:", error);
    throw error;
  }
}

/**
 * Fetch managers by designation
 */
export async function fetchManagersByDesignation(
  designationId: string
): Promise<Manager[]> {
  try {
    const response = await api.get<ManagersResponse>(
      "/masters/audit-additions/reporting-managers/simple_list/",
      {
        params: { designation_id: designationId },
      }
    );
    return response.data.results || [];
  } catch (error) {
    console.error("Error fetching managers by designation:", error);
    throw error;
  }
}

/**
 * Fetch managers by department
 */
export async function fetchManagersByDepartment(departmentId: string): Promise<Manager[]> {
  try {
    const response = await api.get<ManagersResponse>(
      "/masters/audit-additions/reporting-managers/simple_list/",
      {
        params: { department_id: departmentId },
      }
    );
    return response.data.results || [];
  } catch (error) {
    console.error("Error fetching managers by department:", error);
    throw error;
  }
}
