"""
Manual Punch Selectors - Database queries for manual swipe logs.
"""

from django.db.models import QuerySet, Count, Q
from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.models.enums import PunchSource

class ManualPunchSelectors:
    """
    Encapsulates database access logic for manual punches.
    """

    @staticmethod
    def get_manual_punches(
        company_id: str,
        from_date=None,
        to_date=None,
        employee_id=None,
        created_by_id=None
    ) -> QuerySet:
        """
        Get list of manual punches with optimized relations.
        """
        qs = PunchLog.objects.filter(
            company_id=company_id,
            punch_source=PunchSource.MANUAL
        ).select_related(
            "employee",
            "created_by"
        ).exclude(
            meta_data__is_deleted=True
        ).order_by("-created_at")

        if from_date:
            qs = qs.filter(punch_time__date__gte=from_date)
        if to_date:
            qs = qs.filter(punch_time__date__lte=to_date)
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if created_by_id:
            qs = qs.filter(created_by_id=created_by_id)

        return qs

    @staticmethod
    def get_stats(company_id: str, from_date=None, to_date=None) -> dict:
        """
        Calculate manual punch statistics.
        """
        base_qs = PunchLog.objects.filter(
            company_id=company_id,
            punch_source=PunchSource.MANUAL
        ).exclude(meta_data__is_deleted=True)

        if from_date:
            base_qs = base_qs.filter(punch_time__date__gte=from_date)
        if to_date:
            base_qs = base_qs.filter(punch_time__date__lte=to_date)

        total_count = base_qs.count()
        
        by_type = list(base_qs.values('punch_type').annotate(
            count=Count('id')
        ).order_by('punch_type'))

        top_overriders = list(base_qs.values(
            'created_by_id', 
            'created_by__first_name', 
            'created_by__last_name'
        ).annotate(count=Count('id')).order_by('-count')[:5])

        return {
            "total_manual_punches": total_count,
            "by_type": by_type,
            "top_overriders": [
                {"hr_id": item['created_by_id'], "name": f"{item['created_by__first_name']} {item['created_by__last_name']}", "count": item['count']}
                for item in top_overriders
            ]
        }