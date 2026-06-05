from datetime import date
from typing import Dict, Iterable, List

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError

from apps.employees.models.employee import Employee
from apps.employees.models.masters.audit_additions import EmployeeFilter
from apps.employees.models.masters.organization import Company
from apps.employees.models.segments import EmployeeSegment, EmployeeSegmentMember


def actor_id(user):
    employee = getattr(user, "employee_profile", None)
    if employee:
        return employee.id
    if user and getattr(user, "is_authenticated", False):
        return getattr(user, "id", None)
    return None


def company_from_request(request):
    employee = getattr(request.user, "employee_profile", None)
    if employee and getattr(employee, "company_id", None):
        return employee.company
    company_id = request.query_params.get("company_id")
    if not company_id and request.method not in {"GET", "HEAD", "OPTIONS"}:
        company_id = request.data.get("company_id")
    if not company_id:
        raise ValidationError({"company_id": "company_id is required for admin users without employee profile."})
    return get_object_or_404(Company, id=company_id, is_active=True)


PREDEFINED_FILTERS = {
    "ALL_EMPLOYEES": {
        "label": "All Employees",
        "query": lambda: Q(is_active=True),
    },
    "ALL_CURRENT_EMPLOYEES": {
        "label": "All Current Employees",
        "query": lambda: Q(is_active=True, status=Employee.StatusChoices.ACTIVE),
    },
    "ALL_PAST_EMPLOYEES": {
        "label": "All Past Employees",
        "query": lambda: Q(status__in=[
            Employee.StatusChoices.RESIGNED,
            Employee.StatusChoices.TERMINATED,
            Employee.StatusChoices.RETIRED,
        ]),
    },
    "ABOVE_5_YEARS": {
        "label": "Above 5 Years",
        "query": lambda: Q(date_of_joining__lte=date(date.today().year - 5, date.today().month, date.today().day)),
    },
    "BETWEEN_3_5_YEARS": {
        "label": "Between 3 - 5 Years",
        "query": lambda: Q(
            date_of_joining__lte=date(date.today().year - 3, date.today().month, date.today().day),
            date_of_joining__gte=date(date.today().year - 5, date.today().month, date.today().day),
        ),
    },
    "UPTO_3_YEARS_SERVICE": {
        "label": "Upto 3 Years Service",
        "query": lambda: Q(date_of_joining__gte=date(date.today().year - 3, date.today().month, date.today().day)),
    },
    "BANGALORE_EMPLOYEES": {
        "label": "Bangalore Employees",
        "query": lambda: Q(employment_details__office_location__label__icontains="Bangalore"),
    },
    "CONFIRMED_EMPLOYEES": {
        "label": "Confirmed Employees",
        "query": lambda: Q(employment_details__probation_status__icontains="confirm"),
    },
    "PROBATION_EMP": {
        "label": "Probation Emp",
        "query": lambda: Q(employment_details__probation_status__icontains="probation"),
    },
    "CONTRACT_EMP": {
        "label": "Contract Emp",
        "query": lambda: Q(employment_details__employee_type__label__icontains="contract"),
    },
    "TRAINEE_EMPLOYEES": {
        "label": "Trainee Employees",
        "query": lambda: (
            Q(employment_details__employee_type__label__icontains="trainee")
            | Q(employment_details__category__label__icontains="trainee")
        ),
    },
    "SALES_DEPARTMENT": {
        "label": "Sales Department",
        "query": lambda: Q(employment_details__department__name__icontains="sales"),
    },
    "PARTIALLY_VACCINATED_EMPLOYEES": {
        "label": "Partially Vaccinated Employees",
        "query": lambda: Q(id__isnull=False) & Q(id__isnull=True),
    },
}


FIELD_MAP = {
    "employee_number": "employee_code",
    "employeeCode": "employee_code",
    "employee_code": "employee_code",
    "first_name": "first_name",
    "last_name": "last_name",
    "full_name": None,
    "status": "status",
    "department": "employment_details__department__name",
    "department_id": "employment_details__department_id",
    "designation": "employment_details__designation__title",
    "designation_id": "employment_details__designation_id",
    "employee_type": "employment_details__employee_type__label",
    "employee_type_id": "employment_details__employee_type_id",
    "office_location": "employment_details__office_location__label",
    "office_location_id": "employment_details__office_location_id",
    "probation_status": "employment_details__probation_status",
    "date_of_joining": "date_of_joining",
}

TEXT_OPERATORS = {
    "EQUALS": "",
    "NOT_EQUALS": "",
    "CONTAINS": "__icontains",
    "STARTS_WITH": "__istartswith",
    "ENDS_WITH": "__iendswith",
}
COMPARISON_OPERATORS = {
    "GREATER_THAN": "__gt",
    "LESS_THAN": "__lt",
    "GREATER_THAN_OR_EQUAL": "__gte",
    "LESS_THAN_OR_EQUAL": "__lte",
}


def base_employee_queryset(company):
    return (
        Employee.objects.filter(company=company, is_active=True)
        .select_related(
            "company",
            "employment_details__department",
            "employment_details__designation",
            "employment_details__employee_type",
            "employment_details__category",
            "employment_details__office_location",
        )
        .order_by("employee_code", "first_name")
    )


def _rule_to_q(rule):
    field = str(rule.get("field") or "").strip()
    operator = str(rule.get("operator") or "EQUALS").strip().upper()
    value = rule.get("value")
    if field not in FIELD_MAP:
        raise ValidationError({"ruleConfig": f"Unsupported filter field: {field}."})
    if value in ("", None) and operator not in {"IS_EMPTY", "IS_NOT_EMPTY"}:
        raise ValidationError({"ruleConfig": f"Value is required for field {field}."})

    if field == "full_name":
        if operator == "CONTAINS":
            return Q(first_name__icontains=value) | Q(last_name__icontains=value)
        if operator == "EQUALS":
            return Q(first_name__iexact=value) | Q(last_name__iexact=value)
        raise ValidationError({"ruleConfig": "full_name supports EQUALS and CONTAINS only."})

    orm_field = FIELD_MAP[field]
    if operator in TEXT_OPERATORS:
        lookup = orm_field + TEXT_OPERATORS[operator]
        q = Q(**{lookup: value})
        return ~q if operator == "NOT_EQUALS" else q
    if operator in COMPARISON_OPERATORS:
        return Q(**{orm_field + COMPARISON_OPERATORS[operator]: value})
    if operator == "IN":
        if not isinstance(value, list):
            raise ValidationError({"ruleConfig": "IN operator requires a list value."})
        return Q(**{orm_field + "__in": value})
    if operator == "IS_EMPTY":
        return Q(**{orm_field + "__isnull": True}) | Q(**{orm_field: ""})
    if operator == "IS_NOT_EMPTY":
        return Q(**{orm_field + "__isnull": False}) & ~Q(**{orm_field: ""})
    raise ValidationError({"ruleConfig": f"Unsupported operator: {operator}."})


def rule_config_to_q(rule_config: Dict):
    q = Q()
    groups = rule_config.get("groups") or []
    for group in groups:
        rules = group.get("rules") or []
        conjunction = str(group.get("conjunction") or "AND").upper()
        group_q = Q()
        first = True
        for rule in rules:
            rule_q = _rule_to_q(rule)
            if first:
                group_q = rule_q
                first = False
            elif conjunction == "OR":
                group_q |= rule_q
            else:
                group_q &= rule_q
        if not first:
            q &= group_q
    return q


def predefined_codes_to_q(codes: Iterable[str]):
    q = Q()
    first = True
    for code in codes or []:
        clean = str(code).strip().upper()
        if not clean:
            continue
        definition = PREDEFINED_FILTERS.get(clean)
        if not definition:
            raise ValidationError({"predefinedCodes": f"Unknown predefined filter: {clean}."})
        next_q = definition["query"]()
        if first:
            q = next_q
            first = False
        else:
            q |= next_q
    return q


def apply_filter_config(queryset, predefined_codes=None, rule_config=None):
    query = Q()
    has_any = False
    if predefined_codes:
        query &= predefined_codes_to_q(predefined_codes)
        has_any = True
    if rule_config and (rule_config.get("groups") or []):
        query &= rule_config_to_q(rule_config)
        has_any = True
    return queryset.filter(query).distinct() if has_any else queryset


class EmployeeSegmentService:
    @staticmethod
    def list_segments(company, params):
        queryset = (
            EmployeeSegment.objects.filter(company=company, is_active=True)
            .select_related("employee_filter", "company")
            .order_by("title")
        )
        search = (params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(code__icontains=search))
        source = (params.get("sourceMode") or params.get("source") or "").strip().upper()
        if source in EmployeeSegment.SourceMode.values:
            queryset = queryset.filter(source_mode=source)
        return queryset

    @staticmethod
    def get_segment(company, segment_id):
        return get_object_or_404(
            EmployeeSegment.objects.select_related("employee_filter", "company"),
            id=segment_id,
            company=company,
            is_active=True,
        )

    @staticmethod
    def segment_queryset(company, segment):
        if segment.source_mode == EmployeeSegment.SourceMode.MANUAL:
            employee_ids = EmployeeSegmentMember.objects.filter(
                segment=segment,
                is_active=True,
            ).values("employee_id")
            return base_employee_queryset(company).filter(id__in=employee_ids)
        if segment.employee_filter:
            meta = segment.employee_filter.meta_data or {}
            return apply_filter_config(
                base_employee_queryset(company),
                meta.get("predefined_codes", []),
                meta.get("rule_config", {}),
            )
        return apply_filter_config(base_employee_queryset(company), [], segment.rule_config or {})

    @staticmethod
    def create_segment(company, data, user=None):
        code = data["code"]
        if EmployeeSegment.objects.filter(company=company, code__iexact=code, is_active=True).exists():
            raise ValidationError({"code": "Segment code already exists."})
        employee_filter = None
        if data.get("employeeFilterId"):
            employee_filter = EmployeeFilterService.get_filter(company, data["employeeFilterId"])

        with transaction.atomic():
            segment = EmployeeSegment.objects.create(
                company=company,
                title=data["segmentTitle"],
                code=code,
                source_mode=data["sourceMode"],
                employee_filter=employee_filter,
                rule_config=data.get("ruleConfig") or {},
                created_by=actor_id(user),
                updated_by=actor_id(user),
            )
            EmployeeSegmentService._replace_manual_members(segment, data.get("employeeIds", []))
            segment.member_count = EmployeeSegmentService.segment_queryset(company, segment).count()
            segment.save(update_fields=["member_count", "updated_at"])
        return EmployeeSegmentService.get_segment(company, segment.id)

    @staticmethod
    def update_segment(company, segment_id, data, user=None):
        segment = EmployeeSegmentService.get_segment(company, segment_id)
        code = data.get("code", segment.code)
        if EmployeeSegment.objects.filter(company=company, code__iexact=code, is_active=True).exclude(id=segment.id).exists():
            raise ValidationError({"code": "Segment code already exists."})
        employee_filter = segment.employee_filter
        if "employeeFilterId" in data:
            employee_filter = (
                EmployeeFilterService.get_filter(company, data["employeeFilterId"])
                if data["employeeFilterId"]
                else None
            )
        with transaction.atomic():
            segment.title = data.get("segmentTitle", segment.title)
            segment.code = code
            segment.source_mode = data.get("sourceMode", segment.source_mode)
            segment.employee_filter = employee_filter
            segment.rule_config = data.get("ruleConfig", segment.rule_config or {})
            segment.updated_by = actor_id(user)
            segment.save()
            if "employeeIds" in data:
                EmployeeSegmentService._replace_manual_members(segment, data["employeeIds"])
            segment.member_count = EmployeeSegmentService.segment_queryset(company, segment).count()
            segment.save(update_fields=["member_count", "updated_at"])
        return EmployeeSegmentService.get_segment(company, segment.id)

    @staticmethod
    def _replace_manual_members(segment, employee_ids: List[str]):
        if segment.source_mode != EmployeeSegment.SourceMode.MANUAL:
            EmployeeSegmentMember.objects.filter(segment=segment).update(is_active=False)
            return
        EmployeeSegmentMember.objects.filter(segment=segment).update(is_active=False)
        employees = Employee.objects.filter(company=segment.company, id__in=employee_ids, is_active=True)
        found = {str(emp.id): emp for emp in employees}
        missing = sorted(set(employee_ids) - set(found.keys()))
        if missing:
            raise ValidationError({"employeeIds": f"Employees not found for this company: {', '.join(missing)}"})
        for employee in found.values():
            EmployeeSegmentMember.objects.update_or_create(
                segment=segment,
                employee=employee,
                defaults={"is_active": True},
            )

    @staticmethod
    def delete_segment(company, segment_id, user=None):
        segment = EmployeeSegmentService.get_segment(company, segment_id)
        with transaction.atomic():
            segment.is_active = False
            segment.updated_by = actor_id(user)
            segment.save(update_fields=["is_active", "updated_by", "updated_at"])

    @staticmethod
    def duplicate_segment(company, segment_id, user=None):
        source = EmployeeSegmentService.get_segment(company, segment_id)
        base_code = slugify(f"{source.code}_copy").replace("-", "_").upper()[:50]
        code = base_code
        suffix = 1
        while EmployeeSegment.objects.filter(company=company, code__iexact=code).exists():
            suffix += 1
            code = f"{base_code[:45]}_{suffix}"
        employee_ids = list(source.member_links.filter(is_active=True).values_list("employee_id", flat=True))
        return EmployeeSegmentService.create_segment(
            company,
            {
                "segmentTitle": f"{source.title} (Copy)",
                "code": code,
                "sourceMode": source.source_mode,
                "employeeFilterId": source.employee_filter_id,
                "ruleConfig": source.rule_config or {},
                "employeeIds": [str(item) for item in employee_ids],
            },
            user=user,
        )


class EmployeeFilterService:
    @staticmethod
    def list_filters(company, params):
        queryset = EmployeeFilter.objects.filter(company_id=company.id, is_active=True).order_by("name")
        search = (params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(code__icontains=search))
        return queryset

    @staticmethod
    def get_filter(company, filter_id):
        return get_object_or_404(
            EmployeeFilter,
            id=filter_id,
            company_id=company.id,
            is_active=True,
        )

    @staticmethod
    def create_filter(company, data, user=None):
        code = data["code"]
        if EmployeeFilter.objects.filter(company_id=company.id, code__iexact=code, is_active=True).exists():
            raise ValidationError({"code": "Filter code already exists."})
        queryset = apply_filter_config(
            base_employee_queryset(company),
            data.get("predefinedCodes", []),
            data.get("ruleConfig", {}),
        )
        meta_data = {
            "predefined_codes": data.get("predefinedCodes", []),
            "rule_config": data.get("ruleConfig", {}),
            "save_shared": data.get("saveShared", False),
        }
        with transaction.atomic():
            employee_filter = EmployeeFilter.objects.create(
                company_id=company.id,
                code=code,
                name=data["filterName"],
                filter_type=EmployeeFilter.FilterType.DYNAMIC,
                description=data.get("description"),
                is_system=bool(data.get("saveShared", False)),
                member_count=queryset.count(),
                meta_data=meta_data,
                created_by=actor_id(user),
                updated_by=actor_id(user),
            )
        return employee_filter

    @staticmethod
    def preview(company, predefined_codes=None, rule_config=None, employee_ids=None):
        if employee_ids is not None:
            queryset = base_employee_queryset(company).filter(id__in=employee_ids)
        else:
            queryset = apply_filter_config(base_employee_queryset(company), predefined_codes or [], rule_config or {})
        return queryset, queryset.count()
