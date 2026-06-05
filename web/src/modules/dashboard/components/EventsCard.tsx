import { useState } from 'react';
import { CalendarDays, Cake, Briefcase, FileWarning, Clock, Bell, Plus } from 'lucide-react';
import { cn } from '@utils/utils';

type EventType = 'HOLIDAY' | 'BIRTHDAY' | 'DEADLINE' | 'MEETING';

interface HRTaskEvent {
  id: string;
  type: EventType;
  title: string;
  date: string; // ISO date or simple 'YYYY-MM-DD'
  time?: string;
  subtitle?: string;
  isUrgent?: boolean;
}

const MOCK_EVENTS: HRTaskEvent[] = [
  {
    id: '1',
    type: 'MEETING',
    title: 'Q3 Leadership Sync',
    date: new Date().toISOString(), // Today
    time: '02:00 PM',
    subtitle: 'Boardroom A',
    isUrgent: true,
  },
  {
    id: '2',
    type: 'DEADLINE',
    title: 'Payroll Processing',
    date: new Date(Date.now() + 86400000 * 2).toISOString(), // +2 days
    subtitle: 'Approve timesheets by EOD',
    isUrgent: true,
  },
  {
    id: '3',
    type: 'BIRTHDAY',
    title: 'Aarav Mehta',
    date: new Date(Date.now() + 86400000 * 3).toISOString(), // +3 days
    subtitle: 'Senior Product Designer',
  },
  {
    id: '4',
    type: 'HOLIDAY',
    title: 'Diwali',
    date: '2026-11-01T00:00:00.000Z',
    subtitle: 'National Holiday',
  },
  {
    id: '5',
    type: 'DEADLINE',
    title: 'Performance Reviews Due',
    date: new Date(Date.now() + 86400000 * 5).toISOString(),
    subtitle: 'Q3 Evaluations',
  },
];

type FilterType = 'ALL' | 'HOLIDAY' | 'BIRTHDAY' | 'DEADLINE';

export function EventsCard() {
  const [filter, setFilter] = useState<FilterType>('ALL');

  const filteredEvents = MOCK_EVENTS.filter((e) => {
    if (filter === 'ALL') return true;
    if (filter === 'DEADLINE' && e.type === 'MEETING') return true; // Group meetings with deadlines
    return e.type === filter;
  }).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  const getEventIcon = (type: EventType) => {
    switch (type) {
      case 'HOLIDAY':
        return <CalendarDays className="h-5 w-5 text-emerald-500" />;
      case 'BIRTHDAY':
        return <Cake className="h-5 w-5 text-pink-500" />;
      case 'DEADLINE':
        return <FileWarning className="h-5 w-5 text-rose-500" />;
      case 'MEETING':
        return <Briefcase className="h-5 w-5 text-blue-500" />;
    }
  };

  const getEventBg = (type: EventType) => {
    switch (type) {
      case 'HOLIDAY':
        return 'bg-emerald-50 dark:bg-emerald-500/10';
      case 'BIRTHDAY':
        return 'bg-pink-50 dark:bg-pink-500/10';
      case 'DEADLINE':
        return 'bg-rose-50 dark:bg-rose-500/10';
      case 'MEETING':
        return 'bg-blue-50 dark:bg-blue-500/10';
    }
  };

  const isToday = (dateString: string) => {
    const today = new Date();
    const date = new Date(dateString);
    return date.getDate() === today.getDate() && date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear();
  };

  const formatDate = (dateString: string) => {
    if (isToday(dateString)) return 'Today';

    const date = new Date(dateString);
    const diffTime = date.getTime() - new Date().getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Tomorrow';
    if (diffDays > 1 && diffDays <= 7) return `In ${diffDays} days`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-[24px] border border-surface-200/60 bg-surface-0 shadow-sm dark:border-white/10 dark:bg-surface-900/40">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-surface-200/60 p-5 dark:border-white/10">
        <div>
          <h2 className="flex items-center gap-2 text-lg font-bold text-surface-900 dark:text-white">
            <Bell className="h-5 w-5 text-brand-500" />
            Events & Reminders
          </h2>
          <p className="mt-0.5 text-xs text-surface-500 dark:text-white/50">
            Smart HR tracking for important dates
          </p>
        </div>
        <button className="flex h-8 w-8 items-center justify-center rounded-full bg-surface-100 text-surface-600 transition-colors hover:bg-brand-50 hover:text-brand-600 dark:bg-white/10 dark:text-white/60 dark:hover:bg-brand-500/20 dark:hover:text-brand-400">
          <Plus className="h-4 w-4" />
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 overflow-x-auto border-b border-surface-200/60 px-5 py-3 dark:border-white/10 scrollbar-hide">
        {(['ALL', 'DEADLINE', 'BIRTHDAY', 'HOLIDAY'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              'whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-semibold transition-all duration-200',
              filter === f
                ? 'bg-surface-900 text-white dark:bg-white dark:text-surface-900'
                : 'bg-surface-100 text-surface-600 hover:bg-surface-200 dark:bg-white/5 dark:text-white/60 dark:hover:bg-white/10'
            )}
          >
            {f === 'ALL' ? 'All' : f === 'DEADLINE' ? 'Tasks & Meetings' : f === 'BIRTHDAY' ? 'Birthdays' : 'Holidays'}
          </button>
        ))}
      </div>

      {/* Event List */}
      <div className="flex-1 overflow-y-auto p-5 space-y-3">
        {filteredEvents.length > 0 ? (
          filteredEvents.map((event) => {
            const today = isToday(event.date);
            return (
              <div
                key={event.id}
                className={cn(
                  'group relative flex items-start gap-4 rounded-2xl border p-3 transition-all hover:border-surface-300 dark:hover:border-white/20',
                  today
                    ? 'border-brand-200 bg-brand-50/30 dark:border-brand-500/30 dark:bg-brand-500/5'
                    : 'border-surface-200/60 bg-surface-0 dark:border-white/10 dark:bg-transparent'
                )}
              >
                {/* Urgent indicator line */}
                {event.isUrgent && (
                  <div className="absolute left-0 top-3 h-8 w-1 rounded-r-full bg-rose-500" />
                )}

                {/* Icon */}
                <div className={cn('flex h-12 w-12 shrink-0 items-center justify-center rounded-xl', getEventBg(event.type))}>
                  {getEventIcon(event.type)}
                </div>

                {/* Content */}
                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-2">
                    <p className="truncate text-sm font-bold text-surface-900 dark:text-white">
                      {event.title}
                    </p>
                    <span
                      className={cn(
                        'shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider',
                        today
                          ? 'bg-brand-100 text-brand-700 dark:bg-brand-500/20 dark:text-brand-400'
                          : event.isUrgent
                            ? 'bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-400'
                            : 'bg-surface-100 text-surface-600 dark:bg-white/10 dark:text-white/60'
                      )}
                    >
                      {formatDate(event.date)}
                    </span>
                  </div>

                  <p className="mt-0.5 truncate text-xs text-surface-500 dark:text-white/60">
                    {event.subtitle}
                  </p>

                  {event.time && (
                    <div className="mt-2 flex items-center gap-1.5 text-xs font-medium text-surface-600 dark:text-white/50">
                      <Clock className="h-3.5 w-3.5" />
                      {event.time}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <CalendarDays className="h-10 w-10 text-surface-200 dark:text-white/10" />
            <p className="mt-3 text-sm font-semibold text-surface-900 dark:text-white">
              No events found
            </p>
            <p className="mt-1 text-xs text-surface-500 dark:text-white/50">
              There are no upcoming events in this category.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
