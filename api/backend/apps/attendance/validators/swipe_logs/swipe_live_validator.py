"""Validators for swipe live polling endpoints."""

from typing import Optional

from django.core.exceptions import ValidationError

from apps.employees.models import Company


class SwipeLiveValidator:
    """Validation helpers for live swipe polling endpoints."""

    @staticmethod
    def validate_company_exists(company_id: str) -> None:
        if not Company.objects.filter(id=company_id).exists():
            raise ValidationError(f"Company {company_id} not found.")

    @staticmethod
    def validate_polling_params(
        since: Optional[str] = None,
        limit: Optional[int] = None,
        device_ids: Optional[list[int]] = None,
    ) -> None:
        if limit is not None and (not isinstance(limit, int) or limit < 1 or limit > 500):
            raise ValidationError("Limit must be between 1 and 500.")

    @staticmethod
    def validate_summary_params(location_id: Optional[str] = None) -> None:
        return None
