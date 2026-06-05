export type PersistedTheme = "light" | "dark";

export const THEME_STORAGE_KEY = "hrms_theme";
export const THEME_EVENT_NAME = "hrms-theme-change";

export function readPersistedTheme(): PersistedTheme {
  if (typeof window === "undefined") return "light";

  try {
    const saved = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (saved === "dark" || saved === "light") return saved;

    const uiState = window.localStorage.getItem("hrms-ui-state");
    if (uiState) {
      const parsed = JSON.parse(uiState);
      const storedTheme = parsed?.state?.theme;
      if (storedTheme === "dark" || storedTheme === "light") return storedTheme;
    }
  } catch {}

  return "light";
}

export function applyTheme(theme: PersistedTheme) {
  if (typeof document === "undefined") return;

  const isDark = theme === "dark";
  document.documentElement.classList.toggle("dark", isDark);
  document.body?.classList.toggle("dark", isDark);
  document.documentElement.style.colorScheme = theme;
}

export function persistTheme(theme: PersistedTheme) {
  if (typeof window === "undefined") return;

  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);

    const raw = window.localStorage.getItem("hrms-ui-state");
    if (raw) {
      const parsed = JSON.parse(raw);
      window.localStorage.setItem(
        "hrms-ui-state",
        JSON.stringify({
          ...parsed,
          state: {
            ...parsed.state,
            theme,
          },
        }),
      );
    }
  } catch {}
}

export function setGlobalTheme(theme: PersistedTheme) {
  applyTheme(theme);
  persistTheme(theme);
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(THEME_EVENT_NAME, { detail: theme }));
  }
}
