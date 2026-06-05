import React, { createContext, useContext, useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router";

interface EmployeeContextType {
  selectedEmployeeId: string | null;
  selectEmployee: (id: string) => void;
  clearSelection: () => void;
}

const EmployeeContext = createContext<EmployeeContextType | undefined>(undefined);

export function EmployeeProvider({ children }: { children: React.ReactNode }) {
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | null>(null);
  const location = useLocation();
  const navigate = useNavigate();

  // Sync with URL if we are on an information page
  useEffect(() => {
    const match = location.pathname.match(/\/admin\/employees\/information\/([^/]+)/);
    if (match && match[1]) {
      setSelectedEmployeeId(match[1]);
    }
  }, [location.pathname]);

  const selectEmployee = (id: string) => {
    setSelectedEmployeeId(id);
    navigate(`/admin/employees/information/${id}`);
  };

  const clearSelection = () => {
    setSelectedEmployeeId(null);
    navigate("/admin/employees");
  };

  return (
    <EmployeeContext.Provider value={{ selectedEmployeeId, selectEmployee, clearSelection }}>
      {children}
    </EmployeeContext.Provider>
  );
}

export function useEmployee() {
  const context = useContext(EmployeeContext);
  if (context === undefined) {
    throw new Error("useEmployee must be used within an EmployeeProvider");
  }
  return context;
}
