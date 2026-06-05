import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "../ui/dialog";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";

interface ApprovalModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  type: "approve" | "reject" | null;
  onConfirm: (rejectionReason?: string, adminRemark?: string) => void;
}

export function ApprovalModal({ open, onOpenChange, type, onConfirm }: ApprovalModalProps) {
  const [reason, setReason] = useState("");
  const [adminRemark, setAdminRemark] = useState("");

  const handleConfirm = () => {
    if (type === "approve") {
      onConfirm(undefined, adminRemark.trim() || undefined);
    } else {
      onConfirm(reason, undefined);
    }
    setReason("");
    setAdminRemark("");
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{type === "approve" ? "Approve Request" : "Reject Request"}</DialogTitle>
          <DialogDescription>
            {type === "approve"
              ? "Are you sure you want to approve this profile update? The employee profile will be updated immediately."
              : "Please provide a reason for rejecting this profile update request. The employee will see this reason."}
          </DialogDescription>
        </DialogHeader>

        {type === "approve" && (
          <div className="py-2">
            <p className="text-xs font-medium text-muted-foreground mb-2">Admin remark (optional)</p>
            <Textarea
              placeholder="Notes for the employee or audit trail..."
              value={adminRemark}
              onChange={(e) => setAdminRemark(e.target.value)}
              className="min-h-[80px]"
            />
          </div>
        )}

        {type === "reject" && (
          <div className="py-4">
            <Textarea
              placeholder="Rejection reason..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="min-h-[100px]"
            />
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            variant={type === "approve" ? "default" : "destructive"}
            onClick={handleConfirm}
            disabled={type === "reject" && !reason.trim()}
          >
            {type === "approve" ? "Approve" : "Reject"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
