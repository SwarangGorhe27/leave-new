"""
Admin service for Fines & Damages Register.

All DB access goes through Django ORM only; no raw SQL.
"""

from decimal import Decimal
from typing import Any, Dict, Optional
import io

from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.employees.models.employee import Employee
from apps.employees.models.fines_damages import EmployeeFine, EmployeePropertyDamage


# ---------------------------------------------------------------------------
# Internal field-map helpers
# ---------------------------------------------------------------------------

_FINE_FIELD_MAP = {
    "employeeId": "employee_id",
    "offenceDate": "offence_date",
    "actOrOmission": "act_or_omission",
    "showCause": "show_cause",
    "showCauseDate": "show_cause_date",
    "fineAmount": "fine_amount",
    "realizedDate": "realized_date",
    "remarks": "remarks",
    "status": "status",
}

_DAMAGE_FIELD_MAP = {
    "employeeId": "employee_id",
    "damageDate": "damage_date",
    "propertyName": "property_name",
    "damageDescription": "damage_description",
    "damageAmount": "damage_amount",
    "installmentsCount": "installments_count",
    "firstInstallmentDate": "first_installment_date",
    "lastInstallmentDate": "last_installment_date",
    "remarks": "remarks",
}


def _map(data: Dict, field_map: Dict) -> Dict:
    return {field_map[k]: v for k, v in data.items() if k in field_map}


# ---------------------------------------------------------------------------
# Fine Service
# ---------------------------------------------------------------------------

class FineService:

    @staticmethod
    def list_fines(
        employee_id: Optional[str] = None,
        realized_date: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ):
        qs = (
            EmployeeFine.objects.select_related("employee")
            .filter(is_active=True)
        )
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if realized_date:
            qs = qs.filter(realized_date=realized_date)
        if from_date:
            qs = qs.filter(offence_date__gte=from_date)
        if to_date:
            qs = qs.filter(offence_date__lte=to_date)
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search)
                | Q(employee__last_name__icontains=search)
                | Q(employee__employee_code__icontains=search)
                | Q(act_or_omission__icontains=search)
            )
        return qs

    @staticmethod
    def get_fine(fine_id: str) -> EmployeeFine:
        return get_object_or_404(
            EmployeeFine.objects.select_related("employee"),
            id=fine_id,
            is_active=True,
        )

    @staticmethod
    def create_fine(
        validated_data: Dict[str, Any], recorded_by_id: Optional[str] = None
    ) -> EmployeeFine:
        employee_id = validated_data.get("employeeId")
        get_object_or_404(Employee, id=employee_id, is_active=True)

        data = _map(validated_data, _FINE_FIELD_MAP)
        if recorded_by_id:
            data["recorded_by"] = recorded_by_id

        with transaction.atomic():
            fine = EmployeeFine.objects.create(**data)
        return EmployeeFine.objects.select_related("employee").get(id=fine.id)

    @staticmethod
    def update_fine(
        fine_id: str,
        validated_data: Dict[str, Any],
        updated_by_id: Optional[str] = None,
    ) -> EmployeeFine:
        fine = FineService.get_fine(fine_id)
        data = _map(validated_data, _FINE_FIELD_MAP)
        if updated_by_id:
            data["updated_by"] = updated_by_id

        with transaction.atomic():
            for field, value in data.items():
                setattr(fine, field, value)
            fine.save()
        return EmployeeFine.objects.select_related("employee").get(id=fine.id)

    @staticmethod
    def patch_status(
        fine_id: str,
        status: str,
        updated_by_id: Optional[str] = None,
    ) -> EmployeeFine:
        fine = FineService.get_fine(fine_id)
        with transaction.atomic():
            fine.status = status
            if updated_by_id:
                fine.updated_by = updated_by_id
            fine.save(update_fields=["status", "updated_by", "updated_at"])
        return EmployeeFine.objects.select_related("employee").get(id=fine.id)

    @staticmethod
    def delete_fine(fine_id: str) -> None:
        fine = FineService.get_fine(fine_id)
        with transaction.atomic():
            fine.is_active = False
            fine.deleted_at = timezone.now()
            fine.save(update_fields=["is_active", "deleted_at", "updated_at"])

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        qs = EmployeeFine.objects.filter(is_active=True)
        agg = qs.aggregate(
            total=Count("id"),
            pending=Count("id", filter=Q(status=EmployeeFine.FineStatus.PENDING)),
            realized=Count("id", filter=Q(status=EmployeeFine.FineStatus.REALIZED)),
            cancelled=Count("id", filter=Q(status=EmployeeFine.FineStatus.CANCELLED)),
            total_amount=Sum("fine_amount"),
            realized_amount=Sum(
                "fine_amount", filter=Q(status=EmployeeFine.FineStatus.REALIZED)
            ),
        )
        return {
            "totalFines": agg["total"] or 0,
            "pendingFines": agg["pending"] or 0,
            "realizedFines": agg["realized"] or 0,
            "cancelledFines": agg["cancelled"] or 0,
            "totalFineAmount": agg["total_amount"] or Decimal("0.00"),
            "totalRealizedAmount": agg["realized_amount"] or Decimal("0.00"),
            "pendingRecoveries": agg["pending"] or 0,
        }

    @staticmethod
    def export_fines(
        employee_id: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        fmt: str = "excel",
    ) -> bytes:
        """Return CSV/Excel bytes for the filtered fine list."""
        qs = FineService.list_fines(
            employee_id=employee_id, from_date=from_date, to_date=to_date
        )
        return _build_export(
            qs,
            headers=[
                "Date of Offence", "Emp Number", "Employee Name",
                "Act / Omission", "Fine Amount", "Realized On",
                "Remarks", "Status",
            ],
            row_fn=lambda f: [
                str(f.offence_date),
                f.employee.employee_code,
                f"{f.employee.first_name} {f.employee.last_name}".strip(),
                f.act_or_omission,
                str(f.fine_amount),
                str(f.realized_date) if f.realized_date else "",
                f.remarks or "",
                f.status,
            ],
            fmt=fmt,
        )


# ---------------------------------------------------------------------------
# Property Damage Service
# ---------------------------------------------------------------------------

class PropertyDamageService:

    @staticmethod
    def list_damages(
        employee_id: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        search: Optional[str] = None,
        installments_count: Optional[int] = None,
    ):
        qs = (
            EmployeePropertyDamage.objects.select_related("employee")
            .filter(is_active=True)
        )
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if from_date:
            qs = qs.filter(damage_date__gte=from_date)
        if to_date:
            qs = qs.filter(damage_date__lte=to_date)
        if installments_count is not None:
            qs = qs.filter(installments_count=installments_count)
        if search:
            qs = qs.filter(
                Q(employee__first_name__icontains=search)
                | Q(employee__last_name__icontains=search)
                | Q(employee__employee_code__icontains=search)
                | Q(property_name__icontains=search)
                | Q(damage_description__icontains=search)
            )
        return qs

    @staticmethod
    def get_damage(damage_id: str) -> EmployeePropertyDamage:
        return get_object_or_404(
            EmployeePropertyDamage.objects.select_related("employee"),
            id=damage_id,
            is_active=True,
        )

    @staticmethod
    def create_damage(
        validated_data: Dict[str, Any], recorded_by_id: Optional[str] = None
    ) -> EmployeePropertyDamage:
        employee_id = validated_data.get("employeeId")
        get_object_or_404(Employee, id=employee_id, is_active=True)

        data = _map(validated_data, _DAMAGE_FIELD_MAP)
        if recorded_by_id:
            data["recorded_by"] = recorded_by_id

        with transaction.atomic():
            damage = EmployeePropertyDamage.objects.create(**data)
        return EmployeePropertyDamage.objects.select_related("employee").get(
            id=damage.id
        )

    @staticmethod
    def update_damage(
        damage_id: str,
        validated_data: Dict[str, Any],
        updated_by_id: Optional[str] = None,
    ) -> EmployeePropertyDamage:
        damage = PropertyDamageService.get_damage(damage_id)
        data = _map(validated_data, _DAMAGE_FIELD_MAP)
        if updated_by_id:
            data["updated_by"] = updated_by_id

        with transaction.atomic():
            for field, value in data.items():
                setattr(damage, field, value)
            damage.save()
        return EmployeePropertyDamage.objects.select_related("employee").get(
            id=damage.id
        )

    @staticmethod
    def delete_damage(damage_id: str) -> None:
        damage = PropertyDamageService.get_damage(damage_id)
        with transaction.atomic():
            damage.is_active = False
            damage.deleted_at = timezone.now()
            damage.save(update_fields=["is_active", "deleted_at", "updated_at"])

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        qs = EmployeePropertyDamage.objects.filter(is_active=True)
        agg = qs.aggregate(
            total=Count("id"),
            total_amount=Sum("damage_amount"),
        )
        return {
            "totalDamages": agg["total"] or 0,
            "totalDamageAmount": agg["total_amount"] or Decimal("0.00"),
            "totalRecoveredAmount": Decimal("0.00"),  # extend when payment tracking added
            "pendingRecoveries": agg["total"] or 0,
        }

    @staticmethod
    def export_damages(
        employee_id: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        fmt: str = "excel",
    ) -> bytes:
        qs = PropertyDamageService.list_damages(
            employee_id=employee_id, from_date=from_date, to_date=to_date
        )
        return _build_export(
            qs,
            headers=[
                "Date of Damage", "Emp Number", "Employee Name",
                "Property Name", "Damage / Loss Particulars",
                "Deduction Amount", "Installments", "First Install Date",
                "Last Install Date", "Remarks",
            ],
            row_fn=lambda d: [
                str(d.damage_date),
                d.employee.employee_code,
                f"{d.employee.first_name} {d.employee.last_name}".strip(),
                d.property_name,
                d.damage_description,
                str(d.damage_amount),
                str(d.installments_count) if d.installments_count else "",
                str(d.first_installment_date) if d.first_installment_date else "",
                str(d.last_installment_date) if d.last_installment_date else "",
                d.remarks or "",
            ],
            fmt=fmt,
        )


# ---------------------------------------------------------------------------
# Employee dropdown / search
# ---------------------------------------------------------------------------

class EmployeeDropdownService:

    @staticmethod
    def dropdown():
        return (
            Employee.objects.filter(is_active=True)
            .only("id", "employee_code", "first_name", "last_name")
            .order_by("first_name", "last_name")
        )

    @staticmethod
    def search(keyword: str):
        return (
            Employee.objects.filter(is_active=True)
            .filter(
                Q(first_name__icontains=keyword)
                | Q(last_name__icontains=keyword)
                | Q(employee_code__icontains=keyword)
            )
            .only("id", "employee_code", "first_name", "last_name")[:50]
        )


# ---------------------------------------------------------------------------
# Export helper (CSV / Excel)
# ---------------------------------------------------------------------------

def _build_export(qs, headers, row_fn, fmt: str = "excel") -> bytes:
    """Build a CSV or Excel byte stream from a queryset."""
    if fmt == "excel":
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(headers)
            for obj in qs:
                ws.append(row_fn(obj))
            buf = io.BytesIO()
            wb.save(buf)
            return buf.getvalue()
        except ImportError:
            pass  # fall through to CSV

    # CSV fallback
    import csv
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for obj in qs:
        writer.writerow(row_fn(obj))
    return buf.getvalue().encode("utf-8")
