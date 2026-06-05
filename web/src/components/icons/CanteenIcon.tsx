import type { SVGProps } from 'react';

/**
 * Custom canteen icon — a serving cloche (food dome + tray).
 * Matches LucideIcon signature so it can be used in the DockBar.
 */
export function CanteenIcon({ size = 24, strokeWidth = 1.75, color = 'currentColor', className, ...props }: SVGProps<SVGSVGElement> & { size?: number; strokeWidth?: number; color?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
      {...props}
    >
      {/* Tray base */}
      <rect x="2" y="17" width="20" height="2.5" rx="1.25" />
      {/* Cloche dome */}
      <path d="M4 17 C4 10 8 6 12 6 C16 6 20 10 20 17" />
      {/* Dome handle knob */}
      <circle cx="12" cy="5" r="1.2" fill={color} stroke="none" />
      {/* Fork left */}
      <line x1="7.5" y1="17" x2="7.5" y2="13.5" />
      <line x1="6.5" y1="13.5" x2="6.5" y2="11.5" />
      <line x1="8.5" y1="13.5" x2="8.5" y2="11.5" />
      {/* Spoon right */}
      <path d="M16.5 17 L16.5 14 Q16.5 11.5 15 11 Q13.5 11.5 13.5 14 L13.5 17" />
    </svg>
  );
}
