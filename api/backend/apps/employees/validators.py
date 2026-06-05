from apps.employees.services.validators import *  # noqa: F401,F403

from rest_framework import serializers

from apps.employees.constants import ESSModule, IMMUTABLE_EMPLOYEE_FIELDS


def validate_certificate_upload(file):
    return validate_document_upload(file)


def validate_passport_document(file):
    return validate_passport_upload(file)


def validate_phone_number(value):
    return validate_mobile_number(value)


def validate_url_safe(value):
    return validate_url(value)


def validate_module_known(module):
    if module not in ESSModule.ALL:
        raise serializers.ValidationError(f"Unknown employee module: {module}")
    return module


def validate_no_immutable_fields(data):
    blocked = set(data or {}) & IMMUTABLE_EMPLOYEE_FIELDS
    if blocked:
        raise serializers.ValidationError(
            f"These fields cannot be changed by employee request: {', '.join(sorted(blocked))}"
        )
    return data


def validate_change_request_data_not_empty(data):
    if not data:
        raise serializers.ValidationError("request_data cannot be empty.")
    return data


def validate_experience_dates(start_date, end_date, is_current=False):
    if not start_date:
        raise serializers.ValidationError("start_date is required.")
    if not is_current and end_date and end_date < start_date:
        raise serializers.ValidationError("end_date cannot be before start_date.")
    return True
