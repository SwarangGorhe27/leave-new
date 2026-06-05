import { createContext, useContext } from 'react';
import type { MotionValue } from 'framer-motion';

export interface DockMotionContextValue {
  mouseX: MotionValue<number>;
}

export const DockMotionContext = createContext<DockMotionContextValue | null>(null);

export function useDockMotionContext() {
  const context = useContext(DockMotionContext);
  if (!context) {
    throw new Error('Dock motion context is not available.');
  }
  return context;
}
