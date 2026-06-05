from django.db import models
from django_tenants.models import DomainMixin


class Domain(DomainMixin):

    class Meta:
        db_table = "domains"
