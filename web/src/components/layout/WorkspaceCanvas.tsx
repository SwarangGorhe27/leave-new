import type { ReactNode } from 'react';

interface WorkspaceCanvasProps {
  children?: ReactNode;
}

export function WorkspaceCanvas({ children }: WorkspaceCanvasProps) {
  return (
    <main className="relative flex-1 overflow-x-hidden px-4 pb-[calc(var(--dock-height)+24px)] pt-6 sm:px-6 lg:px-8">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          backgroundColor: 'var(--surface-50, #F8F9FA)',
          backgroundImage:
            "radial-gradient(circle at top right, rgba(99,102,241,0.04), transparent 32%), radial-gradient(circle, rgba(226,232,240,0.9) 1px, transparent 1px)",
          backgroundSize: '100% 100%, 24px 24px',
          backgroundPosition: '0 0, 0 0'
        }}
      />
      <div
        className="pointer-events-none absolute inset-0 hidden dark:block"
        style={{
          backgroundColor: '#0F1117',
          backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px)',
          backgroundSize: '24px 24px'
        }}
      />
      <div className="relative z-10 mx-auto max-w-[1400px]">{children}</div>
    </main>
  );
}