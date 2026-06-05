import React, { createContext, useContext, useEffect, useState } from "react";
import {
  applyTheme,
  persistTheme,
  readPersistedTheme,
  setGlobalTheme,
  THEME_EVENT_NAME,
} from "../../lib/theme";

interface ThemeContextType {
  isDark: boolean;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  isDark: false,
  toggleTheme: () => {},
});

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [isDark, setIsDark] = useState(() => readPersistedTheme() === "dark");

  useEffect(() => {
    const theme = isDark ? "dark" : "light";
    applyTheme(theme);
    persistTheme(theme);
  }, [isDark]);

  useEffect(() => {
    const handleStorage = (event: StorageEvent) => {
      if (event.key === "hrms_theme" || event.key === "hrms-ui-state") {
        setIsDark(readPersistedTheme() === "dark");
      }
    };

    const handleThemeChange = (event: Event) => {
      const theme = (event as CustomEvent<"light" | "dark">).detail;
      if (theme === "light" || theme === "dark") setIsDark(theme === "dark");
    };

    window.addEventListener("storage", handleStorage);
    window.addEventListener(THEME_EVENT_NAME, handleThemeChange);
    return () => {
      window.removeEventListener("storage", handleStorage);
      window.removeEventListener(THEME_EVENT_NAME, handleThemeChange);
    };
  }, []);

  const toggleTheme = () =>
    setIsDark((prev) => {
      const next = !prev;
      setGlobalTheme(next ? "dark" : "light");
      return next;
    });

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
