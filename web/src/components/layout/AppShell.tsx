import { motion, AnimatePresence } from 'framer-motion';
import { useUIStore } from '@store/uiStore';
import { useAuthStore } from '@store/authStore';
import { DockBar } from '@components/dock/DockBar';
import { TopBar } from './TopBar';
import { WorkspaceCanvas } from './WorkspaceCanvas';
import { ModulePanel } from '@components/panels/ModulePanel';
import { Dashboard } from './Dashboard';
import { EssDashboard } from './EssDashboard';
import { MyProfilePage } from '@pages/MyProfilePage';
import { SetupPasswordPage } from '@pages/SetupPasswordPage';
import { EmployeeLoginPage } from '@pages/EmployeeLoginPage';
import { AdminLoginPage } from '@pages/AdminLoginPage';
import { FloatingAIBot } from './FloatingAIBot';

export function AppShell() {
  const { panelOpen, activeModule, currentPage, portal, setPortal } = useUIStore((state) => ({
    panelOpen: state.panelOpen,
    activeModule: state.activeModule,
    currentPage: state.currentPage,
    portal: state.portal,
    setPortal: state.setPortal,
  }));
  const { user, isAuthenticated } = useAuthStore((state) => ({
    user: state.user,
    isAuthenticated: state.isAuthenticated,
  }));

  // Ensure portal state matches user role
  if (isAuthenticated) {
    if (user?.role === 'ADMIN' && portal !== 'hrms') {
      setPortal('hrms');
    } else if (user?.role === 'EMPLOYEE' && portal !== 'ess') {
      setPortal('ess');
    }
  }

  // Route: /setup-password?token=xxx — standalone page (no topbar/dock)
  if (window.location.pathname === '/setup-password') {
    return <SetupPasswordPage />;
  }

  // Protected Routes - Auth handling
  if (!isAuthenticated) {
    if (window.location.pathname === '/admin-login') {
      return <AdminLoginPage />;
    }
    return <EmployeeLoginPage />;
  }

  const isAdmin = isAuthenticated && user?.role === 'ADMIN';

  let content: React.ReactNode;
  if (panelOpen && isAdmin) {
    content = <ModulePanel />;
  } else if (currentPage === 'my-profile') {
    content = <MyProfilePage />;
  } else {
    content = user?.role === 'EMPLOYEE' ? <EssDashboard /> : <Dashboard />;
  }

  return (
    <div className="flex min-h-screen flex-col bg-surface-50 dark:bg-surface-200">
      <TopBar />
      <WorkspaceCanvas>
        <AnimatePresence mode="wait">
          <motion.div
            key={panelOpen ? activeModule : currentPage}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3, ease: [0.23, 1, 0.32, 1] }}
            className="w-full h-full"
          >
            {content}
          </motion.div>
        </AnimatePresence>
      </WorkspaceCanvas>
      
      {/* Navigation Dock - Admin & Employee */}
      {isAuthenticated && <DockBar />}
      
      <FloatingAIBot />
    </div>
  );
}
