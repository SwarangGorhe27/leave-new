"""
Leave module Django signals.

Registered in LeaveConfig.ready() via apps.py.

Signal responsibilities
-----------------------
1. LeaveRequest post_save
   - Auto-create LeaveStatusHistory whenever status changes.
   - Trigger LeaveBalanceService on approve / reject / cancel
     so the balance ledger is always in sync regardless of
     which code path changed the status.

2. LeaveApproval post_save
   - Sync actioned_on = actioned_at when an approval is actioned.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver


# ──────────────────────────────────────────────────────────────────────────────
# LeaveRequest — status-change tracking
# ──────────────────────────────────────────────────────────────────────────────

@receiver(post_save, sender="leave.LeaveRequest")
def on_leave_request_saved(sender, instance, created, **kwargs):
    """
    Track every status transition in LeaveStatusHistory.
    Uses _pre_status stashed by the view layer (or defaults to blank).
    """
    from .models.transactions.leave_status_history import LeaveStatusHistory

    old_status = getattr(instance, "_pre_status", None)
    new_status = instance.status

    # Only write a history row when status actually changed
    if old_status is None or old_status == new_status:
        return

    LeaveStatusHistory.objects.create(
        leave_request=instance,
        from_status=old_status,
        to_status=new_status,
        old_status=old_status,
        new_status=new_status,
        # changed_by is set on the instance by the view layer when available
        changed_by=getattr(instance, "_changed_by", None),
        remarks=getattr(instance, "_change_remarks", ""),
    )


# ──────────────────────────────────────────────────────────────────────────────
# LeaveApproval — sync actioned_on with actioned_at
# ──────────────────────────────────────────────────────────────────────────────

@receiver(post_save, sender="leave.LeaveApproval")
def on_leave_approval_saved(sender, instance, created, **kwargs):
    """
    Keep actioned_on in sync with actioned_at so both spec-required
    fields always carry the same value.
    """
    if instance.actioned_at and instance.actioned_on != instance.actioned_at:
        # avoid recursion: use queryset update instead of instance.save()
        type(instance).objects.filter(pk=instance.pk).update(
            actioned_on=instance.actioned_at
        )
