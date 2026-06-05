import api, { unwrap } from "./client";

export interface ApplyLeavePayload {
  leave_type_id: string;
  from_date: string;
  to_date: string;
  from_session?: string;
  to_session?: string;
  reason?: string;
}

export const applyLeave = (payload: ApplyLeavePayload) =>
  api.post(`/leave/ess/apply`, payload).then(unwrap);

export const getMyLeaves = (params?: Record<string, any>) =>
  api.get(`/leave/ess/applications`, { params }).then(unwrap);

export const getLeaveBalances = () => api.get(`/leave/ess/balance`).then(unwrap);

export const managerPending = (params?: Record<string, any>) =>
  api.get(`/leave/manager/team-applications`, { params }).then(unwrap);

export const managerApprove = (id: string, data?: any) =>
  api.post(`/leave/manager/applications/${id}/approve`, data || {}).then(unwrap);

export const managerReject = (id: string, data?: any) =>
  api.post(`/leave/manager/applications/${id}/reject`, data || {}).then(unwrap);

// Admin: leave types
export const listLeaveTypes = (params?: Record<string, any>) =>
  api.get(`/leave/admin/leave-types`, { params }).then(unwrap);

export const createLeaveType = (data: any) => api.post(`/leave/admin/leave-types`, data).then(unwrap);

export const updateLeaveType = (id: string, data: any) =>
  api.patch(`/leave/admin/leave-types/${id}`, data).then(unwrap);

export const deleteLeaveType = (id: string) => api.delete(`/leave/admin/leave-types/${id}/delete/`).then(unwrap);

export default {
  applyLeave,
  getMyLeaves,
  getLeaveBalances,
  managerPending,
  managerApprove,
  managerReject,
  listLeaveTypes,
  createLeaveType,
  updateLeaveType,
  deleteLeaveType,
};
