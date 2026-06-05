"use client";

import * as React from "react";
import { cn } from "@utils/utils";
import { motion, AnimatePresence } from "framer-motion";

export interface DonutChartSegment {
  value: number;
  color: string; // Should be a valid CSS color (e.g., hsl(var(--primary)))
  label: string;
  [key: string]: any; // Allow other data
}

interface DonutChartProps extends React.HTMLAttributes<HTMLDivElement> {
  data: DonutChartSegment[];
  totalValue?: number;
  size?: number;
  strokeWidth?: number;
  animationDuration?: number;
  animationDelayPerSegment?: number;
  highlightOnHover?: boolean;
  centerContent?: React.ReactNode;
  /** Callback function when a segment is hovered */
  onSegmentHover?: (segment: DonutChartSegment | null) => void;
}

const DonutChart = React.forwardRef<HTMLDivElement, DonutChartProps>(
  (
    {
      data,
      totalValue: propTotalValue,
      size = 200,
      strokeWidth = 20,
      animationDuration = 1,
      animationDelayPerSegment = 0.05,
      highlightOnHover = true,
      centerContent,
      onSegmentHover,
      className,
      ...props
    },
    ref
  ) => {
    const [hoveredSegment, setHoveredSegment] =
      React.useState<DonutChartSegment | null>(null);
    const [mousePos, setMousePos] = React.useState({ x: 0, y: 0 });

    const internalTotalValue = React.useMemo(
      () =>
        propTotalValue || data.reduce((sum, segment) => sum + segment.value, 0),
      [data, propTotalValue]
    );

    const radius = size / 2 - strokeWidth / 2;
    const circumference = 2 * Math.PI * radius;
    let cumulativePercentage = 0;

    // Effect to call the onSegmentHover prop when internal state changes
    React.useEffect(() => {
      onSegmentHover?.(hoveredSegment);
    }, [hoveredSegment, onSegmentHover]);

    const handleMouseLeave = () => {
      setHoveredSegment(null);
    };

    const handleMouseMove = (e: React.MouseEvent) => {
      if (!highlightOnHover) return;
      const rect = e.currentTarget.getBoundingClientRect();
      setMousePos({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });
    };

    return (
      <div
        ref={ref}
        className={cn("relative flex items-center justify-center", className)}
        style={{ width: size, height: size }}
        onMouseLeave={handleMouseLeave}
        onMouseMove={handleMouseMove}
        {...props}
      >
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className="overflow-visible -rotate-90" // Rotate to start at 12 o'clock
        >
          {/* Base background ring */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="transparent"
            stroke="hsl(var(--border) / 0.5)" // Use theme variable for bg
            strokeWidth={strokeWidth}
          />
          
          {/* Data Segments */}
          <AnimatePresence>
            {data.map((segment, index) => {
              if (segment.value === 0) return null;

              const percentage =
                internalTotalValue === 0
                  ? 0
                  : (segment.value / internalTotalValue) * 100;
              
              const strokeDasharray = `${(percentage / 100) * circumference} ${circumference}`;
              const strokeDashoffset = (cumulativePercentage / 100) * circumference;
              
              const isActive = hoveredSegment?.label === segment.label;
              
              cumulativePercentage += percentage;

              return (
                <motion.circle
                  key={segment.label || index}
                  cx={size / 2}
                  cy={size / 2}
                  r={radius}
                  fill="transparent"
                  stroke={segment.color}
                  strokeWidth={strokeWidth}
                  strokeDasharray={strokeDasharray}
                  strokeDashoffset={-strokeDashoffset} // Negative offset to draw correctly
                  strokeLinecap="round" // Makes rounded edges
                  initial={{ opacity: 0, strokeDashoffset: circumference }}
                  animate={{ 
                    opacity: 1, 
                    strokeDashoffset: -strokeDashoffset,
                  }}
                  transition={{
                    opacity: { duration: 0.3, delay: index * animationDelayPerSegment },
                    strokeDashoffset: {
                      duration: animationDuration,
                      delay: index * animationDelayPerSegment,
                      ease: "easeOut",
                    },
                  }}
                  className={cn(
                    "origin-center transition-transform duration-200",
                    highlightOnHover && "cursor-pointer"
                  )}
                  style={{
                    filter: isActive
                      ? `drop-shadow(0px 0px 6px ${segment.color}) brightness(1.1)`
                      : 'none',
                    transform: isActive ? 'scale(1.03)' : 'scale(1)',
                    transition: "filter 0.2s ease-out, transform 0.2s ease-out",
                  }}
                  onMouseEnter={() => setHoveredSegment(segment)}
                />
              );
            })}
          </AnimatePresence>
        </svg>

        {/* Center Content */}
        {centerContent && (
          <div
            className="absolute flex flex-col items-center justify-center pointer-events-none"
            style={{
              width: size - strokeWidth * 2.5, // Ensure content fits inside
              height: size - strokeWidth * 2.5,
            }}
          >
            {centerContent}
          </div>
        )}

        {/* Floating Shadcn-style Tooltip */}
        {highlightOnHover && hoveredSegment && (
          <div
            className={cn(
              "absolute pointer-events-none z-[99] left-0 top-0",
              "border-surface-200/50 bg-surface-0 grid min-w-[10rem] items-start gap-1.5 rounded-lg border px-3 py-2 text-xs shadow-xl dark:border-white/10 dark:bg-surface-800 transition-opacity duration-150"
            )}
            style={{
              transform: `translate(calc(${mousePos.x}px - 50%), calc(${mousePos.y}px - 110%))`, // Float slightly above cursor
              willChange: "transform",
            }}
          >
            <div className="grid gap-1.5">
              <div className="flex w-full items-center gap-2">
                {/* Indicator Dot */}
                <div
                  className="shrink-0 h-2.5 w-2.5 rounded-[2px]"
                  style={{ backgroundColor: hoveredSegment.color }}
                />
                
                {/* Label & Value */}
                <div className="flex flex-1 justify-between items-center leading-none gap-4">
                  <span className="font-medium text-surface-500 dark:text-white/60">
                    {hoveredSegment.label}
                  </span>
                  <span className="font-mono font-bold tabular-nums text-surface-900 dark:text-white">
                    {hoveredSegment.value.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Optional: Teams mapping */}
              {hoveredSegment.teams && hoveredSegment.teams.length > 0 && (
                <div className="mt-1.5 border-t border-surface-200/50 dark:border-white/10 pt-2 space-y-1">
                  {hoveredSegment.teams.map((t: any) => (
                    <div key={t.name} className="flex justify-between items-center text-surface-500 dark:text-white/60">
                      <span className="truncate">{t.name}</span>
                      <span className="font-mono font-medium tabular-nums ml-4">{t.count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }
);

DonutChart.displayName = "DonutChart";

export { DonutChart };
