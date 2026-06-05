import { useEffect } from 'react';
import { useUIStore } from '@store/uiStore';

export function useCommandPalette() {
  const open = useUIStore((state) => state.commandPaletteOpen);
  const setOpen = useUIStore((state) => state.setCommandPaletteOpen);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const isShortcut = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k';
      if (isShortcut) {
        event.preventDefault();
        setOpen(!useUIStore.getState().commandPaletteOpen);
      }
      if (event.key === 'Escape') {
        setOpen(false);
      }
    };

    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [setOpen]);

  return { open, setOpen };
}
