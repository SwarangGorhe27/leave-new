import React, { createContext, useContext } from 'react';

interface EmployeeFormContextType {
  finalSubmitted: boolean;
  /** ESS (employee/manager) — view-only sections; edits via My Request */
  essReadOnly?: boolean;
}

const EmployeeFormContext = createContext<EmployeeFormContextType | null>(null);

export const EmployeeFormProvider = ({ children, value }: { children: React.ReactNode; value: EmployeeFormContextType }) => {
  return <EmployeeFormContext.Provider value={value}>{children}</EmployeeFormContext.Provider>;
};

export const useEmployeeFormContext = () => {
  return useContext(EmployeeFormContext);
};

export default EmployeeFormContext;
