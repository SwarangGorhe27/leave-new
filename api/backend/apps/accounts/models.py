from django.db import models

# Create your models here.
import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True)

    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
    )

    mobile_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    # ------------------------------------------------ auth flags

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    is_locked = models.BooleanField(default=False)

    password_expiry_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    failed_login_attempts = models.PositiveIntegerField(default=0)

    # ------------------------------------------------ audit

    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    last_login_device = models.TextField(
        null=True,
        blank=True,
    )

    # ------------------------------------------------ MFA

    is_mfa_enabled = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email

