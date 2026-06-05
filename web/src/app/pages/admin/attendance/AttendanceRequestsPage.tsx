import React, { useState, useMemo } from 'react';
import { Search, Download, CheckCircle, XCircle, Clock, Eye, AlertCircle, Loader2, Calendar } from 'lucide-react';
import { Input } from "../../../components/ui/input";
import { Button } from "../../../components/ui/button";
import { Badge } from "../../../components/ui/badge";
import { Sheet } from "../../../components/ui/sheet";
import { cn } from "../../../components/ui/utils";
import { toast } from "sonner";
import {
  useAttendanceRequests,
  useAttendanceRequestStats,
  useApproveAttendanceRequest,
  useRejectAttendanceRequest,
  useAttendanceFilterOptions,
} from "../../../modules/attendance/hooks";
import type { UiAttendanceRequest } from "../../../modules/attendance/mappers";

type ApprovalStatus = 'Pending' | 'Approved' | 'Rejected';
type AttendanceRequest = UiAttendanceRequest;

// --- Helper Functions ---

const getFinalStatus = (manager: ApprovalStatus, admin: ApprovalStatus) => {
  if (manager === 'Rejected') return 'Rejected';
  if (manager === 'Approved' && admin === 'Pending') return 'Pending Admin Approval';
  if (manager === 'Approved' && admin === 'Approved') return 'Fully Approved';
  if (manager === 'Approved' && admin === 'Rejected') return 'Rejected';
  return 'Pending';
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'Pending': return 'warning';
    case 'Pending Admin Approval': return 'info';
    case 'Fully Approved': return 'success';
    case 'Rejected': return 'danger';
    default: return 'neutral';
  }
};

// --- Main Component ---

export function AttendanceRequestsPage() {
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('All');
  const [filterDept, setFilterDept] = useState('All');
  const [filterStatus, setFilterStatus] = useState('All');
  
  const [selectedRequests, setSelectedRequests] = useState<Set<string>>(new Set());
  const [selectedRequestDetails, setSelectedRequestDetails] = useState<AttendanceRequest | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const { data: filterOpts } = useAttendanceFilterOptions();
  const requestQueryParams = useMemo(() => {
    const params: {
      search?: string;
      request_type?: string;
      department?: string;
      status?: string;
      final_status?: string;
    } = {
      search: search || undefined,
      request_type: filterType !== 'All' ? filterType : undefined,
      department: filterDept !== 'All' ? filterDept : undefined,
    };

    if (filterStatus === 'Pending Admin Approval') {
      params.final_status = 'pending_admin_approval';
    } else if (filterStatus === 'Fully Approved') {
      params.status = 'fully_approved';
    } else if (filterStatus === 'Rejected') {
      params.status = 'rejected';
    } else if (filterStatus === 'Pending') {
      params.status = 'pending';
    }

    return params;
  }, [search, filterType, filterDept, filterStatus]);

  const { data: requests = [], isLoading, isFetching, isError, error, refetch } =
    useAttendanceRequests(requestQueryParams);
  const { data: stats = { pending: 0, managerApproved: 0, pendingAdmin: 0, approved: 0, rejected: 0 } } =
    useAttendanceRequestStats();
  const approveMutation = useApproveAttendanceRequest();
  const rejectMutation = useRejectAttendanceRequest();
  const isRequestMutating = approveMutation.isPending || rejectMutation.isPending;

  const handleBulkAction = async (action: 'Approve' | 'Reject') => {
    const selectedIds = Array.from(selectedRequests);
    if (!selectedIds.length) return;

    try {
      const mutateFn = action === 'Approve' ? approveMutation.mutateAsync : rejectMutation.mutateAsync;
      await Promise.all(
        selectedIds.map((id) => mutateFn({ id, comment: `${action}d by admin` })),
      );
      toast.success(`${selectedIds.length} request(s) ${action.toLowerCase()}d successfully`);
      setSelectedRequests(new Set());
      refetch();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : `Failed to ${action.toLowerCase()} selected requests`);
    }
  };

  const filteredRequests = useMemo(() => {
    return requests.filter((req) => {
      const finalStatus = getFinalStatus(req.managerStatus, req.adminStatus);
      const matchStatus = filterStatus === 'All' || finalStatus === filterStatus;
      return matchStatus;
    });
  }, [requests, filterStatus]);

  // Handlers
  const toggleSelection = (id: string) => {
    const newSel = new Set(selectedRequests);
    if (newSel.has(id)) newSel.delete(id);
    else newSel.add(id);
    setSelectedRequests(newSel);
  };

  const selectAllValid = () => {
    const validIds = filteredRequests.filter(r => r.managerStatus === 'Approved' && r.adminStatus === 'Pending').map(r => r.id);
    if (selectedRequests.size === validIds.length && validIds.length > 0) {
      setSelectedRequests(new Set());
    } else {
      setSelectedRequests(new Set(validIds));
    }
  };

  const openDetails = (req: AttendanceRequest) => {
    setSelectedRequestDetails(req);
    setIsDrawerOpen(true);
  };

  const handleAction = async (req: AttendanceRequest, action: 'Approve' | 'Reject') => {
    try {
      if (action === 'Approve') {
        await approveMutation.mutateAsync({ id: req.id, comment: 'Approved by admin' });
        toast.success(`Request ${req.id} approved`);
      } else {
        await rejectMutation.mutateAsync({ id: req.id, comment: 'Rejected by admin' });
        toast.success(`Request ${req.id} rejected`);
      }
      setIsDrawerOpen(false);
      refetch();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : `Failed to ${action.toLowerCase()} request`);
    }
  };

  return (
    <div className="p-4 space-y-4 max-w-[1600px] mx-auto animate-in fade-in duration-500">
      {isError && (
        <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4" />
          {error instanceof Error ? error.message : 'Failed to load attendance requests.'}
        </div>
      )}
      {(isLoading || isFetching) && requests.length === 0 && (
        <div className="flex items-center gap-2 text-muted-foreground text-sm">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading requests…
        </div>
      )}
      
      {/* Compact Header — title + stats + filters inline */}
      <div className="bg-card border border-border rounded-xl px-4 py-3 shadow-sm space-y-3">
        {/* Row 1: Title + Filters */}
        <div className="flex flex-col md:flex-row md:items-center gap-3">
          {/* Search Box - Left Side */}
          <div className="relative w-40 flex-shrink-0">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground dark:text-muted-foreground" />
            <Input 
              value={search} 
              onChange={e => setSearch(e.target.value)} 
              placeholder="Name or ID..." 
              className="pl-8 h-8 text-xs"
            />
          </div>

          {/* Filters and Buttons - Right Side */}
          <div className="flex flex-wrap items-center gap-2 ml-auto">
            <select 
              value={filterType} 
              onChange={e => setFilterType(e.target.value)}
              className="h-8 rounded-md border border-input bg-transparent px-2 py-1 text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="All">All Types</option>
              {(filterOpts?.requestTypes ?? []).map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>

            <select 
              value={filterDept} 
              onChange={e => setFilterDept(e.target.value)}
              className="h-8 rounded-md border border-input bg-transparent px-2 py-1 text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="All">All Depts</option>
              {(filterOpts?.departments ?? []).map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>

            <select 
              value={filterStatus} 
              onChange={e => setFilterStatus(e.target.value)}
              className="h-8 rounded-md border border-input bg-transparent px-2 py-1 text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              <option value="All">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Pending Admin Approval">Pending Admin</option>
              <option value="Fully Approved">Fully Approved</option>
              <option value="Rejected">Rejected</option>
            </select>

            <Button variant="outline" className="h-8 text-xs" size="sm" onClick={() => { setSearch(''); setFilterType('All'); setFilterDept('All'); setFilterStatus('All'); }}>
              Clear
            </Button>
            <Button variant="outline" className="h-8 text-xs gap-1.5" size="sm">
              <Download className="w-3.5 h-3.5" /> Export
            </Button>
          </div>
        </div>

        {/* Row 2: Stats Inline */}
        <div className="grid grid-cols-5 gap-2 border-t border-border pt-3">
          <StatCard title="Pending" value={stats.pending} icon={Clock} color="text-orange-500" bg="bg-orange-500/10" />
          <StatCard title="Mgr Approved" value={stats.managerApproved} icon={CheckCircle} color="text-emerald-500" bg="bg-emerald-500/10" />
          <StatCard title="Pending Admin" value={stats.pendingAdmin} icon={AlertCircle} color="text-blue-500" bg="bg-blue-500/10" />
          <StatCard title="Approved" value={stats.approved} icon={CheckCircle} color="text-emerald-500" bg="bg-emerald-500/10" />
          <StatCard title="Rejected" value={stats.rejected} icon={XCircle} color="text-red-500" bg="bg-red-500/10" />
        </div>
      </div>


      {/* Bulk Actions */}
      {selectedRequests.size > 0 && (
        <div className="bg-primary/5 border border-primary/20 rounded-xl p-3 flex items-center justify-between animate-in slide-in-from-top-2">
          <span className="text-sm font-medium text-primary ml-2">{selectedRequests.size} requests selected</span>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              className="text-emerald-600 border-emerald-200 hover:bg-emerald-50"
              onClick={() => handleBulkAction('Approve')}
              disabled={isRequestMutating}
            >
              Approve Selected
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="text-red-600 border-red-200 hover:bg-red-50"
              onClick={() => handleBulkAction('Reject')}
              disabled={isRequestMutating}
            >
              Reject Selected
            </Button>
          </div>
        </div>
      )}

      {/* Table Area */}
      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="text-[10px] font-bold text-muted-foreground uppercase bg-secondary/50 border-b border-border tracking-wider">
              <tr>
                <th className="px-3 py-2 w-10">
                  <input 
                    type="checkbox" 
                    className="rounded border-input"
                    checked={filteredRequests.length > 0 && selectedRequests.size === filteredRequests.filter(r => r.managerStatus === 'Approved' && r.adminStatus === 'Pending').length}
                    onChange={selectAllValid}
                  />
                </th>
                <th className="px-3 py-2">Request ID</th>
                <th className="px-3 py-2">Employee</th>
                <th className="px-3 py-2">Type & Date</th>
                <th className="px-3 py-2">Manager Status</th>
                <th className="px-3 py-2">Final Status</th>
                <th className="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredRequests.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-3 py-8 text-center text-muted-foreground">
                    <div className="flex flex-col items-center gap-2">
                      <Search className="w-8 h-8 opacity-20" />
                      <p>No attendance requests found.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredRequests.map(req => {
                  const finalStatus = getFinalStatus(req.managerStatus, req.adminStatus);
                  const canSelect = req.managerStatus === 'Approved' && req.adminStatus === 'Pending';
                  
                  return (
                    <tr key={req.id} className="border-b border-border hover:bg-secondary/20 transition-colors">
                      <td className="px-3 py-2">
                        <input 
                          type="checkbox" 
                          className="rounded border-input disabled:opacity-50"
                          disabled={!canSelect}
                          checked={selectedRequests.has(req.id)}
                          onChange={() => toggleSelection(req.id)}
                        />
                      </td>
                      <td className="px-3 py-2 font-medium text-foreground">{req.id}</td>
                      <td className="px-3 py-2">
                        <div className="flex flex-col">
                          <span className="font-medium text-foreground">{req.employeeName}</span>
                          <span className="text-[10px] text-muted-foreground">{req.employeeId} • {req.department}</span>
                        </div>
                      </td>
                      <td className="px-3 py-2">
                        <div className="flex flex-col">
                          <span className="text-foreground">{req.requestType}</span>
                          <span className="text-[10px] text-muted-foreground inline-flex items-center gap-1 mt-0.5">
                            <Calendar className="w-3 h-3" /> {req.attendanceDate}
                          </span>
                        </div>
                      </td>
                      <td className="px-3 py-2">
                        <Badge variant={req.managerStatus === 'Approved' ? 'success' : req.managerStatus === 'Rejected' ? 'danger' : 'warning'}>
                          {req.managerStatus}
                        </Badge>
                      </td>
                      <td className="px-3 py-2">
                        <Badge variant={getStatusColor(finalStatus) as any}>
                          {finalStatus}
                        </Badge>
                      </td>
                      <td className="px-3 py-2 text-right">
                        <div className="flex justify-end items-center gap-1.5">
                          <Button variant="ghost" size="sm" className="h-7 w-7" aria-label="View request details" onClick={() => openDetails(req)}>
                            <Eye className="w-3.5 h-3.5" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="h-7 text-[10px] text-emerald-600 border-emerald-200 hover:bg-emerald-50 disabled:opacity-50"
                            disabled={req.managerStatus !== 'Approved' || req.adminStatus !== 'Pending' || isRequestMutating}
                            onClick={() => handleAction(req, 'Approve')}
                          >
                            Approve
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="h-7 text-[10px] text-red-600 border-red-200 hover:bg-red-50 disabled:opacity-50"
                            disabled={req.managerStatus !== 'Approved' || req.adminStatus !== 'Pending' || isRequestMutating}
                            onClick={() => handleAction(req, 'Reject')}
                          >
                            Reject
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Drawer */}
      <Sheet 
        open={isDrawerOpen} 
        onOpenChange={setIsDrawerOpen}
        title="Request Details"
        subtitle={selectedRequestDetails?.id}
        footer={
          selectedRequestDetails?.managerStatus === 'Approved' && selectedRequestDetails?.adminStatus === 'Pending' ? (
            <div className="flex gap-2 w-full justify-end">
              <Button variant="outline" className="border-red-200 text-red-600 hover:bg-red-50" onClick={() => handleAction(selectedRequestDetails!, 'Reject')}>
                Reject Request
              </Button>
              <Button className="bg-emerald-600 hover:bg-emerald-700 text-white" onClick={() => handleAction(selectedRequestDetails!, 'Approve')}>
                Approve Request
              </Button>
            </div>
          ) : undefined
        }
      >
        {selectedRequestDetails && (
          <div className="space-y-6">
            
            {/* Employee Info */}
            <div className="bg-secondary/30 rounded-xl p-4 border border-border">
              <h3 className="text-sm font-semibold text-foreground mb-3 uppercase tracking-wider">Employee Details</h3>
              <div className="grid grid-cols-2 gap-y-3 text-sm">
                <div>
                  <div className="text-muted-foreground text-xs mb-0.5">Name</div>
                  <div className="font-medium text-foreground">{selectedRequestDetails.employeeName}</div>
                </div>
                <div>
                  <div className="text-muted-foreground text-xs mb-0.5">Employee ID</div>
                  <div className="font-medium text-foreground">{selectedRequestDetails.employeeId}</div>
                </div>
                <div>
                  <div className="text-muted-foreground text-xs mb-0.5">Department</div>
                  <div className="font-medium text-foreground">{selectedRequestDetails.department}</div>
                </div>
                <div>
                  <div className="text-muted-foreground text-xs mb-0.5">Designation</div>
                  <div className="font-medium text-foreground">{selectedRequestDetails.designation}</div>
                </div>
              </div>
            </div>

            {/* Attendance Details */}
            <div className="bg-secondary/30 rounded-xl p-4 border border-border">
              <h3 className="text-sm font-semibold text-foreground mb-3 uppercase tracking-wider">Attendance Details</h3>
              <div className="grid grid-cols-2 gap-y-3 text-sm">
                <div>
                  <div className="text-muted-foreground text-xs mb-0.5">Date</div>
                  <div className="font-medium text-foreground flex items-center gap-1"><Calendar className="w-3 h-3" /> {selectedRequestDetails.attendanceDate}</div>
                </div>
                <div>
                  <div className="text-muted-foreground text-xs mb-0.5">Shift Timing</div>
                  <div className="font-medium text-foreground">{selectedRequestDetails.shiftTiming || '--'}</div>
                </div>
                <div>
                  <div className="text-muted-foreground text-xs mb-0.5">Punch In</div>
                  <div className="font-medium text-foreground">{selectedRequestDetails.punchIn || '--'}</div>
                </div>
                <div>
                  <div className="text-muted-foreground text-xs mb-0.5">Punch Out</div>
                  <div className="font-medium text-foreground">{selectedRequestDetails.punchOut || '--'}</div>
                </div>
                <div className="col-span-2 border-t border-border mt-1 pt-2">
                  <div className="text-muted-foreground text-xs mb-0.5">Working Hours</div>
                  <div className="font-medium text-foreground">{selectedRequestDetails.workingHours || '--'}</div>
                </div>
              </div>
            </div>

            {/* Request Details */}
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-foreground border-b border-border pb-2 uppercase tracking-wider">Request Information</h3>
              <div>
                <div className="text-xs text-muted-foreground mb-1">Request Type</div>
                <div className="text-sm font-medium text-foreground bg-secondary/50 px-3 py-2 rounded-lg border border-border/50">{selectedRequestDetails.requestType}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">Reason / Justification</div>
                <p className="text-sm text-foreground bg-secondary/50 px-3 py-2 rounded-lg border border-border/50 leading-relaxed">
                  {selectedRequestDetails.reason}
                </p>
              </div>
              <div className="pt-2">
                <Button variant="outline" size="sm" className="gap-2 w-full justify-center">
                  <Download className="w-4 h-4" /> Download Supporting Document
                </Button>
              </div>
            </div>

            {/* Workflow */}
            <div className="space-y-4 pt-2">
              <h3 className="text-sm font-semibold text-foreground border-b border-border pb-2 uppercase tracking-wider">Approval Workflow</h3>
              
              {/* Manager Step */}
              <div className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className={cn("w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white", 
                    selectedRequestDetails.managerStatus === 'Approved' ? 'bg-emerald-500' : 
                    selectedRequestDetails.managerStatus === 'Rejected' ? 'bg-red-500' : 'bg-orange-500'
                  )}>
                    {selectedRequestDetails.managerStatus === 'Approved' ? <CheckCircle className="w-5 h-5" /> :
                     selectedRequestDetails.managerStatus === 'Rejected' ? <XCircle className="w-5 h-5" /> : <Clock className="w-5 h-5" />}
                  </div>
                  <div className="w-0.5 h-full bg-border mt-2" />
                </div>
                <div className="pb-6">
                  <h4 className="text-sm font-semibold text-foreground">Manager Approval</h4>
                  <div className="text-xs mt-1">
                    Status: <Badge variant={selectedRequestDetails.managerStatus === 'Approved' ? 'success' : selectedRequestDetails.managerStatus === 'Rejected' ? 'danger' : 'warning'}>{selectedRequestDetails.managerStatus}</Badge>
                  </div>
                  {selectedRequestDetails.managerRemarks && (
                    <div className="mt-2 text-sm text-muted-foreground bg-secondary/30 p-2 rounded border border-border italic">
                      "{selectedRequestDetails.managerRemarks}"
                    </div>
                  )}
                </div>
              </div>

              {/* Admin Step */}
              <div className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className={cn("w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white", 
                    selectedRequestDetails.adminStatus === 'Approved' ? 'bg-emerald-500' : 
                    selectedRequestDetails.adminStatus === 'Rejected' ? 'bg-red-500' : 'bg-blue-500'
                  )}>
                    {selectedRequestDetails.adminStatus === 'Approved' ? <CheckCircle className="w-5 h-5" /> :
                     selectedRequestDetails.adminStatus === 'Rejected' ? <XCircle className="w-5 h-5" /> : <Clock className="w-5 h-5" />}
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-foreground">Admin Approval</h4>
                  <div className="text-xs mt-1">
                    Status: <Badge variant={selectedRequestDetails.adminStatus === 'Approved' ? 'success' : selectedRequestDetails.adminStatus === 'Rejected' ? 'danger' : 'info'}>{selectedRequestDetails.adminStatus}</Badge>
                  </div>
                  {selectedRequestDetails.adminRemarks && (
                    <div className="mt-2 text-sm text-muted-foreground bg-secondary/30 p-2 rounded border border-border italic">
                      "{selectedRequestDetails.adminRemarks}"
                    </div>
                  )}
                  {selectedRequestDetails.adminStatus === 'Pending' && selectedRequestDetails.managerStatus === 'Pending' && (
                    <div className="mt-2 text-xs text-muted-foreground">Waiting for Manager to approve first.</div>
                  )}
                </div>
              </div>

            </div>
          </div>
        )}
      </Sheet>

    </div>
  );
}

// Simple Stat Card component
function StatCard({ title, value, icon: Icon, color, bg }: { title: string, value: number, icon: any, color: string, bg: string }) {
  return (
    <div className="bg-card border border-border rounded-xl p-3 shadow-sm flex items-center gap-3 cursor-pointer hover:border-primary/50 transition-colors">
      <div className={cn("w-10 h-10 rounded-full flex items-center justify-center shrink-0", bg, color)}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-muted-foreground text-[10px] font-medium uppercase tracking-wide">{title}</p>
        <p className="text-xl font-bold text-foreground">{value}</p>
      </div>
    </div>
  );
}
