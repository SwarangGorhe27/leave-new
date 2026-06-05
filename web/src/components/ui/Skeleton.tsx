import type { HTMLAttributes } from 'react';
import { cn } from '@utils/utils';

export function Skeleton({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('animate-shimmer rounded-lg bg-[linear-gradient(110deg,rgba(222,226,230,0.45),rgba(248,249,250,0.9),rgba(222,226,230,0.45))] bg-[length:200%_100%] dark:bg-[linear-gradient(110deg,rgba(34,38,58,0.65),rgba(48,53,77,0.9),rgba(34,38,58,0.65))]', className)}
      {...props}
    />
  );
}

export function SkeletonText() {
  return (
    <div className="space-y-2">
      <Skeleton className="h-3 w-2/3" />
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-4/5" />
    </div>
  );
}

export function SkeletonAvatar() {
  return <Skeleton className="h-10 w-10 rounded-full" />;
}

export function SkeletonCard() {
  return (
    <div className="surface-card space-y-4 p-4">
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-16 w-full" />
      <Skeleton className="h-3 w-2/3" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3 p-4">
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="grid grid-cols-6 gap-3">
          {Array.from({ length: 6 }).map((__, cellIndex) => (
            <Skeleton key={cellIndex} className="h-10 w-full rounded-xl" />
          ))}
        </div>
      ))}
    </div>
  );
}
