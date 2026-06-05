import React, { createContext, useContext, useState } from "react";
import { clearAuthStorage, loginWithBackend, type LoginResponse } from "../../api/authClient";

export type UserRole = "admin" | "manager" | "employee";

export interface AuthUser {
  id?: number;
  email: string;
  role?: UserRole;
  name?: string;
  initials?: string;
  employeeId?: string;
  companyId?: string;
  employeeCode?: string;
}

interface AuthContextType {
  user: AuthUser | null;
  token?: string | null;
  login: (
    email: string,
    password: string,
    role?: UserRole
  ) => Promise<{
    success: boolean;
    message?: string;
  }>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

function readStoredUser(): AuthUser | null {
  const raw = localStorage.getItem("hrms_user");
  if (!raw) return null;

  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    localStorage.removeItem("hrms_user");
    return null;
  }
}

function decodeJwtPayload(token: string): Record<string, unknown> {
  try {
    const payload = token.split(".")[1];
    if (!payload) return {};
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(
      base64.length + ((4 - (base64.length % 4)) % 4),
      "="
    );
    return JSON.parse(atob(padded)) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function stringClaim(
  claims: Record<string, unknown>,
  key: string
): string | undefined {
  const value = claims[key];
  return typeof value === "string" && value.trim() ? value : undefined;
}

function initialsFromName(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "??";
  return parts
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

const BACKEND_ROLE_TO_UI: Record<string, UserRole> = {
  ADMIN: "admin",
  MANAGER: "manager",
  EMPLOYEE: "employee",
};

function resolveBackendRole(data: LoginResponse, selectedRole: UserRole | undefined): UserRole | null {
  const fromType = (data as any).user_type ? (BACKEND_ROLE_TO_UI as any)[(data as any).user_type] : undefined;
  if (fromType) return fromType;

  const roleCodes = (data as any).roles ?? [];
  const codes = roleCodes.map((r: any) => r.role_code).filter(Boolean) as string[];

  if (codes.includes("ADMIN")) return "admin";
  if (codes.some((c) => c === "HR_MANAGER" || c === "MANAGER")) return "manager";
  if (codes.includes("EMPLOYEE")) return "employee";

  if (selectedRole === "admin") return "admin";
  return "employee";
}

function buildAuthUser(
  data: LoginResponse,
  email: string,
  role: UserRole,
): AuthUser {
  const profile = (data as any).user;
  const name = (profile?.full_name as string | undefined)?.trim() || (profile?.email as string | undefined) || email;

  return {
    email: (profile?.email as string) ?? email,
    role,
    name,
    initials: initialsFromName(name),
    employeeId: (profile?.employee_id as string | undefined) ?? (profile?.employee_code as string | undefined),
    companyId: (profile?.company_id as string | undefined),
    employeeCode: profile?.employee_code,
  };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    try {
      const token = localStorage.getItem("hrms_access_token");
      const stored = localStorage.getItem("hrms_user");
      if (!token || !stored) return null;
      return JSON.parse(stored) as AuthUser;
    } catch {
      return null;
    }
  });

  const [loading] = useState(false);

  const login = async (email: string, password: string, role?: UserRole) => {
    const result = await loginWithBackend(email, password);

    if (!result.success || !result.data) {
      return { success: false, message: result.message ?? "Login failed." };
    }

    const data = result.data;
    const backendRole = resolveBackendRole(data, role);

    if (!backendRole || (role && backendRole !== role)) {
      clearAuthStorage();
      const roleLabel = role ? role.charAt(0).toUpperCase() + role.slice(1) : "role";
      return {
        success: false,
        message: `This account is not authorized as ${roleLabel}. Select the correct role or use another account.`,
      };
    }

    localStorage.setItem("hrms_access_token", data.access);
    localStorage.setItem("hrms_refresh_token", data.refresh);

    const userData = buildAuthUser(data, email.trim().toLowerCase(), backendRole ?? (role ?? "employee"));
    if (userData.companyId) {
      localStorage.setItem("hrms_company_id", userData.companyId);
    }

    setUser(userData);
    localStorage.setItem("hrms_user", JSON.stringify(userData));
    return { success: true };
  };

  const logout = () => {
    setUser(null);
    clearAuthStorage();
  };

  const isAuthenticated = !!user && !!localStorage.getItem("hrms_access_token");

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
