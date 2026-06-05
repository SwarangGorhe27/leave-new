"""Language Details — read, apply, and change-request helpers."""

from typing import Any, Dict, List

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.employees.constants.language_details import LANGUAGE_PROFICIENCY_ROW_FIELDS
from apps.employees.models.employee import Employee
from apps.employees.models.language import EmployeeLanguageProficiency


def _master_label(obj):
    if obj is None:
        return None
    return (
        getattr(obj, "label", None)
        or getattr(obj, "name", None)
        or getattr(obj, "code", None)
    )


def _first_selected_proficiency(proficiency: EmployeeLanguageProficiency):
    return (
        proficiency.read_proficiency
        or proficiency.write_proficiency
        or proficiency.speak_proficiency
    )


def build_language_details(employee: Employee) -> List[Dict[str, Any]]:
    """Build language_details list for employee Language Details UI."""
    language_details = []
    
    for proficiency in employee.language_proficiencies.filter(
        is_active=True
    ).select_related(
        "language",
        "read_proficiency",
        "write_proficiency",
        "speak_proficiency",
    ):
        # Determine if can read/write/speak based on proficiency levels
        can_read = proficiency.read_proficiency_id is not None
        can_write = proficiency.write_proficiency_id is not None
        can_speak = proficiency.speak_proficiency_id is not None
        
        selected_proficiency = _first_selected_proficiency(proficiency)

        row = {
            "id": str(proficiency.id),
            "language_id": proficiency.language_id,
            "language": _master_label(proficiency.language),

            # Screenshot field: one proficiency dropdown used by selected skills.
            "proficiency_level_id": (
                selected_proficiency.id if selected_proficiency else None
            ),
            "proficiency_level": _master_label(selected_proficiency),
            
            # Proficiency levels
            "read_proficiency_id": proficiency.read_proficiency_id,
            "read_proficiency": _master_label(proficiency.read_proficiency),
            
            "write_proficiency_id": proficiency.write_proficiency_id,
            "write_proficiency": _master_label(proficiency.write_proficiency),
            
            "speak_proficiency_id": proficiency.speak_proficiency_id,
            "speak_proficiency": _master_label(proficiency.speak_proficiency),
            
            # Checkboxes for capabilities
            "can_read": can_read,
            "can_write": can_write,
            "can_speak": can_speak,
            
            # Flags
            "is_mother_tongue": proficiency.is_mother_tongue,
        }
        
        language_details.append({k: row[k] for k in LANGUAGE_PROFICIENCY_ROW_FIELDS})
    
    return language_details


@transaction.atomic
def apply_language_details(employee: Employee, data: Dict[str, Any]) -> None:
    """Apply approved LANGUAGE change request."""
    language_data = data.get("language_details")
    if language_data is None:
        raise ValidationError({"language_details": "language_details list is required."})
    
    update_language_details(employee, language_data)


def update_language_details(
    employee: Employee,
    data: List[Dict[str, Any]],
) -> None:
    """Update employee language proficiencies."""
    
    # Track which proficiencies to keep (by ID)
    ids_to_keep = set()
    
    for row in data:
        # Skip delete/remove rows
        if row.get("remove") or row.get("delete"):
            if row.get("id"):
                # Soft delete
                EmployeeLanguageProficiency.objects.filter(
                    id=row["id"],
                    employee=employee,
                ).update(is_active=False)
            continue
        
        language_id = row.get("language_id")
        if not language_id:
            raise ValidationError(
                {"language_details": "language_id is required for non-deleted rows."}
            )
        
        # Get or create language proficiency record
        proficiency_id = row.get("id")
        if proficiency_id:
            # Update existing
            try:
                prof = EmployeeLanguageProficiency.objects.get(
                    id=proficiency_id,
                    employee=employee,
                    is_active=True,
                )
                ids_to_keep.add(proficiency_id)
            except EmployeeLanguageProficiency.DoesNotExist:
                raise ValidationError(
                    {"language_details": f"Language proficiency {proficiency_id} not found."}
                )
        else:
            # Update existing language row if the client did not send its id.
            prof = (
                EmployeeLanguageProficiency.objects.filter(
                    employee=employee,
                    language_id=language_id,
                    is_active=True,
                )
                .first()
                or EmployeeLanguageProficiency(
                    employee=employee,
                    language_id=language_id,
                )
            )
        
        proficiency_level_id = row.get("proficiency_level_id")

        # Update proficiency levels based on screenshot field, checkboxes, or
        # legacy per-skill explicit IDs.
        if row.get("can_read"):
            prof.read_proficiency_id = (
                row.get("read_proficiency_id") or proficiency_level_id
            )
        else:
            prof.read_proficiency_id = None
        
        if row.get("can_write"):
            prof.write_proficiency_id = (
                row.get("write_proficiency_id") or proficiency_level_id
            )
        else:
            prof.write_proficiency_id = None
        
        if row.get("can_speak"):
            prof.speak_proficiency_id = (
                row.get("speak_proficiency_id") or proficiency_level_id
            )
        else:
            prof.speak_proficiency_id = None
        
        prof.is_mother_tongue = row.get("is_mother_tongue", False)
        prof.is_active = True
        prof.save()
        
        if proficiency_id:
            ids_to_keep.add(proficiency_id)
        else:
            ids_to_keep.add(prof.id)
    
    # Soft delete any existing proficiencies not in the update
    EmployeeLanguageProficiency.objects.filter(
        employee=employee,
        is_active=True,
    ).exclude(id__in=ids_to_keep).update(is_active=False)
