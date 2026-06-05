from datetime import datetime, time

from django.db.models import Q
from rest_framework.exceptions import ValidationError

from ..helpers import paginate_queryset
from ..models.system_and_audit.audit_logs import AuditLogs


class AuditLogsService:
    @staticmethod
    def get_audit_logs(request):
        queryset = AuditLogs.objects.select_related("actor").all()

        entity_type = request.query_params.get("entity_type")
        if entity_type:
            normalized = entity_type.strip().lower()
            variants = {
                normalized,
                normalized.rstrip("s"),
                f"{normalized.rstrip('s')}s",
                normalized.replace("_", ""),
                normalized.replace("_", " "),
                normalized.replace("_", "-")
            }
            table_q = Q()
            module_q = Q()
            for variant in variants:
                table_q |= Q(table_name__iexact=variant)
                module_q |= Q(module__iexact=variant)

            queryset = queryset.filter(
                table_q
                | module_q
                | Q(action__icontains=normalized)
            )

        start_date = request.query_params.get("start_date")
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                queryset = queryset.filter(created_at__gte=start)
            except ValueError as exc:
                raise ValidationError({"start_date": "Use YYYY-MM-DD format."}) from exc

        end_date = request.query_params.get("end_date")
        if end_date:
            try:
                end = datetime.combine(
                    datetime.strptime(end_date, "%Y-%m-%d").date(),
                    time.max,
                )
                queryset = queryset.filter(created_at__lte=end)
            except ValueError as exc:
                raise ValidationError({"end_date": "Use YYYY-MM-DD format."}) from exc

        results, total = paginate_queryset(queryset.order_by("-created_at"), request)
        return results, total
