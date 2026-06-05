import type { HTMLAttributes } from 'react';
import { cn, getInitials } from '@utils/utils';

const initialsClasses = [
  'bg-brand-500/90 text-white',
  'bg-sky-500/90 text-white',
  'bg-emerald-500/90 text-white',
  'bg-amber-500/90 text-white',
  'bg-violet-500/90 text-white',
  'bg-fuchsia-500/90 text-white',
  'bg-cyan-500/90 text-white',
  'bg-rose-500/90 text-white'
] as const;

const sizes = {
  xs: 'h-5 w-5 text-[9px]',
  sm: 'h-6 w-6 text-[10px]',
  md: 'h-8 w-8 text-xs',
  lg: 'h-10 w-10 text-sm',
  xl: 'h-12 w-12 text-base',
  '2xl': 'h-16 w-16 text-lg'
} as const;

const statusClasses = {
  online: 'bg-success-500',
  away: 'bg-warning-500',
  offline: 'bg-surface-400',
  busy: 'bg-danger-500'
} as const;

function hashName(name: string) {
  return Array.from(name).reduce((accumulator, character) => accumulator + character.charCodeAt(0), 0) % initialsClasses.length;
}

interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  name: string;
  src?: string;
  size?: keyof typeof sizes;
  status?: keyof typeof statusClasses;
}

export function Avatar({ name, src, size = 'md', status, className, ...props }: AvatarProps) {
  const tone = initialsClasses[hashName(name)];

  return (
    <div className={cn('relative inline-flex shrink-0 items-center justify-center rounded-full', sizes[size], className)} {...props}>
      {src ? (
        <img src={src} alt={name} className="h-full w-full rounded-full object-cover" />
      ) : (
        <div className={cn('flex h-full w-full items-center justify-center rounded-full font-semibold', tone)}>{getInitials(name)}</div>
      )}
      {status ? (
        <span className={cn('absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-white dark:border-[var(--surface-100)]', statusClasses[status])} />
      ) : null}
    </div>
  );
}

interface AvatarGroupProps {
  items: Array<Pick<AvatarProps, 'name' | 'src' | 'status'>>;
  max?: number;
  size?: keyof typeof sizes;
}

export function AvatarGroup({ items, max = 4, size = 'md' }: AvatarGroupProps) {
  const visible = items.slice(0, max);
  const overflow = Math.max(0, items.length - visible.length);

  return (
    <div className="flex items-center">
      {visible.map((item, index) => (
        <Avatar
          key={`${item.name}-${index}`}
          name={item.name}
          src={item.src}
          status={item.status}
          size={size}
          className={cn(index > 0 ? '-ml-2 ring-2 ring-white dark:ring-[var(--surface-100)]' : '')}
        />
      ))}
      {overflow > 0 ? (
        <span className="-ml-2 inline-flex h-8 w-8 items-center justify-center rounded-full border-2 border-white bg-surface-100 text-xs font-semibold text-surface-700 dark:border-[var(--surface-100)] dark:bg-white/5 dark:text-white/70">
          +{overflow}
        </span>
      ) : null}
    </div>
  );
}
