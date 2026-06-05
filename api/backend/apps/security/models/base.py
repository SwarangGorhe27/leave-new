"""
Base model classes for the Security app.

Provides:
  SecurityBaseModel  — UUID PK + created_at / updated_at / deleted_at / is_active
"""

import uuid

from django.db import models


class SecurityBaseModel(models.Model):
    """
    Abstract base for all Security app models.

    Supplies:
      id          — UUID PK (auto-generated)
      created_at  — set once on INSERT
      updated_at  — updated on every SAVE
      deleted_at  — soft-delete timestamp (NULL = not deleted)
      is_active   — convenience flag (False = logically disabled)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True
