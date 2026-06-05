import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { setGlobalTheme } from '../lib/theme';

export type ThemeMode = 'light' | 'dark' | 'system';
export type ModuleKey = 'dashboard' | 'employees' | 'attendance' | 'leave' | 'payroll' | 'documents' | 'forms' | 'ai' | 'biometric' | 'lifecycle' | 'settings' | 'canteen' | 'profile';
export type ModuleView = 'employee' | 'admin';
export type PageId = 'dashboard' | 'my-profile';
export type Portal = 'hrms' | 'ess';

/** Modules visible in the ESS (Employee Self-Service) portal */
export const ESS_MODULES: ModuleKey[] = ['dashboard', 'profile', 'attendance', 'leave', 'documents', 'payroll'];

interface UIState {
  activeModule: ModuleKey;
  panelOpen: boolean;
  currentPage: PageId;
  theme: ThemeMode;
  commandPaletteOpen: boolean;
  aiAssistantOpen: boolean;
  moduleViews: Partial<Record<ModuleKey, ModuleView>>;
  portal: Portal;
  /** Employee code to pre-select when navigating to Employees module */
  selectedEmployeeCode: string | null;
  setTheme: (theme: ThemeMode) => void;
  openModule: (module: ModuleKey) => void;
  closeModule: () => void;
  navigateTo: (page: PageId) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  setAiAssistantOpen: (open: boolean) => void;
  setModuleView: (module: ModuleKey, view: ModuleView) => void;
  setPortal: (portal: Portal) => void;
  setSelectedEmployeeCode: (code: string | null) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      activeModule: 'employees',
      panelOpen: false,
      currentPage: 'dashboard' as PageId,
      theme: 'system',
      commandPaletteOpen: false,
      aiAssistantOpen: false,
      moduleViews: { employees: 'admin', attendance: 'admin', leave: 'employee' },
      portal: 'hrms',
      selectedEmployeeCode: null,
      setTheme: (theme) => {
        if (theme === 'light' || theme === 'dark') setGlobalTheme(theme);
        set({ theme });
      },
      openModule: (module) => set({ activeModule: module, panelOpen: true, currentPage: 'dashboard' }),
      closeModule: () => set({ panelOpen: false, currentPage: 'dashboard' }),
      navigateTo: (page) => set({ currentPage: page, panelOpen: false }),
      setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
      setAiAssistantOpen: (open) => set({ aiAssistantOpen: open }),
      setModuleView: (module, view) => set((state) => ({ moduleViews: { ...state.moduleViews, [module]: view } })),
      setSelectedEmployeeCode: (code) => set({ selectedEmployeeCode: code }),
      setPortal: (portal) => set((state) => ({
        portal,
        // Switch to a valid default module when entering ESS
        activeModule: portal === 'ess'
          ? (ESS_MODULES.includes(state.activeModule) ? state.activeModule : 'leave')
          : state.activeModule,
        panelOpen: false,
        currentPage: 'dashboard',
      })),
    }),
    {
      name: 'hrms-ui-state',
      version: 3,
      partialize: (state) => ({
        activeModule: state.activeModule,
        theme: state.theme,
        moduleViews: state.moduleViews,
        portal: state.portal,
      }),
      migrate: (persistedState) => {
        const state = persistedState as Partial<UIState> | undefined;

        return {
          activeModule: state?.activeModule ?? 'employees',
          panelOpen: false,
          theme: state?.theme ?? 'system',
          commandPaletteOpen: false,
          aiAssistantOpen: false,
          moduleViews: state?.moduleViews ?? { employees: 'admin', attendance: 'admin', leave: 'employee' },
          portal: state?.portal ?? 'hrms',
        } satisfies Pick<UIState, 'activeModule' | 'panelOpen' | 'theme' | 'commandPaletteOpen' | 'aiAssistantOpen' | 'moduleViews' | 'portal'>;
      }
    }
  )
);
