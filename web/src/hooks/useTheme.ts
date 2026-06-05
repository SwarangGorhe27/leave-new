import { useEffect } from 'react';
import { useUIStore } from '@store/uiStore';
import {
  applyTheme,
  persistTheme,
  readPersistedTheme,
  THEME_EVENT_NAME,
} from '../lib/theme';

export function getResolvedTheme(theme: 'light' | 'dark' | 'system') {
  if (theme === 'system') return readPersistedTheme();
  return theme;
}

export function useTheme() {
  const theme = useUIStore((state) => state.theme);
  const setTheme = useUIStore((state) => state.setTheme);

  useEffect(() => {
    const resolved = getResolvedTheme(theme);
    applyTheme(resolved);
    persistTheme(resolved);
  }, [theme]);

  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const listener = () => {
      if (useUIStore.getState().theme === 'system') {
        applyTheme(readPersistedTheme());
      }
    };
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, []);

  useEffect(() => {
    const listener = (event: Event) => {
      const nextTheme = (event as CustomEvent<'light' | 'dark'>).detail;
      if (nextTheme === 'light' || nextTheme === 'dark') {
        useUIStore.setState({ theme: nextTheme });
      }
    };

    window.addEventListener(THEME_EVENT_NAME, listener);
    return () => window.removeEventListener(THEME_EVENT_NAME, listener);
  }, []);

  return { theme, setTheme };
}
