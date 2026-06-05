import { useSelector } from "react-redux";
import { RootState } from "../store";
import { useAuth } from "../app/context/AuthContext";

/**
 * Returns the set of section IDs the current employee is allowed to edit,
 * driven entirely by the admin's `editableSections` checkbox controls.
 */
export function useEssPermissions() {
  const { user } = useAuth();
  const employeeId = user?.employeeId ?? "1";

  const adminEmployee = useSelector((state: RootState) =>
    state.admin.employees.find((e) => e.id === employeeId)
  );

  const editableSections: string[] = adminEmployee?.editableSections ?? [];

  const canEdit = (sectionId: string): boolean => editableSections.includes(sectionId);

  return { editableSections, canEdit, adminEmployee };
}
