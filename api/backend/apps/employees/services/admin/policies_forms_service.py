import os
import uuid
from urllib.parse import urlparse

from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.employees.models.masters.audit_additions import FormCategory, PolicyCategory
from apps.employees.models.masters.organization import Company
from apps.employees.models.policies_forms import CompanyPolicyFormDocument


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


def model_for_kind(document_kind):
    if document_kind == CompanyPolicyFormDocument.DocumentKind.POLICY:
        return PolicyCategory
    return FormCategory


def category_field_for_kind(document_kind):
    if document_kind == CompanyPolicyFormDocument.DocumentKind.POLICY:
        return "policy_category"
    return "form_category"


class PolicyFormCategoryService:
    @staticmethod
    def list_categories(company, document_kind):
        model = model_for_kind(document_kind)
        return (
            model.objects.filter(company_id=company.id, is_active=True)
            .order_by("sort_order" if document_kind == "POLICY" else "name", "name")
        )

    @staticmethod
    def counts_by_category(company, document_kind):
        field = f"{category_field_for_kind(document_kind)}_id"
        rows = (
            CompanyPolicyFormDocument.objects.filter(
                company=company,
                document_kind=document_kind,
                is_active=True,
            )
            .values(field)
            .annotate(total=Count("id"))
        )
        return {row[field]: row["total"] for row in rows}

    @staticmethod
    def get_category(company, document_kind, category_id):
        model = model_for_kind(document_kind)
        category = model.objects.filter(
            id=category_id,
            company_id=company.id,
            is_active=True,
        ).first()
        if category:
            return category

        label = "policy" if document_kind == CompanyPolicyFormDocument.DocumentKind.POLICY else "form"
        raise ValidationError({
            "categoryId": (
                f"No active {label} category found for this company. "
                f"Use a category from {'mst_policy_category' if label == 'policy' else 'mst_form_category'}."
            )
        })

    @staticmethod
    def create_category(company, document_kind, data, user=None):
        model = model_for_kind(document_kind)
        code = data["code"]
        if model.objects.filter(company_id=company.id, code__iexact=code, is_active=True).exists():
            raise ValidationError({"code": "Category code already exists."})
        payload = {
            "company_id": company.id,
            "code": code,
            "name": data["name"],
            "created_by": actor_id(user),
            "updated_by": actor_id(user),
        }
        if hasattr(model, "sort_order"):
            payload["sort_order"] = data.get("sort_order", 0)
        with transaction.atomic():
            return model.objects.create(**payload)

    @staticmethod
    def update_category(company, document_kind, category_id, data, user=None):
        category = PolicyFormCategoryService.get_category(company, document_kind, category_id)
        code = data.get("code")
        if code:
            exists = (
                model_for_kind(document_kind)
                .objects.filter(company_id=company.id, code__iexact=code, is_active=True)
                .exclude(id=category.id)
                .exists()
            )
            if exists:
                raise ValidationError({"code": "Category code already exists."})
        with transaction.atomic():
            for field in ("name", "code", "sort_order"):
                if field in data and hasattr(category, field):
                    setattr(category, field, data[field])
            category.updated_by = actor_id(user)
            category.save()
        return category

    @staticmethod
    def delete_category(company, document_kind, category_id, user=None):
        category = PolicyFormCategoryService.get_category(company, document_kind, category_id)
        field = category_field_for_kind(document_kind)
        if CompanyPolicyFormDocument.objects.filter(
            company=company,
            document_kind=document_kind,
            is_active=True,
            **{field: category},
        ).exists():
            raise ValidationError({"category": "Cannot delete a category that has active documents."})
        with transaction.atomic():
            category.is_active = False
            category.updated_by = actor_id(user)
            category.save(update_fields=["is_active", "updated_by", "updated_at"])


class PolicyFormDocumentService:
    @staticmethod
    def list_documents(company, document_kind, params):
        queryset = (
            CompanyPolicyFormDocument.objects.filter(
                company=company,
                document_kind=document_kind,
                is_active=True,
            )
            .select_related("policy_category", "form_category", "company")
            .order_by("serial_no", "name")
        )
        search = (params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(
                Q(serial_no__icontains=search)
                | Q(name__icontains=search)
                | Q(description__icontains=search)
            )
        category_id = params.get("category_id") or params.get("categoryId")
        if category_id:
            queryset = queryset.filter(**{f"{category_field_for_kind(document_kind)}_id": category_id})
        status = params.get("status")
        if status:
            queryset = queryset.filter(status=str(status).upper())
        return queryset

    @staticmethod
    def dashboard(company, document_kind, params):
        documents = list(PolicyFormDocumentService.list_documents(company, document_kind, params))
        counts = PolicyFormCategoryService.counts_by_category(company, document_kind)
        categories = list(PolicyFormCategoryService.list_categories(company, document_kind))
        return categories, documents, counts

    @staticmethod
    def get_document(company, document_id):
        return get_object_or_404(
            CompanyPolicyFormDocument.objects.select_related(
                "policy_category",
                "form_category",
                "company",
            ),
            id=document_id,
            company=company,
            is_active=True,
        )

    @staticmethod
    def _save_file(company, document_kind, file):
        ext = os.path.splitext(file.name or "")[-1].lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"
        directory = f"companies/{company.id}/policies_forms/{document_kind.lower()}/"
        saved_path = default_storage.save(os.path.join(directory, unique_name), file)
        return default_storage.url(saved_path)

    @staticmethod
    def _delete_file(file_url):
        if not file_url:
            return
        parsed = urlparse(file_url)
        if parsed.scheme in {"http", "https"}:
            return
        path = file_url
        from django.conf import settings

        media_url = getattr(settings, "MEDIA_URL", "/media/")
        if path.startswith(media_url):
            path = path[len(media_url):]
        default_storage.delete(path)

    @staticmethod
    def _payload(company, data, user=None, existing=None):
        kind = data["documentKind"]
        category = PolicyFormCategoryService.get_category(company, kind, data["categoryId"])
        payload = {
            "document_kind": kind,
            "serial_no": data["serialNo"],
            "name": data["documentName"],
            "description": data.get("description"),
            "status": data.get("status", CompanyPolicyFormDocument.Status.DRAFT),
            "release_to_ess": data.get("releaseToEss", False),
            "enforce_policy": data.get("enforcePolicy", False),
            "target_filter_ids": [str(item) for item in data.get("targetFilterIds", [])],
            "updated_by": actor_id(user),
        }
        if kind == CompanyPolicyFormDocument.DocumentKind.POLICY:
            payload["policy_category"] = category
            payload["form_category"] = None
        else:
            payload["form_category"] = category
            payload["policy_category"] = None

        file = data.get("document")
        if file:
            payload["file_url"] = PolicyFormDocumentService._save_file(company, kind, file)
            payload["file_name"] = file.name[:255]
            payload["file_size_bytes"] = file.size
            payload["mime_type"] = getattr(file, "content_type", "")[:100]
        elif not existing:
            raise ValidationError({"document": "Upload a document file."})
        return payload

    @staticmethod
    def create_document(company, data, user=None):
        if CompanyPolicyFormDocument.objects.filter(
            company=company,
            document_kind=data["documentKind"],
            serial_no__iexact=data["serialNo"],
            is_active=True,
        ).exists():
            raise ValidationError({"serialNo": "Serial number already exists for this document type."})
        payload = PolicyFormDocumentService._payload(company, data, user=user)
        payload["company"] = company
        payload["created_by"] = actor_id(user)
        with transaction.atomic():
            return CompanyPolicyFormDocument.objects.create(**payload)

    @staticmethod
    def update_document(company, document_id, data, user=None):
        document = PolicyFormDocumentService.get_document(company, document_id)
        kind = data.get("documentKind", document.document_kind)
        serial_no = data.get("serialNo", document.serial_no)
        if CompanyPolicyFormDocument.objects.filter(
            company=company,
            document_kind=kind,
            serial_no__iexact=serial_no,
            is_active=True,
        ).exclude(id=document.id).exists():
            raise ValidationError({"serialNo": "Serial number already exists for this document type."})

        merged = {
            "documentKind": kind,
            "serialNo": serial_no,
            "documentName": data.get("documentName", document.name),
            "description": data.get("description", document.description),
            "categoryId": data.get(
                "categoryId",
                document.policy_category_id if kind == "POLICY" else document.form_category_id,
            ),
            "status": data.get("status", document.status),
            "releaseToEss": data.get("releaseToEss", document.release_to_ess),
            "enforcePolicy": data.get("enforcePolicy", document.enforce_policy),
            "targetFilterIds": data.get("targetFilterIds", document.target_filter_ids or []),
        }
        if data.get("document"):
            merged["document"] = data["document"]
        payload = PolicyFormDocumentService._payload(company, merged, user=user, existing=document)
        old_file_url = document.file_url if "file_url" in payload else None
        with transaction.atomic():
            for field, value in payload.items():
                setattr(document, field, value)
            document.save()
        if old_file_url:
            PolicyFormDocumentService._delete_file(old_file_url)
        return PolicyFormDocumentService.get_document(company, document.id)

    @staticmethod
    def delete_document(company, document_id, user=None):
        document = PolicyFormDocumentService.get_document(company, document_id)
        with transaction.atomic():
            document.is_active = False
            document.updated_by = actor_id(user)
            document.save(update_fields=["is_active", "updated_by", "updated_at"])
