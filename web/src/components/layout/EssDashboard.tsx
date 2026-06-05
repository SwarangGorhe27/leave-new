import {
  ChevronRight,
  UserCheck,
  Sparkles,
} from 'lucide-react';

import React from 'react';
import { useAuthStore } from '@store/authStore';

/* ------------------------------------------------------------------ */
/* Greeting */
/* ------------------------------------------------------------------ */
function greeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

/* ------------------------------------------------------------------ */
/* Check In / Out */
/* ------------------------------------------------------------------ */
function CheckInOutPanel() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <div className="flex items-center justify-between rounded-2xl border bg-white px-4 py-3 shadow-sm dark:bg-[#161B26]">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 flex items-center justify-center rounded-xl bg-emerald-100 text-emerald-600">
            <UserCheck />
          </div>
          <div>
            <p className="text-sm font-semibold dark:text-white">Check In</p>
            <p className="text-xs text-surface-500">09:12 AM</p>
          </div>
        </div>
        <ChevronRight />
      </div>

      <div className="flex items-center justify-between rounded-2xl border bg-white px-4 py-3 shadow-sm dark:bg-[#161B26]">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 flex items-center justify-center rounded-xl bg-rose-100 text-rose-600">
            <UserCheck />
          </div>
          <div>
            <p className="text-sm font-semibold dark:text-white">Check Out</p>
            <p className="text-xs text-surface-500">Not checked out</p>
          </div>
        </div>
        <ChevronRight />
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Last 3 Days */
/* ------------------------------------------------------------------ */
function Last3DaysActivity() {
  const logs = [
    { day: 'Today', time: '09:12 AM —', status: 'Working' },
    { day: 'Yesterday', time: '09:45 AM – 06:10 PM', status: 'Late Coming' },
    { day: '2 May', time: '—', status: 'Miss Punch' },
  ];

  return (
    <div className="rounded-[28px] border bg-white px-5 py-4 shadow-sm dark:bg-[#161B26]">
      <div className="mb-4 flex justify-between">
        <h3 className="text-sm font-semibold dark:text-white">
          Last 3 Days Activity
        </h3>
        <span className="text-xs text-surface-400">Logs</span>
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        {logs.map((log, i) => (
          <div key={i} className="rounded-2xl bg-surface-50 p-3 text-center dark:bg-white/5">
            <p className="font-semibold dark:text-white">{log.day}</p>
            <p className="text-xs text-surface-400">{log.time}</p>
            <p className="text-xs text-indigo-500">{log.status}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Attendance Donut */
/* ------------------------------------------------------------------ */
function AttendanceDonut() {
  const data = [
    { label: 'Present', value: 19, color: '#6366F1' },
    { label: 'Absent', value: 3, color: '#F43F5E' },
    { label: 'Leave', value: 2, color: '#FACC15' },
    { label: 'Holiday', value: 4, color: '#A855F7' },
  ];

  const total = data.reduce((s, d) => s + d.value, 0);

  let cumulative = 0;
  const segments = data.map((d) => {
    const start = (cumulative / total) * 360;
    cumulative += d.value;
    const end = (cumulative / total) * 360;
    return { ...d, start, end };
  });

  const gradient = segments
    .map((s) => `${s.color} ${s.start}deg ${s.end}deg`)
    .join(',');

  const [active, setActive] = React.useState<any>(null);

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;

    let angle = (Math.atan2(y, x) * 180) / Math.PI;
    angle = (angle + 450) % 360;

    const found = segments.find(
      (s) => angle >= s.start && angle < s.end,
    );

    setActive(found || null);
  }

  return (
    <div
      className="relative flex h-[220px] w-[220px] items-center justify-center"
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setActive(null)}
    >
      <div
        className="absolute h-[190px] w-[190px] rounded-full"
        style={{ background: `conic-gradient(${gradient})` }}
      />
      <div className="absolute h-[140px] w-[140px] rounded-full bg-white dark:bg-[#0F1117]" />

      <div className="z-10 text-center">
        {!active ? (
          <>
            <p className="text-xs text-surface-400">Total</p>
            <h1 className="text-2xl font-bold dark:text-white">{total}</h1>
          </>
        ) : (
          <>
            <p style={{ color: active.color }}>{active.label}</p>
            <h1 className="font-bold dark:text-white">{active.value}</h1>
          </>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Leave Donut */
/* ------------------------------------------------------------------ */
function LeaveDonut() {
  const data = [
    { label: 'Used', value: 8, color: '#F43F5E' },
    { label: 'Remaining', value: 12, color: '#10B981' },
  ];

  const total = data.reduce((s, d) => s + d.value, 0);

  let cumulative = 0;
  const segments = data.map((d) => {
    const start = (cumulative / total) * 360;
    cumulative += d.value;
    const end = (cumulative / total) * 360;
    return { ...d, start, end };
  });

  const gradient = segments
    .map((s) => `${s.color} ${s.start}deg ${s.end}deg`)
    .join(',');

  const [active, setActive] = React.useState<any>(null);

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;

    let angle = (Math.atan2(y, x) * 180) / Math.PI;
    angle = (angle + 450) % 360;

    const found = segments.find(
      (s) => angle >= s.start && angle < s.end,
    );

    setActive(found || null);
  }

  return (
    <div
      className="relative flex h-[220px] w-[220px] items-center justify-center"
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setActive(null)}
    >
      {/* Ring */}
      <div
        className="absolute h-[190px] w-[190px] rounded-full"
        style={{ background: `conic-gradient(${gradient})` }}
      />

      {/* Inner */}
      <div className="absolute h-[140px] w-[140px] rounded-full bg-white dark:bg-[#0F1117]" />

      {/* Center Content */}
      <div className="z-10 text-center px-2">
        {!active ? (
          <>
            <p className="text-xs text-surface-400">Total Leaves</p>
            <h1 className="mt-2 text-2xl font-bold dark:text-white">
              {total}
            </h1>
          </>
        ) : (
          <>
            <p
              className="text-xs font-semibold"
              style={{ color: active.color }}
            >
              {active.label}
            </p>

            <h1 className="mt-2 text-xl font-bold dark:text-white">
              {active.value}
            </h1>

            <p className="text-xs text-surface-400">
              {Math.round((active.value / total) * 100)}%
            </p>
          </>
        )}
      </div>
    </div>
  );
}


/* ------------------------------------------------------------------ */
/* Stats Row */
/* ------------------------------------------------------------------ */
function StatsRow() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Attendance */}
      <div className="rounded-[28px] border bg-white p-5 min-h-[390px] dark:bg-[#161B26] flex flex-col">
        <h2 className="text-sm font-bold dark:text-white">Attendance</h2>

        <div className="flex-1 flex items-center justify-center">
          <AttendanceDonut />
        </div>
      </div>

      {/* Leave */}
      <div className="rounded-[28px] border bg-white p-5 min-h-[390px] dark:bg-[#161B26] flex flex-col">
        <h2 className="text-sm font-bold dark:text-white">Leave Balance</h2>

        <div className="flex-1 flex items-center justify-center">
          <LeaveDonut />
        </div>
      </div>
    </div>
  );
}


/* ------------------------------------------------------------------ */
/* Sidebar Cards */
/* ------------------------------------------------------------------ */
function EventsCard() {
  return (
    <div className="rounded-[32px] border bg-white p-4 shadow-sm min-h-[200px] dark:bg-[#161B26] flex flex-col">
      <h2 className="text-sm font-bold dark:text-white">Events</h2>

      <div className="flex flex-1 flex-col items-center justify-center text-center">
        <Sparkles className="h-10 w-10 text-indigo-400" />
        <p className="mt-2 text-xs dark:text-white">No events</p>
      </div>
    </div>
  );
}

function UpcomingHolidayCard() {
  return (
    <div className="rounded-[32px] border bg-white p-4 shadow-sm min-h-[200px] dark:bg-[#161B26] flex flex-col">
      <h2 className="text-sm font-bold dark:text-white">Upcoming Holidays</h2>

      <div className="flex flex-1 flex-col items-center justify-center text-center">
        <Sparkles className="h-10 w-10 text-rose-400" />
        <p className="mt-2 text-xs dark:text-white">No holidays</p>
      </div>
    </div>
  );
}

function BirthdayCard() {
  return (
    <div className="rounded-[32px] border bg-white p-4 shadow-sm min-h-[200px] dark:bg-[#161B26] flex flex-col">
      <h2 className="text-sm font-bold dark:text-white">Birthdays</h2>

      <div className="flex flex-1 flex-col items-center justify-center text-center">
        <Sparkles className="h-10 w-10 text-pink-400" />
        <p className="mt-2 text-xs dark:text-white">No birthdays</p>
      </div>
    </div>
  );
}


<h2 className="text-sm font-bold dark:text-white">Birthdays</h2>
/* ------------------------------------------------------------------ */
/* MAIN */
/* ------------------------------------------------------------------ */
export function EssDashboard() {
  const user = useAuthStore((s) => s.user);

  return (
    <div className="mx-auto max-w-[1600px] px-5 pb-20 pt-5">
      <h1 className="mb-6 text-3xl font-extrabold dark:text-white">
        {greeting()}, {user?.name.split(' ')[0]} 👋
      </h1>

      <div className="grid gap-6 xl:grid-cols-[1fr_340px]">
        {/* LEFT */}
        <div className="space-y-6">
          <CheckInOutPanel />
          <Last3DaysActivity />
          <StatsRow />
        </div>

        {/* RIGHT */}
        <div className="space-y-6">
          <EventsCard />
          <UpcomingHolidayCard />
          <BirthdayCard />
        </div>
      </div>
    </div>
  );
}