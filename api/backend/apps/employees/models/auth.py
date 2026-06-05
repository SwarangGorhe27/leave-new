"""
Employee authentication models.

Tables:
  employee_auth                — Hashed password, MFA, lockout state
  employee_verification_tokens — Email/phone/OTP tokens
  login_history                — Session login/logout event log

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionBaseModel


# ---------------------------------------------------------------------------
# employee_auth
# ---------------------------------------------------------------------------


class EmployeeAuth(TransactionBaseModel):
    """
    Authentication state for an employee.

    SECURITY:
      password_hash MUST contain bcrypt / argon2 hash — never plain text.
      mfa_secret MUST be stored encrypted at rest.
      session_token_hash stores only the hash — never the raw token.

    Lockout:
      failed_login_attempts / max_failed_attempts drive auto-lockout.
      account_locked + unlock_at support time-based auto-unlock via scheduler.
    """

    class MFAType(models.TextChoices):
        TOTP = "TOTP", "TOTP"
        SMS = "SMS", "SMS"
        EMAIL = "EMAIL", "Email"
        NONE = "NONE", "None"

    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="auth",
    )

    # -------------------------------------------------------- password
    password_hash = models.TextField()
    password_salt = models.CharField(max_length=64, blank=True, null=True)
    last_password_changed_at = models.DateTimeField(auto_now_add=True)
    password_expiry_at = models.DateTimeField(null=True, blank=True)
    must_change_password = models.BooleanField(default=True)

    # -------------------------------------------------------- MFA
    mfa_enabled = models.BooleanField(default=False)
    mfa_type = models.CharField(
        max_length=20,
        choices=MFAType.choices,
        default=MFAType.NONE,
    )
    mfa_secret = models.TextField(
        blank=True,
        null=True,
        help_text="Encrypted TOTP seed — must be encrypted at rest",
    )

    # -------------------------------------------------------- lockout
    failed_login_attempts = models.SmallIntegerField(default=0)
    max_failed_attempts = models.SmallIntegerField(default=5)
    account_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_reason = models.CharField(max_length=100, blank=True, null=True)
    unlock_at = models.DateTimeField(null=True, blank=True)

    # -------------------------------------------------------- session
    last_login_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(
        protocol="both", unpack_ipv4=True, null=True, blank=True
    )
    session_token_hash = models.TextField(blank=True, null=True)

    # -------------------------------------------------------- status
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_auth"
        verbose_name = "Employee Auth"
        verbose_name_plural = "Employee Auths"
        indexes = [
            models.Index(fields=["employee"], name="idx_emp_auth_employee"),
            # Partial index: locked accounts only — used by auto-unlock scheduler
            models.Index(
                fields=["account_locked", "unlock_at"],
                name="idx_emp_auth_locked_unlock",
                condition=models.Q(account_locked=True),
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["employee"], name="uq_emp_auth_employee"),
        ]

    def __str__(self) -> str:
        return f"Auth — {self.employee_id}"


# ---------------------------------------------------------------------------
# employee_verification_tokens
# ---------------------------------------------------------------------------


class EmployeeVerificationToken(TransactionBaseModel):
    """
    Short-lived verification tokens for password reset, email verify, MFA OTP etc.

    SECURITY:
      token_hash MUST be SHA-256 hash of the raw token — never store raw.
      expires_at MUST be enforced in the application layer.
    """

    class TokenType(models.TextChoices):
        PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"
        EMAIL_VERIFY = "EMAIL_VERIFY", "Email Verify"
        MFA_OTP = "MFA_OTP", "MFA OTP"
        INVITE = "INVITE", "Invite"
        REFRESH = "REFRESH", "Refresh"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="verification_tokens",
    )
    token_hash = models.CharField(max_length=128, unique=True)
    token_type = models.CharField(max_length=30, choices=TokenType.choices)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    is_used = models.BooleanField(default=False)
    issued_ip = models.GenericIPAddressField(
        protocol="both", unpack_ipv4=True, null=True, blank=True
    )
    consumed_ip = models.GenericIPAddressField(
        protocol="both", unpack_ipv4=True, null=True, blank=True
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employee_verification_tokens"
        verbose_name = "Employee Verification Token"
        verbose_name_plural = "Employee Verification Tokens"
        indexes = [
            # Fast token validation on hot path — partial: unused + not expired
            models.Index(
                fields=["token_hash"],
                name="idx_emp_vtoken_hash_active",
                condition=models.Q(is_used=False),
            ),
            models.Index(
                fields=["employee", "token_type"],
                name="idx_emp_vtoken_employee_type",
            ),
        ]
        constraints = [
            models.UniqueConstraint(fields=["token_hash"], name="uq_emp_vtoken_hash"),
        ]

    def __str__(self) -> str:
        return f"Token [{self.token_type}] — {self.employee_id}"


# ---------------------------------------------------------------------------
# login_history
# ---------------------------------------------------------------------------


class LoginHistory(TransactionBaseModel):
    """
    Session login / logout event log.

    High-volume INSERT-only table.
    Indexed on (employee_id, login_at DESC) for history queries.
    Partial index on FAILED logins for brute-force detection.

    NOTE: No CASCADE delete — audit log must be retained after employee deactivation.
    """

    class DeviceType(models.TextChoices):
        WEB = "WEB", "Web"
        MOBILE_IOS = "MOBILE_IOS", "Mobile iOS"
        MOBILE_ANDROID = "MOBILE_ANDROID", "Mobile Android"
        DESKTOP = "DESKTOP", "Desktop"
        API = "API", "API"

    class LoginStatus(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        LOCKED = "LOCKED", "Locked"
        MFA_PENDING = "MFA_PENDING", "MFA Pending"
        MFA_FAILED = "MFA_FAILED", "MFA Failed"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        db_column="employee_id",
        related_name="login_history",
    )
    login_at = models.DateTimeField(auto_now_add=True, db_index=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    session_id = models.UUIDField()
    ip_address = models.GenericIPAddressField(protocol="both", unpack_ipv4=True)
    user_agent = models.TextField(blank=True, null=True)
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        blank=True,
        null=True,
    )
    login_status = models.CharField(max_length=20, choices=LoginStatus.choices)
    failure_reason = models.CharField(max_length=100, blank=True, null=True)
    mfa_used = models.BooleanField(default=False)
    geolocation = models.JSONField(
        null=True,
        blank=True,
        help_text="Derived geo: {city, country, lat, lng}",
    )

    class Meta:
        db_table = "login_history"
        verbose_name = "Login History"
        verbose_name_plural = "Login Histories"
        indexes = [
            models.Index(
                fields=["employee", "login_at"],
                name="idx_login_history_employee_at",
            ),
            # Partial: failed logins for brute-force detection
            models.Index(
                fields=["login_at"],
                name="idx_login_history_failed_at",
                condition=models.Q(login_status="FAILED"),
            ),
        ]

    def __str__(self) -> str:
        return f"Login [{self.login_status}] — {self.employee_id} at {self.login_at}"
