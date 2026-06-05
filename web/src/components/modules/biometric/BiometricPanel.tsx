import { useState } from 'react';
import { Fingerprint, Plus, Wifi, WifiOff, RefreshCw, Clock, AlertTriangle, Check, X } from 'lucide-react';
import { cn } from '@utils/utils';
import {
  useBiometricDevices, useCreateBiometricDevice,
  useDeleteBiometricDevice, useSyncDevice, usePunchLogs, useSyncLogs,
  type BiometricDevice,
} from '@hooks/useBiometric';

const STATUS_CONFIG: Record<string, { label: string; icon: React.ReactNode; cls: string }> = {
  ACTIVE: { label: 'Active', icon: <Wifi className="h-3.5 w-3.5" />, cls: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 dark:text-emerald-400' },
  INACTIVE: { label: 'Inactive', icon: <WifiOff className="h-3.5 w-3.5" />, cls: 'text-surface-500 bg-surface-100 dark:bg-white/10 dark:text-white/40' },
  ERROR: { label: 'Error', icon: <AlertTriangle className="h-3.5 w-3.5" />, cls: 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400' },
  OFFLINE: { label: 'Offline', icon: <WifiOff className="h-3.5 w-3.5" />, cls: 'text-amber-600 bg-amber-50 dark:bg-amber-900/20 dark:text-amber-400' },
};

type BiometricTab = 'devices' | 'punch-logs' | 'sync-logs';

function AddDeviceForm({ onClose }: { onClose: () => void }) {
  const create = useCreateBiometricDevice();
  const [form, setForm] = useState({ name: '', device_type: 'ZKTECO', serial_number: '', ip_address: '', port: '4370', location: '' });

  const inputCls = 'w-full rounded-xl border border-surface-200 bg-surface-0 px-3 py-2 text-sm text-surface-900 placeholder-surface-400 focus:border-brand-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder-white/30';

  function handleSave() {
    create.mutate(
      { ...form, port: parseInt(form.port) || 4370, status: 'INACTIVE' as const },
      { onSuccess: onClose },
    );
  }

  return (
    <div className="rounded-2xl border border-brand-200 bg-brand-50/30 p-4 dark:border-brand-800/40 dark:bg-brand-900/10">
      <h4 className="mb-3 text-sm font-semibold text-surface-900 dark:text-white">Add Biometric Device</h4>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <input placeholder="Device name *" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} className={inputCls} />
        <select value={form.device_type} onChange={(e) => setForm((f) => ({ ...f, device_type: e.target.value }))} className={inputCls}>
          <option value="ZKTECO">ZKTeco</option>
          <option value="SUPREMA">Suprema</option>
          <option value="ESSL">eSSL</option>
          <option value="OTHER">Other</option>
        </select>
        <input placeholder="Serial number" value={form.serial_number} onChange={(e) => setForm((f) => ({ ...f, serial_number: e.target.value }))} className={inputCls} />
        <input placeholder="IP address (e.g. 192.168.1.100)" value={form.ip_address} onChange={(e) => setForm((f) => ({ ...f, ip_address: e.target.value }))} className={inputCls} />
        <input placeholder="Port (default 4370)" value={form.port} onChange={(e) => setForm((f) => ({ ...f, port: e.target.value }))} type="number" className={inputCls} />
        <input placeholder="Location / Floor" value={form.location} onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))} className={inputCls} />
      </div>
      <div className="mt-3 flex justify-end gap-2">
        <button onClick={onClose} className="rounded-xl border border-surface-200 px-4 py-2 text-sm text-surface-600 dark:border-white/10 dark:text-white/50">Cancel</button>
        <button onClick={handleSave} disabled={!form.name || create.isPending} className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
          {create.isPending ? 'Adding…' : 'Add Device'}
        </button>
      </div>
    </div>
  );
}

function DeviceCard({ device }: { device: BiometricDevice }) {
  const sync = useSyncDevice();
  const del = useDeleteBiometricDevice();
  const [confirm, setConfirm] = useState(false);
  const cfg = STATUS_CONFIG[device.status] ?? STATUS_CONFIG.OFFLINE;

  return (
    <div className="rounded-2xl border border-surface-200/70 bg-surface-0 p-4 shadow-xs dark:border-white/10 dark:bg-white/5">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-surface-100 dark:bg-white/10">
            <Fingerprint className="h-5 w-5 text-surface-500 dark:text-white/40" />
          </div>
          <div>
            <p className="font-medium text-surface-900 dark:text-white">{device.name}</p>
            <p className="text-xs text-surface-500 dark:text-white/40">{device.device_type} · {device.ip_address}:{device.port}</p>
          </div>
        </div>
        <span className={cn('flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium', cfg.cls)}>
          {cfg.icon} {cfg.label}
        </span>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-3 text-xs text-surface-500 dark:text-white/40 sm:grid-cols-4">
        <div>
          <p className="font-medium text-surface-700 dark:text-white/60">Serial</p>
          <p className="font-mono">{device.serial_number || '—'}</p>
        </div>
        <div>
          <p className="font-medium text-surface-700 dark:text-white/60">Location</p>
          <p>{device.location || '—'}</p>
        </div>
        <div>
          <p className="font-medium text-surface-700 dark:text-white/60">Last Sync</p>
          <p>{device.last_sync ? new Date(device.last_sync).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' }) : 'Never'}</p>
        </div>
        <div>
          <p className="font-medium text-surface-700 dark:text-white/60">Last Heartbeat</p>
          <p>{device.last_heartbeat ? new Date(device.last_heartbeat).toLocaleString('en-IN', { dateStyle: 'short', timeStyle: 'short' }) : 'Never'}</p>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-end gap-2">
        <button
          onClick={() => sync.mutate(device.id)}
          disabled={sync.isPending}
          className="flex items-center gap-1.5 rounded-lg border border-surface-200 px-3 py-1.5 text-xs font-medium text-surface-700 hover:border-brand-400 hover:text-brand-600 dark:border-white/10 dark:text-white/60 disabled:opacity-50"
        >
          <RefreshCw className={cn('h-3.5 w-3.5', sync.isPending && 'animate-spin')} /> Sync Now
        </button>
        {confirm ? (
          <div className="flex items-center gap-1">
            <button onClick={() => { del.mutate(device.id); setConfirm(false); }} className="rounded-lg bg-red-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-red-700">Delete</button>
            <button onClick={() => setConfirm(false)} className="rounded-lg border border-surface-200 px-2.5 py-1.5 text-xs dark:border-white/10">Cancel</button>
          </div>
        ) : (
          <button onClick={() => setConfirm(true)} className="rounded-lg border border-surface-200 px-2.5 py-1.5 text-xs text-red-600 hover:bg-red-50 dark:border-white/10 dark:hover:bg-red-900/20">Remove</button>
        )}
      </div>
    </div>
  );
}

function PunchLogsView() {
  const { data: logs = [], isLoading } = usePunchLogs();
  if (isLoading) return <div className="space-y-2 p-2">{[1,2,3,4].map(i=><div key={i} className="h-10 animate-pulse rounded-xl bg-surface-100 dark:bg-white/10"/>)}</div>;
  if (!logs.length) return <div className="flex flex-col items-center py-16"><Clock className="h-10 w-10 text-surface-300 dark:text-white/20"/><p className="mt-3 text-sm text-surface-400 dark:text-white/30">No punch logs yet.</p></div>;
  return (
    <div className="overflow-x-auto rounded-xl border border-surface-200/70 dark:border-white/10">
      <table className="w-full text-xs">
        <thead className="border-b border-surface-100 bg-surface-50 dark:border-white/5 dark:bg-white/5">
          <tr>
            {['Device ID', 'Emp Device ID', 'Punch Time', 'Processed', 'Notes'].map(h=>(
              <th key={h} className="px-3 py-2 text-left font-medium text-surface-600 dark:text-white/50">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-surface-50 dark:divide-white/5">
          {logs.map(log=>(
            <tr key={log.id} className="hover:bg-surface-50 dark:hover:bg-white/5">
              <td className="px-3 py-2 font-mono text-surface-500 dark:text-white/40">{String(log.device).slice(0,8)}…</td>
              <td className="px-3 py-2 font-semibold text-surface-800 dark:text-white/80">{log.employee_device_id}</td>
              <td className="px-3 py-2 text-surface-600 dark:text-white/60">{new Date(log.punch_time).toLocaleString('en-IN')}</td>
              <td className="px-3 py-2">
                {log.is_processed
                  ? <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400"><Check className="h-3 w-3"/> Yes</span>
                  : <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400"><X className="h-3 w-3"/> Pending</span>}
              </td>
              <td className="px-3 py-2 text-surface-400 dark:text-white/30">{log.error_message || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SyncLogsView() {
  const { data: logs = [], isLoading } = useSyncLogs();
  if (isLoading) return <div className="space-y-2">{[1,2,3].map(i=><div key={i} className="h-12 animate-pulse rounded-xl bg-surface-100 dark:bg-white/10"/>)}</div>;
  if (!logs.length) return <div className="flex flex-col items-center py-16"><RefreshCw className="h-10 w-10 text-surface-300 dark:text-white/20"/><p className="mt-3 text-sm text-surface-400 dark:text-white/30">No sync history yet.</p></div>;
  return (
    <div className="space-y-2">
      {logs.map(log=>(
        <div key={log.id} className="flex items-center gap-4 rounded-xl border border-surface-200/70 px-4 py-3 dark:border-white/10">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-surface-800 dark:text-white/80">{String(log.device).slice(0,8)}… — {log.sync_type}</p>
            <p className="text-xs text-surface-400 dark:text-white/30">{new Date(log.started_at).toLocaleString('en-IN')}</p>
          </div>
          <div className="text-xs text-right text-surface-500 dark:text-white/40">
            <p>{log.records_pulled ?? 0} pulled · {log.records_processed ?? 0} processed</p>
            <p className={cn(log.status === 'COMPLETED' ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400')}>{log.status}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

export function BiometricPanel() {
  const [tab, setTab] = useState<BiometricTab>('devices');
  const [showAdd, setShowAdd] = useState(false);
  const { data: devices = [], isLoading } = useBiometricDevices();

  const TABS: { key: BiometricTab; label: string }[] = [
    { key: 'devices', label: `Devices (${devices.length})` },
    { key: 'punch-logs', label: 'Punch Logs' },
    { key: 'sync-logs', label: 'Sync History' },
  ];

  return (
    <div className="space-y-4 p-1">
      {/* Tab strip + add */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex gap-1 rounded-xl border border-surface-200/70 bg-surface-50 p-1 dark:border-white/10 dark:bg-white/5">
          {TABS.map((t) => (
            <button key={t.key} type="button" onClick={() => setTab(t.key)}
              className={cn('rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
                tab === t.key
                  ? 'bg-surface-0 text-surface-900 shadow-sm dark:bg-white/10 dark:text-white'
                  : 'text-surface-500 hover:text-surface-800 dark:text-white/40 dark:hover:text-white/70')}>
              {t.label}
            </button>
          ))}
        </div>
        {tab === 'devices' && (
          <button onClick={() => setShowAdd(!showAdd)}
            className="flex items-center gap-1.5 rounded-xl bg-brand-600 px-3 py-2 text-xs font-medium text-white hover:bg-brand-700">
            <Plus className="h-3.5 w-3.5" /> Add Device
          </button>
        )}
      </div>

      {showAdd && tab === 'devices' && <AddDeviceForm onClose={() => setShowAdd(false)} />}

      {tab === 'devices' && (
        isLoading ? (
          <div className="space-y-3">{[1,2].map(i=><div key={i} className="h-36 animate-pulse rounded-2xl bg-surface-100 dark:bg-white/10"/>)}</div>
        ) : devices.length === 0 ? (
          <div className="flex flex-col items-center py-16 text-center">
            <Fingerprint className="h-10 w-10 text-surface-300 dark:text-white/20" />
            <p className="mt-3 text-sm font-medium text-surface-700 dark:text-white/60">No devices registered</p>
            <p className="mt-1 text-xs text-surface-400 dark:text-white/30">Add a biometric device to start syncing attendance.</p>
          </div>
        ) : (
          <div className="space-y-3">{devices.map(d => <DeviceCard key={d.id} device={d} />)}</div>
        )
      )}
      {tab === 'punch-logs' && <PunchLogsView />}
      {tab === 'sync-logs' && <SyncLogsView />}
    </div>
  );
}
