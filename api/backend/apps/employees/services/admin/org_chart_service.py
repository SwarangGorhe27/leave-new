"""
Org chart service — business logic for hierarchy search, tree, assignments, and export.

All querysets are scoped by company (tenant). Uses Django ORM only.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Set

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from config.pdf_export import export_html

from apps.employees.models.employee import Employee
from apps.employees.models.masters.organization import Company, Team
from apps.employees.models.org_chart import OrgChartSettings


EMPLOYEE_TREE_SELECT = (
    "manager",
    "employment_details",
    "employment_details__designation",
    "employment_details__department",
)


def resolve_company_id(request, explicit: Optional[Any] = None) -> uuid.UUID:
    """
    Resolve company scope from explicit value, query/body, or authenticated user.
    Falls back to the first active company in the current tenant schema.
    """
    raw = explicit
    if raw is None and request is not None:
        raw = request.query_params.get("company_id")
        if raw is None and hasattr(request, "data"):
            raw = request.data.get("company_id")
    if raw is None and request is not None and getattr(request.user, "is_authenticated", False):
        profile = getattr(request.user, "employee_profile", None)
        if profile is not None:
            raw = profile.company_id
    if raw is not None:
        return uuid.UUID(str(raw))

    company = Company.objects.filter(is_active=True).order_by("created_at").first()
    if company is None:
        raise ValidationError({"company_id": "company_id is required for this tenant."})
    return company.id


def _employee_queryset(company_id: uuid.UUID):
    return (
        Employee.objects.filter(company_id=company_id, is_active=True)
        .select_related(*EMPLOYEE_TREE_SELECT)
        .order_by("employee_code")
    )


def _designation_label(employee: Employee) -> Optional[str]:
    ed = getattr(employee, "employment_details", None)
    if not ed or not ed.designation:
        return None
    return getattr(ed.designation, "name", None) or getattr(ed.designation, "label", None)


def _department_label(employee: Employee) -> Optional[str]:
    ed = getattr(employee, "employment_details", None)
    if not ed or not ed.department:
        return None
    return getattr(ed.department, "name", None) or getattr(ed.department, "label", None)


def _team_label(employee: Employee) -> Optional[str]:
    ed = getattr(employee, "employment_details", None)
    if not ed:
        return None
    return ed.team or None


def _employee_node_payload(employee: Employee, *, is_top_level: bool = False) -> Dict[str, Any]:
    manager = employee.manager
    return {
        "id": str(employee.id),
        "employee_code": employee.employee_code,
        "label": f"{employee.full_name} ({employee.employee_code})",
        "full_name": employee.full_name,
        "designation": _designation_label(employee),
        "department": _department_label(employee),
        "team": _team_label(employee),
        "manager_id": str(manager.id) if manager else None,
        "is_top_level": is_top_level,
        "children": [],
    }


def _apply_team_filter(qs, team_param: Optional[str]):
    if not team_param:
        return qs
    team_param = str(team_param).strip()
    if not team_param:
        return qs
    try:
        team_uuid = uuid.UUID(team_param)
        team = Team.objects.filter(id=team_uuid, is_active=True).first()
        if team:
            return qs.filter(
                Q(employment_details__team__iexact=team.name)
                | Q(employment_details__team__iexact=team.code)
            )
    except ValueError:
        pass
    return qs.filter(employment_details__team__icontains=team_param)


def _require_active_employee(
    company_id: uuid.UUID,
    employee_id: uuid.UUID,
    *,
    field: str,
) -> Employee:
    """
    Load an active employee in the resolved company scope.
    Raises ValidationError with a specific reason (400) instead of a generic 404.
    """
    employee = Employee.objects.filter(id=employee_id).first()
    if employee is None:
        raise ValidationError(
            {field: "Employee id was not found in this tenant schema."}
        )
    if not employee.is_active:
        raise ValidationError({field: "Employee exists but is_active is false."})
    if employee.company_id != company_id:
        raise ValidationError(
            {
                field: (
                    f"Employee belongs to company_id={employee.company_id}, but the "
                    f"request resolved company_id={company_id}. Pass the correct "
                    "company_id in the JSON body or query string."
                ),
                "company_id": str(company_id),
            }
        )
    return employee


def _manager_chain_contains(
    start_manager_id: uuid.UUID,
    target_employee_id: uuid.UUID,
    id_to_manager: Dict[uuid.UUID, Optional[uuid.UUID]],
) -> bool:
    """True if walking manager_id upward from start_manager reaches target_employee."""
    visited: Set[uuid.UUID] = set()
    current: Optional[uuid.UUID] = start_manager_id
    while current is not None:
        if current == target_employee_id:
            return True
        if current in visited:
            return False
        visited.add(current)
        current = id_to_manager.get(current)
    return False


def _would_create_cycle(employee_id: uuid.UUID, new_manager_id: Optional[uuid.UUID]) -> bool:
    if new_manager_id is None:
        return False
    if employee_id == new_manager_id:
        return True
    visited: Set[uuid.UUID] = set()
    current_id = new_manager_id
    while current_id is not None:
        if current_id == employee_id:
            return True
        if current_id in visited:
            return False
        visited.add(current_id)
        current_id = (
            Employee.objects.filter(id=current_id)
            .values_list("manager_id", flat=True)
            .first()
        )
    return False


def _get_top_level_manager_id(company_id: uuid.UUID) -> Optional[uuid.UUID]:
    settings = (
        OrgChartSettings.objects.filter(company_id=company_id, is_active=True)
        .values_list("top_level_manager_id", flat=True)
        .first()
    )
    return settings


class OrgChartService:
    """Admin org chart operations."""

    @staticmethod
    def search_employees(
        request,
        *,
        company_id: Optional[Any] = None,
        query: Optional[str] = None,
        team: Optional[str] = None,
    ):
        company_id = resolve_company_id(request, company_id)
        qs = _employee_queryset(company_id)
        qs = _apply_team_filter(qs, team)

        if query:
            term = query.strip()
            if term:
                qs = qs.filter(
                    Q(first_name__icontains=term)
                    | Q(middle_name__icontains=term)
                    | Q(last_name__icontains=term)
                    | Q(employee_code__icontains=term)
                    | Q(nickname__icontains=term)
                )

        results = []
        for emp in qs:
            mgr = emp.manager
            results.append(
                {
                    "id": emp.id,
                    "employee_code": emp.employee_code,
                    "full_name": emp.full_name,
                    "designation": _designation_label(emp),
                    "department": _department_label(emp),
                    "team": _team_label(emp),
                    "manager_id": mgr.id if mgr else None,
                    "manager_name": mgr.full_name if mgr else None,
                    "status": emp.status,
                    "profile_picture_url": emp.profile_picture_url,
                }
            )
        return results

    @staticmethod
    def build_tree(
        request,
        *,
        company_id: Optional[Any] = None,
        team: Optional[str] = None,
        manager_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        company_id = resolve_company_id(request, company_id)
        top_level_id = _get_top_level_manager_id(company_id)

        all_qs = _employee_queryset(company_id)
        if team:
            team_qs = _apply_team_filter(all_qs, team)
            team_ids = set(team_qs.values_list("id", flat=True))
            ancestor_ids: Set[uuid.UUID] = set()
            id_to_manager = dict(all_qs.values_list("id", "manager_id"))
            for emp_id in team_ids:
                current = id_to_manager.get(emp_id)
                while current:
                    ancestor_ids.add(current)
                    current = id_to_manager.get(current)
            visible_ids = team_ids | ancestor_ids
            employees = list(all_qs.filter(id__in=visible_ids))
        else:
            employees = list(all_qs)

        by_id: Dict[uuid.UUID, Dict[str, Any]] = {}
        for emp in employees:
            is_root = top_level_id is not None and emp.id == top_level_id
            by_id[emp.id] = _employee_node_payload(emp, is_top_level=is_root)

        active_ids = set(by_id.keys())
        id_to_manager: Dict[uuid.UUID, Optional[uuid.UUID]] = {
            emp.id: emp.manager_id for emp in employees
        }
        for emp in employees:
            node = by_id[emp.id]
            mgr_id = emp.manager_id
            if mgr_id and mgr_id in active_ids:
                if _manager_chain_contains(mgr_id, emp.id, id_to_manager):
                    node.setdefault("_is_root", True)
                else:
                    by_id[mgr_id]["children"].append(node)
            else:
                node.setdefault("_is_root", True)

        roots = [n for n in by_id.values() if n.pop("_is_root", False)]

        if manager_id:
            try:
                root_uuid = uuid.UUID(str(manager_id))
            except ValueError as exc:
                raise ValidationError({"manager_id": "Invalid UUID."}) from exc
            if root_uuid in by_id:
                roots = [by_id[root_uuid]]
            else:
                emp = get_object_or_404(
                    Employee,
                    id=root_uuid,
                    company_id=company_id,
                    is_active=True,
                )
                roots = [_employee_node_payload(emp)]
        elif top_level_id and top_level_id in by_id:
            roots = [by_id[top_level_id]]
        else:
            # Manager-less employees with no reportees belong in unassigned only.
            roots = [
                n
                for n in roots
                if n.get("manager_id") is not None or len(n.get("children", [])) > 0
            ]

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        for emp_id, node in by_id.items():
            nodes.append(
                {
                    "id": node["id"],
                    "type": "employee",
                    "data": {
                        "label": node["label"],
                        "employee_code": node["employee_code"],
                        "designation": node["designation"],
                        "department": node["department"],
                        "team": node["team"],
                    },
                }
            )
            if node["manager_id"]:
                edges.append(
                    {
                        "id": f"{node['manager_id']}-{node['id']}",
                        "source": node["manager_id"],
                        "target": node["id"],
                    }
                )

        def _strip_children(
            node: Dict[str, Any],
            seen: Optional[Set[str]] = None,
        ) -> Dict[str, Any]:
            seen = seen or set()
            node_id = str(node.get("id", ""))
            if node_id and node_id in seen:
                return {
                    **{k: v for k, v in node.items() if k != "children"},
                    "children": [],
                }
            next_seen = seen | {node_id} if node_id else seen
            return {
                **{k: v for k, v in node.items() if k != "children"},
                "children": [
                    _strip_children(c, next_seen) for c in node.get("children", [])
                ],
            }

        return {
            "company_id": company_id,
            "top_level_manager_id": top_level_id,
            "roots": [_strip_children(r) for r in roots],
            "nodes": nodes,
            "edges": edges,
        }

    @staticmethod
    @transaction.atomic
    def set_top_level_manager(request, manager_id: uuid.UUID) -> Dict[str, Any]:
        company_id = resolve_company_id(request)
        manager = get_object_or_404(
            Employee,
            id=manager_id,
            company_id=company_id,
            is_active=True,
        )
        if manager.manager_id is not None:
            manager.manager_id = None
            manager.save(update_fields=["manager_id", "updated_at"])

        settings, _created = OrgChartSettings.objects.get_or_create(
            company_id=company_id,
            defaults={"top_level_manager": manager},
        )
        settings.top_level_manager = manager
        settings.is_active = True
        settings.save(update_fields=["top_level_manager", "is_active", "updated_at"])

        return {
            "company_id": str(company_id),
            "top_level_manager_id": str(manager.id),
            "top_level_manager_name": manager.full_name,
        }

    @staticmethod
    @transaction.atomic
    def assign_manager(
        request,
        *,
        employee_id: uuid.UUID,
        manager_id: Optional[uuid.UUID],
    ) -> Dict[str, Any]:
        company_id = resolve_company_id(request)
        employee = get_object_or_404(
            Employee,
            id=employee_id,
            company_id=company_id,
            is_active=True,
        )

        manager = None
        if manager_id is not None:
            manager = get_object_or_404(
                Employee,
                id=manager_id,
                company_id=company_id,
                is_active=True,
            )
            if _would_create_cycle(employee.id, manager.id):
                raise ValidationError(
                    {"manager_id": "Assignment would create a circular reporting line."}
                )

        employee.manager = manager
        employee.save(update_fields=["manager_id", "updated_at"])

        if manager_id is None:
            OrgChartSettings.objects.filter(
                company_id=company_id,
                top_level_manager_id=employee.id,
            ).update(top_level_manager=None)

        return {
            "employee_id": str(employee.id),
            "employee_name": employee.full_name,
            "manager_id": str(manager.id) if manager else None,
            "manager_name": manager.full_name if manager else None,
        }

    @staticmethod
    @transaction.atomic
    def mass_transfer(
        request,
        *,
        from_manager_id: uuid.UUID,
        employee_ids: List[uuid.UUID],
        to_manager_id: uuid.UUID,
        company_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        company_id = resolve_company_id(request, explicit=company_id)
        from_manager = _require_active_employee(
            company_id, from_manager_id, field="from_manager_id"
        )
        to_manager = _require_active_employee(
            company_id, to_manager_id, field="to_manager_id"
        )
        if from_manager.id == to_manager.id:
            raise ValidationError(
                {"to_manager_id": "Target manager must differ from source manager."}
            )

        unique_ids = list({uuid.UUID(str(eid)) for eid in employee_ids})
        reportees = list(
            Employee.objects.filter(
                company_id=company_id,
                is_active=True,
                manager_id=from_manager.id,
                id__in=unique_ids,
            )
        )
        if len(reportees) != len(unique_ids):
            raise ValidationError(
                {
                    "employee_ids": (
                        "All employees must be active direct reportees of from_manager_id."
                    )
                }
            )

        for emp in reportees:
            if _would_create_cycle(emp.id, to_manager.id):
                raise ValidationError(
                    {
                        "employee_ids": (
                            f"Transfer of {emp.employee_code} would create a reporting cycle."
                        )
                    }
                )

        updated_ids = []
        for emp in reportees:
            emp.manager = to_manager
            emp.save(update_fields=["manager_id", "updated_at"])
            updated_ids.append(str(emp.id))

        return {
            "from_manager_id": str(from_manager.id),
            "to_manager_id": str(to_manager.id),
            "transferred_count": len(updated_ids),
            "employee_ids": updated_ids,
        }

    @staticmethod
    def list_unassigned(
        request,
        *,
        company_id: Optional[Any] = None,
        query: Optional[str] = None,
    ):
        company_id = resolve_company_id(request, company_id)
        qs = _employee_queryset(company_id).filter(manager__isnull=True)

        if query:
            term = query.strip()
            if term:
                qs = qs.filter(
                    Q(first_name__icontains=term)
                    | Q(middle_name__icontains=term)
                    | Q(last_name__icontains=term)
                    | Q(employee_code__icontains=term)
                )

        return [
            {
                "id": emp.id,
                "employee_code": emp.employee_code,
                "full_name": emp.full_name,
                "designation": _designation_label(emp),
                "department": _department_label(emp),
                "team": _team_label(emp),
                "status": emp.status,
            }
            for emp in qs
        ]

    @staticmethod
    def export_chart(
        request,
        *,
        export_format: str,
        company_id: Optional[Any] = None,
        team: Optional[str] = None,
        manager_id: Optional[str] = None,
        image_base64: Optional[str] = None,
    ) -> Dict[str, Any]:
        tree = OrgChartService.build_tree(
            request,
            company_id=company_id,
            team=team,
            manager_id=manager_id,
        )
        html = OrgChartService._tree_to_html(tree)

        return export_html(
            html,
            export_format,
            image_base64=image_base64,
            png_filename_prefix="org_chart",
        )

    @staticmethod
    def _tree_to_html(tree: Dict[str, Any]) -> str:
        def render_node(node: Dict[str, Any], depth: int = 0) -> str:
            indent = "  " * depth
            title = node.get("label") or node.get("full_name") or node.get("id")
            extra = []
            if node.get("designation"):
                extra.append(node["designation"])
            if node.get("team"):
                extra.append(f"Team: {node['team']}")
            subtitle = " — ".join(extra)
            line = f"{indent}<li><strong>{title}</strong>"
            if subtitle:
                line += f" <span>({subtitle})</span>"
            children = node.get("children") or []
            if children:
                line += f"\n{indent}  <ul>\n"
                line += "\n".join(render_node(child, depth + 2) for child in children)
                line += f"\n{indent}  </ul>"
            line += "</li>"
            return line

        roots_html = "\n".join(render_node(root) for root in tree.get("roots", []))
        generated = timezone.now().strftime("%Y-%m-%d %H:%M UTC")
        return f"""
        <html>
          <head>
            <meta charset="utf-8"/>
            <style>
              body {{ font-family: Arial, sans-serif; margin: 24px; }}
              h1 {{ font-size: 20px; }}
              ul {{ list-style-type: none; padding-left: 16px; }}
              li {{ margin: 6px 0; }}
              span {{ color: #555; font-size: 12px; }}
            </style>
          </head>
          <body>
            <h1>Organization Chart</h1>
            <p>Generated: {generated}</p>
            <ul>{roots_html}</ul>
          </body>
        </html>
        """
