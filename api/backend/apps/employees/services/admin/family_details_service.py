"""
Family Details Service for Admin Side - Get and Edit Only.

Handles business logic for viewing and editing family member operations.
All queries use Django ORM for SQL injection protection.
"""

from typing import Any, Dict, List, Optional

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet

from apps.employees.models.family import EmployeeFamilyMember
from apps.employees.models.employee import Employee


def _master_label(model, pk: Optional[int]) -> Optional[str]:
    if pk is None:
        return None
    return model.objects.filter(pk=pk).values_list("label", flat=True).first()


def _family_rows_from_pending_request(employee_id: str) -> List[Dict[str, Any]]:
    """Expose employee-submitted family rows before admin approval."""
    from apps.employees.constants import ChangeRequestStatus, ESSModule
    from apps.employees.models import EmployeeChangeRequest
    from apps.employees.models.masters.misc import Occupation, Relation
    from apps.employees.models.masters.personal import BloodGroup, Gender

    cr = (
        EmployeeChangeRequest.objects.filter(
            employee_id=employee_id,
            module=ESSModule.FAMILY,
            status=ChangeRequestStatus.PENDING,
        )
        .order_by("-created_at")
        .first()
    )
    if not cr:
        return []

    rows = (cr.request_data or {}).get("family_details") or []
    payload: List[Dict[str, Any]] = []
    for row in rows:
        if row.get("remove") or row.get("delete"):
            continue

        name = (row.get("name") or "").strip()
        if not name:
            name = " ".join(
                part
                for part in [row.get("first_name"), row.get("last_name")]
                if part
            ).strip()

        relation_id = row.get("relation_id") or row.get("relationship_id")
        gender_id = row.get("gender_id")
        blood_group_id = row.get("blood_group_id")
        occupation_id = row.get("occupation_id")

        payload.append(
            {
                "id": row.get("id"),
                "first_name": row.get("first_name") or (name.split()[0] if name else ""),
                "last_name": row.get("last_name") or "",
                "full_name": name,
                "date_of_birth": row.get("date_of_birth"),
                "relation": relation_id,
                "relation_label": (
                    row.get("relationship")
                    or row.get("relation")
                    or _master_label(Relation, relation_id)
                ),
                "gender": gender_id,
                "gender_label": row.get("gender") or _master_label(Gender, gender_id),
                "occupation": occupation_id,
                "occupation_label": row.get("occupation") or _master_label(Occupation, occupation_id),
                "blood_group": blood_group_id,
                "blood_group_label": row.get("blood_group") or _master_label(BloodGroup, blood_group_id),
                "mobile_no": row.get("mobile_no") or row.get("phone"),
                "is_dependent": bool(row.get("is_dependent") or row.get("isDependent")),
                "is_nominee": False,
                "is_active": True,
            }
        )
    return payload


class FamilyDetailsService:
    """Service class for family member GET and UPDATE operations."""
    
    @staticmethod
    def get_all_family_members(employee_id: str) -> QuerySet:
        """
        Fetch all family members for a specific employee.
        
        Args:
            employee_id (str): UUID of the employee
            
        Returns:
            QuerySet: All active family members with related masters loaded
            
        Note:
            Uses select_related() to prevent N+1 queries.
            SQL injection protected through Django ORM parametrized queries.
        """
        employee = get_object_or_404(Employee, id=employee_id)
        
        return EmployeeFamilyMember.objects.filter(
            employee=employee,
            is_active=True
        ).select_related(
            'relation',
            'gender',
            'occupation',
            'blood_group',
            'nationality'
        ).order_by('created_at')

    @staticmethod
    def get_family_display_for_admin(employee_id: str) -> List[Dict[str, Any]]:
        """
        Return persisted family members, or pending employee submission when DB is empty.
        """
        from apps.employees.serializers.admin.family_details_serializer import (
            FamilyMemberSerializer,
        )

        members = FamilyDetailsService.get_all_family_members(employee_id)
        if members.exists():
            return FamilyMemberSerializer(members, many=True).data

        return _family_rows_from_pending_request(employee_id)
    
    @staticmethod
    @transaction.atomic
    def update_family_member(
        employee_id: str,
        family_member_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None
    ) -> EmployeeFamilyMember:
        """
        Update an existing family member's details.
        
        Args:
            employee_id (str): UUID of the employee
            family_member_id (str): UUID of the family member to update
            validated_data (Dict): Validated updated data from serializer
            updated_by: User object who updated the record
            
        Returns:
            EmployeeFamilyMember: Updated family member object
            
        Note:
            Uses @transaction.atomic to ensure data consistency.
            All validations done by serializer before this point.
        """
        employee = get_object_or_404(Employee, id=employee_id)
        
        family_member = get_object_or_404(
            EmployeeFamilyMember,
            id=family_member_id,
            employee=employee,
            is_active=True
        )
        
        # Update all fields
        for key, value in validated_data.items():
            setattr(family_member, key, value)
        
        family_member.save()
        
        return family_member
