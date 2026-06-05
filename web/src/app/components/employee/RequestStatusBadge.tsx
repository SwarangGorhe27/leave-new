import React from 'react';
import { RequestStatus } from '../../modules/ess/types';

export function RequestStatusBadge({ status }: { status: RequestStatus }) {
  const colors: Record<RequestStatus, string> = {
    pending: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
    approved: 'bg-green-500/10 text-green-500 border-green-500/20',
    rejected: 'bg-red-500/10 text-red-500 border-red-500/20',
  };

  const labels: Record<RequestStatus, string> = {
    pending: 'Pending Approval',
    approved: 'Approved',
    rejected: 'Rejected',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium border ${colors[status]}`}>
      {labels[status]}
    </span>
  );
}
