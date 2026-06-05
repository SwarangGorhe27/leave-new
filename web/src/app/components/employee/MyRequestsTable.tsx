import React, { useEffect, useMemo, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../../store';
import { RequestStatusBadge } from './RequestStatusBadge';
import { fetchRequests, createRequest, updateRequest, withdrawRequest } from '../../../store/slices/requestSlice';
import { useAuth } from '../../context/AuthContext';

type ChangeInput = { fieldName: string; fieldLabel?: string; oldValue?: string; newValue?: string };

export function MyRequestsTable() {
  const dispatch = useDispatch();
  const { user } = useAuth();
  const employeeId = user?.employeeId ?? '1';

  const allRequests = useSelector((state: RootState) => state.requests.requests);
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all');
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<any | null>(null);
  const [changes, setChanges] = useState<ChangeInput[]>([{ fieldName: '', fieldLabel: '', oldValue: '', newValue: '' }]);
  const [sectionLabel, setSectionLabel] = useState('Profile');

  useEffect(() => {
    dispatch(fetchRequests(employeeId) as any);
  }, [dispatch, employeeId]);

  const requests = useMemo(() => {
    return allRequests.filter(r => {
      if (statusFilter !== 'all' && r.status !== statusFilter) return false;
      if (!query) return true;
      const q = query.toLowerCase();
      if (r.sectionLabel.toLowerCase().includes(q)) return true;
      if (r.changes.some((c: any) => String(c.fieldLabel || c.fieldName).toLowerCase().includes(q))) return true;
      return false;
    });
  }, [allRequests, statusFilter, query]);

  const resetForm = () => {
    setEditing(null);
    setChanges([{ fieldName: '', fieldLabel: '', oldValue: '', newValue: '' }]);
    setSectionLabel('Profile');
    setShowForm(false);
  };

  const handleAddChange = () => setChanges(c => [...c, { fieldName: '', fieldLabel: '', oldValue: '', newValue: '' }]);
  const handleRemoveChange = (i: number) => setChanges(c => c.filter((_, idx) => idx !== i));

  const handleSubmit = async () => {
    const payloadBase = {
      employeeId,
      section: 'profile',
      sectionLabel,
      changes: changes.map(ch => ({ fieldName: ch.fieldName, fieldLabel: ch.fieldLabel || ch.fieldName, oldValue: ch.oldValue, newValue: ch.newValue })),
    } as any;

    if (editing) {
      const updated = { ...editing, ...payloadBase };
      await dispatch(updateRequest(updated) as any);
    } else {
      await dispatch(createRequest(payloadBase) as any);
    }
    dispatch(fetchRequests(employeeId) as any);
    resetForm();
  };

  const handleEdit = (req: any) => {
    setEditing(req);
    setSectionLabel(req.sectionLabel || 'Profile');
    setChanges(req.changes.map((c: any) => ({ fieldName: c.fieldName, fieldLabel: c.fieldLabel, oldValue: String(c.oldValue || ''), newValue: String(c.newValue || '') })));
    setShowForm(true);
  };

  const handleWithdraw = async (id: string) => {
    if (!confirm('Withdraw this request?')) return;
    await dispatch(withdrawRequest({ requestId: id }) as any);
    dispatch(fetchRequests(employeeId) as any);
  };

  // Always render the UI; show placeholder when no requests exist.

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <button onClick={() => setShowForm(true)} className="px-3 py-1.5 bg-primary text-white rounded">New Request</button>
        <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search requests" className="px-3 py-1 rounded border border-border" />
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value as any)} className="px-3 py-1 rounded border border-border">
          <option value="all">All</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      {showForm && (
        <div className="rounded-lg border border-border bg-card p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold">{editing ? 'Edit Request' : 'New Profile Update Request'}</h3>
            <div className="flex items-center gap-2">
              <button onClick={resetForm} className="text-sm text-muted-foreground">Cancel</button>
              <button onClick={handleSubmit} className="px-3 py-1.5 bg-primary text-white rounded text-sm">Submit</button>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input value={sectionLabel} onChange={e => setSectionLabel(e.target.value)} placeholder="Section (e.g. Bank / Education)" className="px-3 py-2 border border-border rounded" />
            <div />
          </div>
          <div className="mt-3 space-y-2">
            {changes.map((ch, i) => (
              <div key={i} className="grid grid-cols-1 md:grid-cols-4 gap-2">
                <input value={ch.fieldLabel} onChange={e => setChanges(s => s.map((it, idx) => idx === i ? { ...it, fieldLabel: e.target.value } : it))} placeholder="Field label" className="px-2 py-1 border border-border rounded" />
                <input value={ch.oldValue} onChange={e => setChanges(s => s.map((it, idx) => idx === i ? { ...it, oldValue: e.target.value } : it))} placeholder="Old value" className="px-2 py-1 border border-border rounded" />
                <input value={ch.newValue} onChange={e => setChanges(s => s.map((it, idx) => idx === i ? { ...it, newValue: e.target.value } : it))} placeholder="New value" className="px-2 py-1 border border-border rounded" />
                <div className="flex items-center gap-2">
                  <button onClick={() => handleRemoveChange(i)} className="text-sm text-destructive">Remove</button>
                </div>
              </div>
            ))}
            <div>
              <button onClick={handleAddChange} className="text-sm text-primary">+ Add field</button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-3">
        {requests.map(req => (
          <div key={req.id} className="rounded-lg border border-border bg-card p-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3">
                  <h4 className="font-bold">{req.sectionLabel}</h4>
                  <RequestStatusBadge status={req.status} />
                  <span className="text-xs text-muted-foreground">{new Date(req.createdAt).toLocaleString()}</span>
                </div>
                <p className="text-sm text-muted-foreground mt-2">{req.changes.map((c: any) => c.fieldLabel).join(', ')}</p>
              </div>
              <div className="flex items-center gap-2">
                {req.status === 'pending' && (
                  <>
                    <button onClick={() => handleEdit(req)} className="text-sm px-2 py-1 border border-border rounded">Edit</button>
                    <button onClick={() => handleWithdraw(req.id)} className="text-sm px-2 py-1 border border-border rounded text-destructive">Withdraw</button>
                  </>
                )}
              </div>
            </div>

            <details className="mt-3">
              <summary className="text-sm text-muted-foreground cursor-pointer">Details</summary>
              <div className="mt-2 space-y-2">
                {req.changes.map((c: any, i: number) => (
                  <div key={i} className="grid grid-cols-3 gap-2 items-center">
                    <div className="font-medium">{c.fieldLabel || c.fieldName}</div>
                    <div className="text-sm text-muted-foreground">{String(c.oldValue ?? '-')}</div>
                    <div className="text-sm text-foreground">{String(c.newValue ?? '-')}</div>
                  </div>
                ))}
                {req.rejectionComment && <div className="text-sm text-destructive">Admin: {req.rejectionComment}</div>}
              </div>
            </details>
          </div>
        ))}
      </div>
    </div>
  );
}
