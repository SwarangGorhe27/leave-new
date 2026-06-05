from typing import Any, Dict

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from ..models.masters.accural_schedule import AccrualSchedule
from ..models.masters.leave_policy import LeavePolicyRule
from .base_service import BaseLeaveService


class AccrualScheduleService(BaseLeaveService):
    @staticmethod
    def create_accrual_schedule(data: Dict[str, Any]) -> AccrualSchedule:
        """
        Create a new accrual schedule.
        """
        policy_rule = get_object_or_404(
            LeavePolicyRule, 
            id=data["policy_rule_id"]
        )
        
        accrual_schedule = AccrualSchedule.objects.create(
            policy_rule=policy_rule,
            frequency=data["frequency"],
            run_day_of_month=data.get("run_day_of_month"),
            run_month=data.get("run_month"),
            proration_on_join=data.get("proration_on_join", True),
            rounding_rule=data.get("rounding_rule", "FLOOR"),
            is_active=data.get("is_active", True),
            meta_data=data.get("meta_data", {}),
            meta_tags=data.get("meta_tags", []),
        )
        
        return accrual_schedule
    
    @staticmethod
    def list_accrual_schedules(filters: Dict[str, Any]) -> QuerySet:
        queryset = (
            AccrualSchedule.objects.select_related(
                "policy_rule",
                "policy_rule__policy",
                "policy_rule__leave_type",
            )
            .filter(deleted_at__isnull=True)
            .order_by(
                "policy_rule__policy__name",
                "policy_rule__leave_type__name",
                "frequency",
                "run_day_of_month",
            )
        )

        if "is_active" in filters:
            queryset = queryset.filter(is_active=filters["is_active"])

        if filters.get("frequency"):
            queryset = queryset.filter(frequency=filters["frequency"])

        if filters.get("policy_id"):
            queryset = queryset.filter(policy_rule__policy_id=filters["policy_id"])

        if filters.get("policy_rule_id"):
            queryset = queryset.filter(policy_rule_id=filters["policy_rule_id"])

        if filters.get("leave_type_id"):
            queryset = queryset.filter(
                policy_rule__leave_type_id=filters["leave_type_id"]
            )

        return queryset
