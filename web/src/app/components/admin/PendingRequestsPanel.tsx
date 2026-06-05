import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Eye } from "lucide-react";
import { AppDispatch, RootState } from "../../../store";
import { fetchRequests, reviewRequest, ProfileRequest } from "../../../store/slices/requestSlice";
import { RequestStatusBadge } from "../employee/RequestStatusBadge";
import { Button } from "../ui/button";
import { ApprovalModal } from "./ApprovalModal";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "../ui/dialog";

export function PendingRequestsPanel({ employeeId }: { employeeId: string }) {
  const dispatch = useDispatch<AppDispatch>();
  const requests = useSelector((state: RootState) => state.requests.requests);
  const status = useSelector((state: RootState) => state.requests.status);

  const [selectedRequest, setSelectedRequest] = useState<ProfileRequest | null>(null);
  const [modalType, setModalType] = useState<"approve" | "reject" | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [detailRequest, setDetailRequest] = useState<ProfileRequest | null>(null);

  useEffect(() => {
    dispatch(fetchRequests(employeeId));
  }, [dispatch, employeeId]);

  const handleAction = (req: ProfileRequest, type: "approve" | "reject") => {
    setSelectedRequest(req);
    setModalType(type);
    setModalOpen(true);
  };

  const handleConfirm = (rejectionReason?: string, adminRemark?: string) => {
    if (!selectedRequest || !modalType) return;

    const finalDataObj = selectedRequest.changes.reduce((acc, curr) => {
      const keys = curr.fieldName.split(".");
      let currentLevel = acc as Record<string, unknown>;
      keys.forEach((k, idx) => {
        if (idx === keys.length - 1) {
          currentLevel[k] = curr.newValue;
        } else {
          currentLevel[k] = (currentLevel[k] as Record<string, unknown>) || {};
          currentLevel = currentLevel[k] as Record<string, unknown>;
        }
      });
      return acc;
    }, {} as Record<string, unknown>);

    dispatch(
      reviewRequest({
        requestId: selectedRequest.id,
        status: modalType === "approve" ? "approved" : "rejected",
        reviewer: "Admin",
        rejectionComment: rejectionReason,
        adminRemark,
        employeeId: selectedRequest.employeeId,
        section: selectedRequest.section,
        finalData: modalType === "approve" ? finalDataObj : undefined,
      })
    );
  };

  if (status === "loading") {
    return <div className="p-6 text-sm text-muted-foreground">Loading requests...</div>;
  }

  const employeeRequests = requests.filter((r) => r.employeeId === employeeId);

  if (employeeRequests.length === 0) {
    return (
      <div className="flex flex-col h-full bg-background p-6">
        <h2 className="text-xl font-bold mb-4 text-foreground">Profile Update Requests</h2>
        <div className="rounded-lg border border-border p-8 text-center text-muted-foreground text-sm">
          No requests found for this employee.
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-background p-6 space-y-6">
      <div>
        <h2 className="text-xl font-bold text-foreground">Profile Update Requests</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Review field-level changes submitted by the employee before they go live.
        </p>
      </div>

      <div className="space-y-4">
        {employeeRequests.map((req) => (
          <div
            key={req.id}
            className="rounded-xl border border-border bg-card shadow-sm overflow-hidden transition-shadow hover:shadow-md"
          >
            <div className="flex flex-wrap items-start justify-between gap-3 p-4 border-b border-border bg-secondary/20">
              <div className="min-w-0">
                <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Requested Field</p>
                <h3 className="font-semibold text-foreground mt-0.5">{req.sectionLabel}</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Requested on {new Date(req.createdAt).toLocaleString("en-IN")}
                </p>
              </div>
              <RequestStatusBadge status={req.status} />
            </div>

            <div className="p-4 grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
              <div>
                <p className="text-[10px] font-bold uppercase text-muted-foreground">Sample change</p>
                <p className="font-medium text-foreground mt-1 truncate">
                  {req.changes[0]?.fieldLabel || req.changes[0]?.fieldName || "—"}
                </p>
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase text-muted-foreground">Old value</p>
                <p className="text-muted-foreground mt-1 truncate">{String(req.changes[0]?.oldValue ?? "—")}</p>
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase text-muted-foreground">New value</p>
                <p className="text-foreground font-medium mt-1 truncate">{String(req.changes[0]?.newValue ?? "—")}</p>
              </div>
            </div>

            {req.status === "approved" && req.adminRemark ? (
              <div className="px-4 pb-3 text-xs text-muted-foreground">
                <span className="font-semibold text-foreground">Admin remark: </span>
                {req.adminRemark}
              </div>
            ) : null}

            {req.status === "rejected" && req.rejectionComment ? (
              <div className="mx-4 mb-4 rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2 text-xs">
                <span className="font-semibold text-red-600">Rejection: </span>
                <span className="text-muted-foreground">{req.rejectionComment}</span>
              </div>
            ) : null}

            <div className="flex flex-wrap items-center justify-end gap-2 p-4 border-t border-border bg-secondary/10">
              <Button variant="outline" size="sm" className="gap-1.5" onClick={() => setDetailRequest(req)}>
                <Eye className="w-4 h-4" />
                View Details
              </Button>
              {req.status === "pending" && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-red-600 border-red-500/30 hover:bg-red-500/10"
                    onClick={() => handleAction(req, "reject")}
                  >
                    Reject
                  </Button>
                  <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 text-white" onClick={() => handleAction(req, "approve")}>
                    Approve
                  </Button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      <Dialog open={!!detailRequest} onOpenChange={(o) => !o && setDetailRequest(null)}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Request details</DialogTitle>
            <DialogDescription>
              {detailRequest?.sectionLabel} · {detailRequest && new Date(detailRequest.createdAt).toLocaleString("en-IN")}
            </DialogDescription>
          </DialogHeader>
          {detailRequest ? (
            <table className="w-full text-sm text-left border border-border rounded-lg overflow-hidden">
              <thead className="bg-secondary/60 text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-3 py-2 border-b border-border">Requested Field</th>
                  <th className="px-3 py-2 border-b border-border">Old Value</th>
                  <th className="px-3 py-2 border-b border-border">New Value</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {detailRequest.changes.map((change, idx) => (
                  <tr key={idx} className="bg-card">
                    <td className="px-3 py-2 font-medium">{change.fieldLabel || change.fieldName}</td>
                    <td className="px-3 py-2 text-muted-foreground">{String(change.oldValue ?? "—")}</td>
                    <td className="px-3 py-2 font-medium">{String(change.newValue ?? "—")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </DialogContent>
      </Dialog>

      <ApprovalModal open={modalOpen} onOpenChange={setModalOpen} type={modalType} onConfirm={handleConfirm} />
    </div>
  );
}
