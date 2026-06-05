import { useState } from "react";
import { useNavigate } from "react-router";
import {
  Eye,
  EyeOff,
  ArrowRight,
  ShieldCheck,
  User,
  Users,
  Lock,
  Mail,
  Moon,
  Sun,
} from "lucide-react";

import { useAuth, UserRole } from "../context/AuthContext";
import loginGraphic from "../../assets/login_graphic.png";
import { readPersistedTheme, setGlobalTheme } from "../../lib/theme";

/* =========================
   MINIMAL ENTERPRISE THEME (Notion / Stripe / Linear style)
========================= */

const COLORS = {
  light: {
    bg: "#F8FAFC",
    panel: "rgba(255,255,255,0.92)",
    border: "rgba(15,23,42,0.08)",
    primary: "#6366F1",
    text: "#0F172A",
    muted: "#64748B",
  },
  dark: {
    bg: "#020617",
    panel: "rgba(15,23,42,0.88)",
    border: "rgba(255,255,255,0.06)",
    primary: "#818CF8",
    text: "#F8FAFC",
    muted: "#94A3B8",
  },
};

// Features grid is replaced by the interactive graphic showcase

const ROLES: {
  value: UserRole;
  label: string;
  icon: React.ReactNode;
}[] = [
  {
    value: "admin",
    label: "Admin",
    icon: <ShieldCheck size={14} />,
  },
  {
    value: "manager",
    label: "Manager",
    icon: <Users size={14} />,
  },
  {
    value: "employee",
    label: "Employee",
    icon: <User size={14} />,
  },
];

const DEMO: Record<
  UserRole,
  { email: string; password: string }
> = {
  admin: {
    email: "hr.admin@company.com",
    password: "Password@123",
  },
  manager: {
    email: "hr.manager@company.com",
    password: "Password@123",
  },
  employee: {
    email: "jane.employee@company.com",
    password: "Password@123",
  },
};  

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [theme, setThemeState] = useState<"light" | "dark">(() =>
    readPersistedTheme()
  );

  const c = COLORS[theme];

  const [role, setRole] = useState<UserRole>("admin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleThemeToggle = () => {
    const nextTheme = theme === "light" ? "dark" : "light";
    setThemeState(nextTheme);
    setGlobalTheme(nextTheme);
  };

  const switchRole = (r: UserRole) => {
    setRole(r);
    setError("");
    setEmail("");
    setPassword("");
  };

  const fillDemo = () => {
    setEmail(DEMO[role].email);
    setPassword(DEMO[role].password);
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      setError("Please enter email and password.");
      return;
    }

    setLoading(true);
    setError("");

    const result = await login(email, password, role);

    setLoading(false);

    if (result.success) {
      navigate(
        role === "admin"
          ? "/admin/dashboard"
          : role === "manager"
          ? "/manager/dashboard"
          : "/employee/dashboard",
        { replace: true }
      );
    } else {
      setError(result.message || "Invalid credentials.");
    }
  };

  return (
    <>
      <style>{`
      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      }

      .login-root {
        display: flex;
        min-height: 100vh;
        background: ${c.bg};
        color: ${c.text};
        transition: background-color 0.2s ease, color 0.2s ease;
      }

      .login-container {
        display: grid;
        grid-template-columns: 1.05fr 0.95fr;
        width: 100%;
        min-height: 100vh;
      }

      /* LEFT PANEL (Cinematic Enterprise Identity) */
      .left-panel {
        background: #0B1120;
        padding: clamp(32px, 5vw, 68px) clamp(28px, 5.4vw, 82px);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border-right: 1px solid ${theme === 'light' ? 'rgba(15,23,42,0.08)' : 'rgba(255,255,255,0.06)'};
        position: relative;
        overflow: hidden;
        isolation: isolate;
        min-height: 100vh;
      }

      .left-bg-img {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center;
        filter: saturate(1.02) contrast(1.04) brightness(${theme === 'light' ? '1' : '0.9'});
        transform: scale(1.006);
        z-index: -3;
      }

      .left-panel::before {
        content: "";
        position: absolute;
        inset: 0;
        background:
          linear-gradient(90deg, ${theme === 'light' ? 'rgba(8,13,24,0.38)' : 'rgba(2,6,23,0.58)'} 0%, rgba(2,6,23,0.28) 48%, rgba(2,6,23,0.06) 100%),
          radial-gradient(circle at 20% 18%, rgba(255,255,255,0.18), transparent 30%),
          linear-gradient(180deg, rgba(2,6,23,0.1), rgba(2,6,23,0.22));
        pointer-events: none;
        z-index: -2;
      }

      .left-panel::after {
        content: "";
        position: absolute;
        inset: 0;
        background:
          repeating-linear-gradient(100deg, rgba(255,255,255,0.035) 0px, rgba(255,255,255,0.035) 1px, transparent 1px, transparent 7px),
          linear-gradient(180deg, transparent 0%, rgba(2,6,23,0.18) 100%);
        mix-blend-mode: soft-light;
        opacity: ${theme === 'light' ? '0.38' : '0.52'};
        pointer-events: none;
        z-index: -1;
      }

      .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 1;
      }

      .brand-icon {
        width: 36px;
        height: 36px;
        border-radius: 9px;
        background: rgba(255,255,255,0.18);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 15px;
        font-weight: 800;
        letter-spacing: -0.5px;
        border: 1px solid rgba(255,255,255,0.22);
        box-shadow: 0 12px 30px rgba(2, 6, 23, 0.18);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
      }

      .brand-title {
        font-size: 15px;
        font-weight: 700;
        letter-spacing: -0.2px;
        color: #FFFFFF;
        margin: 0;
        text-shadow: 0 1px 18px rgba(2,6,23,0.22);
      }

      .brand-sub {
        font-size: 11px;
        color: rgba(255,255,255,0.74);
        font-weight: 500;
        margin: 0;
      }

      .left-content {
        max-width: 430px;
        margin-top: auto;
        margin-bottom: auto;
        z-index: 1;
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 18px;
        padding: clamp(22px, 3vw, 34px);
        background: rgba(2,6,23,0.22);
        box-shadow:
          0 24px 80px rgba(2,6,23,0.22),
          inset 0 1px 0 rgba(255,255,255,0.16);
      }

      .headline {
        font-size: clamp(30px, 3.4vw, 42px);
        line-height: 1.14;
        font-weight: 700;
        letter-spacing: -0.6px;
        color: #FFFFFF;
        margin: 0 0 14px 0;
        text-shadow: 0 16px 44px rgba(2,6,23,0.34);
      }

      .headline span {
        color: rgba(255,255,255,0.82);
      }

      .subtext {
        font-size: 14.5px;
        line-height: 1.65;
        color: rgba(255,255,255,0.78);
        margin: 0;
      }

      .left-footer {
        z-index: 1;
      }

      /* RIGHT PANEL (Clean Compact Authentication) */
      .right-panel {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 40px;
        position: relative;
        background: ${theme === 'light' ? '#F8FAFC' : '#020617'};
        transition: background-color 0.2s ease;
      }

      .login-card {
        width: 100%;
        max-width: 400px;
        background: ${theme === 'light' ? '#FFFFFF' : '#0F172A'};
        border: 1px solid ${c.border};
        border-radius: 14px;
        padding: 32px;
        box-shadow: 
          0 20px 45px rgba(15, 23, 42, ${theme === 'light' ? '0.055' : '0.28'}),
          0 1px 3px rgba(0, 0, 0, 0.01);
        transition: background-color 0.2s ease, border-color 0.2s ease;
      }

      .signin-header {
        margin-bottom: 28px;
      }

      .signin-title {
        font-size: 22px;
        font-weight: 700;
        letter-spacing: -0.4px;
        color: ${theme === 'light' ? '#0F172A' : '#F8FAFC'};
        margin: 0;
      }

      .signin-sub {
        font-size: 13px;
        color: ${theme === 'light' ? '#64748B' : '#94A3B8'};
        margin-top: 6px;
      }

      /* ROLE TABS (Calm, highly polished selector) */
      .role-switch {
        display: flex;
        background: ${theme === 'light' ? '#F1F5F9' : '#1E293B'};
        padding: 3px;
        border-radius: 8px;
        gap: 1px;
        margin-bottom: 24px;
      }

      .role-btn {
        flex: 1;
        height: 32px;
        border: none;
        border-radius: 6px;
        background: transparent;
        color: ${theme === 'light' ? '#64748B' : '#94A3B8'};
        font-size: 12.5px;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        transition: all 0.15s ease;
      }

      .role-btn:hover {
        color: ${theme === 'light' ? '#0F172A' : '#F8FAFC'};
      }

      .role-btn.active {
        background: ${theme === 'light' ? '#FFFFFF' : '#0F172A'};
        color: #6366F1;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
      }

      /* FORM & INPUTS */
      .form-group {
        margin-bottom: 18px;
      }

      .label {
        display: block;
        font-size: 11px;
        font-weight: 600;
        color: ${theme === 'light' ? '#475569' : '#CBD5E1'};
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .input-wrap {
        position: relative;
        display: flex;
        align-items: center;
        width: 100%;
        height: 44px;
        border-radius: 8px;
        border: 1px solid ${theme === 'light' ? '#DDE5EE' : '#334155'};
        background: ${theme === 'light' ? '#FFFFFF' : '#0B1220'};
        box-shadow: inset 0 1px 0 rgba(255,255,255,${theme === 'light' ? '0.7' : '0.03'});
        transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
      }

      .input-icon {
        flex: 0 0 38px;
        margin-left: 8px;
        width: 26px;
        height: 26px;
        border-radius: 6px;
        color: ${theme === 'light' ? '#64748B' : '#94A3B8'};
        background: ${theme === 'light' ? '#F8FAFC' : '#111827'};
        border: 1px solid ${theme === 'light' ? '#EEF2F7' : '#243244'};
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: none;
      }

      .input {
        flex: 1 1 auto;
        min-width: 0;
        height: 100%;
        border: 0;
        background: transparent;
        color: ${theme === 'light' ? '#0F172A' : '#F8FAFC'};
        padding: 0 12px 0 0;
        font-size: 13.5px;
        font-weight: 500;
        line-height: 44px;
        outline: none;
      }

      .input-wrap:focus-within {
        border-color: #6366F1;
        background: ${theme === 'light' ? '#FFFFFF' : '#0F172A'};
        box-shadow:
          0 0 0 3px rgba(99, 102, 241, ${theme === 'light' ? '0.11' : '0.18'}),
          0 10px 22px rgba(15, 23, 42, ${theme === 'light' ? '0.04' : '0.18'});
      }

      .input-wrap:focus-within .input-icon {
        color: #6366F1;
        border-color: rgba(99, 102, 241, 0.22);
        background: ${theme === 'light' ? '#F5F7FF' : 'rgba(99,102,241,0.1)'};
      }

      .input::placeholder {
        color: ${theme === 'light' ? '#94A3B8' : '#64748B'};
        font-weight: 500;
      }

      .input.password-input {
        padding-right: 8px;
      }

      .pw-toggle {
        flex: 0 0 34px;
        margin-right: 7px;
        border: none;
        background: transparent;
        cursor: pointer;
        color: ${theme === 'light' ? '#94A3B8' : '#64748B'};
        display: flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        border-radius: 6px;
        transition: all 0.15s ease;
      }

      .pw-toggle:hover {
        color: ${theme === 'light' ? '#475569' : '#CBD5E1'};
        background: ${theme === 'light' ? '#F1F5F9' : '#1E293B'};
      }

      .extra {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12.5px;
        margin-top: 14px;
      }

      .remember {
        display: flex;
        align-items: center;
        gap: 6px;
        color: ${theme === 'light' ? '#64748B' : '#94A3B8'};
        cursor: pointer;
        user-select: none;
      }

      .remember input {
        accent-color: #6366F1;
        width: 13px;
        height: 13px;
        border-radius: 3px;
      }

      .forgot {
        color: #6366F1;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.15s ease;
      }

      .forgot:hover {
        color: #4F46E5;
      }

      .submit-btn {
        width: 100%;
        height: 38px;
        background: #6366F1;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 13.5px;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        margin-top: 22px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        transition: all 0.15s ease;
      }

      .submit-btn:hover {
        background: #4F46E5;
      }

      .submit-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      /* THEME TOGGLE (Subtle, Notion-like) */
      .theme-toggle {
        position: absolute;
        top: 24px;
        right: 24px;
        width: 32px;
        height: 32px;
        border-radius: 6px;
        border: 1px solid ${theme === 'light' ? '#E2E8F0' : '#334155'};
        background: ${theme === 'light' ? '#FFFFFF' : '#0F172A'};
        color: ${theme === 'light' ? '#64748B' : '#94A3B8'};
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.15s ease;
      }

      .theme-toggle:hover {
        background: ${theme === 'light' ? '#F1F5F9' : '#1E293B'};
        color: ${theme === 'light' ? '#0F172A' : '#F8FAFC'};
      }

      /* DEMO CREDENTIALS BOX */
      .demo-box {
        margin-top: 28px;
        background: ${theme === 'light' ? '#F8FAFC' : '#111827'};
        border: 1px solid ${theme === 'light' ? '#E2E8F0' : '#1E293B'};
        border-radius: 8px;
        padding: 14px;
      }

      .demo-title {
        font-size: 11px;
        font-weight: 700;
        color: ${theme === 'light' ? '#475569' : '#CBD5E1'};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0 0 10px 0;
      }

      .demo-row {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        margin-bottom: 5px;
      }

      .demo-row:last-child {
        margin-bottom: 0;
      }

      .demo-key {
        color: ${theme === 'light' ? '#64748B' : '#94A3B8'};
      }

      .demo-value {
        color: ${theme === 'light' ? '#0F172A' : '#CBD5E1'};
        font-weight: 600;
      }

      .demo-btn {
        width: 100%;
        height: 28px;
        background: transparent;
        border: 1px dashed ${theme === 'light' ? '#CBD5E1' : '#334155'};
        border-radius: 5px;
        color: #6366F1;
        font-size: 11px;
        font-weight: 600;
        cursor: pointer;
        margin-top: 10px;
        transition: all 0.15s ease;
      }

      .demo-btn:hover {
        background: ${theme === 'light' ? 'rgba(99, 102, 241, 0.04)' : 'rgba(99, 102, 241, 0.08)'};
        border-color: #6366F1;
      }

      .error {
        margin-top: 14px;
        background: ${theme === 'light' ? '#FEF2F2' : '#450A0A'};
        border: 1px solid ${theme === 'light' ? '#FCA5A5' : '#7F1D1D'};
        color: ${theme === 'light' ? '#991B1B' : '#FCA5A5'};
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 6px;
      }

      .spinner {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-top-color: white;
        animation: spin 0.6s linear infinite;
      }

      @keyframes spin {
        to { transform: rotate(360deg); }
      }

      /* RESPONSIVENESS */
      @media (max-width: 980px) {
        .login-container {
          grid-template-columns: 1fr;
        }

        .left-panel {
          display: none;
        }

        .right-panel {
          padding: 24px;
          min-height: 100vh;
        }
      }
      `}</style>

      <div className="login-root">
        <div className="login-container">
          
          {/* LEFT */}
          <div className="left-panel">
            <img
              src={loginGraphic}
              alt=""
              aria-hidden="true"
              className="left-bg-img"
            />
            <div className="brand">
              <div className="brand-icon">
                HR
              </div>
              <div>
                <h2 className="brand-title">HRMS Portal</h2>
                <p className="brand-sub">Workforce Management Platform</p>
              </div>
            </div>

            <div className="left-content">
              <h1 className="headline">
                Workforce clarity,
                <br />
                <span>beautifully controlled.</span>
              </h1>
              <p className="subtext">
                A calm, secure command center for attendance, payroll,
                onboarding, approvals, and every employee moment.
              </p>
            </div>

            <div className="left-footer">
              <p style={{ fontSize: '11px', color: 'rgba(255,255,255,0.66)', margin: 0, fontWeight: 500, textShadow: '0 1px 14px rgba(2,6,23,0.35)' }}>
                (c) 2026 HRMS Portal. All rights reserved.
              </p>
            </div>
          </div>

          {/* RIGHT */}
          <div className="right-panel">
            
            <button
              className="theme-toggle"
              onClick={handleThemeToggle}
              aria-label="Toggle theme"
              type="button"
            >
              {theme === "light" ? (
                <Moon size={16} />
              ) : (
                <Sun size={16} />
              )}
            </button>

            <div className="login-card">
              
              <div className="signin-header">
                <h2 className="signin-title">Welcome back</h2>
                <p className="signin-sub">Enter your credentials to continue</p>
              </div>

              <div className="role-switch">
                {ROLES.map(({ value, label, icon }) => (
                  <button
                    key={value}
                    onClick={() => switchRole(value)}
                    className={`role-btn ${role === value ? "active" : ""}`}
                    type="button"
                  >
                    {icon}
                    <span>{label}</span>
                  </button>
                ))}
              </div>

              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="label">Email Address</label>
                  <div className="input-wrap">
                    <div className="input-icon">
                      <Mail size={15} />
                    </div>
                    <input
                      type="email"
                      className="input"
                      placeholder="name@company.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="label">Password</label>
                  <div className="input-wrap">
                    <div className="input-icon">
                      <Lock size={15} />
                    </div>
                    <input
                      type={showPassword ? "text" : "password"}
                      className="input password-input"
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                    <button
                      type="button"
                      className="pw-toggle"
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? <Eye size={15} /> : <EyeOff size={15} />}
                    </button>
                  </div>
                </div>

                <div className="extra">
                  <label className="remember">
                    <input type="checkbox" />
                    <span>Remember me</span>
                  </label>
                  <a href="#" className="forgot">Forgot password?</a>
                </div>

                {error && (
                  <div className="error">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{error}</span>
                  </div>
                )}

                <button
                  type="submit"
                  className="submit-btn"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <div className="spinner" />
                      <span>Signing in...</span>
                    </>
                  ) : (
                    <>
                      <span>Sign In</span>
                      <ArrowRight size={15} />
                    </>
                  )}
                </button>
              </form>

              <div className="demo-box">
                <h3 className="demo-title">Demo Credentials</h3>
                <div className="demo-row">
                  <span className="demo-key">Email</span>
                  <span className="demo-value">{DEMO[role].email}</span>
                </div>
                <div className="demo-row">
                  <span className="demo-key">Password</span>
                  <span className="demo-value">{DEMO[role].password}</span>
                </div>
                <button
                  className="demo-btn"
                  onClick={fillDemo}
                  type="button"
                >
                  Auto Fill Credentials
                </button>
              </div>

            </div>

          </div>

        </div>
      </div>
    </>
  );
}
