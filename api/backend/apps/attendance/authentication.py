"""
attendance/authentication.py

API key authentication for the ESSL agent ingest endpoint.

The agent sends:
    X-API-Key: <key>

The key is validated against AGENT_API_KEY in Django settings / .env.
This is intentionally simple — the ingest endpoint is internal only,
called by the ESSL agent on the same network, not exposed to the internet.

For multi-agent or per-client key management in future, replace this
with a database-backed APIKey model.
"""
import logging

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

log = logging.getLogger(__name__)


class AgentAPIKeyAuthentication(BaseAuthentication):
    """
    Validates the X-API-Key header against AGENT_API_KEY in settings.

    Returns (None, None) as the user — the agent is not a Django user.
    The view has no permission classes beyond authentication.

    Raises AuthenticationFailed on:
      - Missing header
      - Invalid key
    """

    HEADER = "HTTP_X_API_KEY"   # Django converts X-API-Key → HTTP_X_API_KEY

    def authenticate(self, request):
        api_key = request.META.get(self.HEADER)
        

        if not api_key:
            # Return None — DRF will try the next authentication class.
            # If no class succeeds, the request is treated as anonymous.
            # Since the view has no AllowAny permission, it will be rejected.
            return None

        expected_key = getattr(settings, "AGENT_API_KEY", None)

        if not expected_key:
            log.error(
                "AGENT_API_KEY is not configured in settings. "
                "All agent requests will be rejected."
            )
            raise AuthenticationFailed("Server misconfiguration — contact admin.")

        if api_key != expected_key:
            log.warning("Invalid API key received from %s", request.META.get("REMOTE_ADDR"))
            raise AuthenticationFailed("Invalid API key.")

        log.debug("Agent authenticated from %s", request.META.get("REMOTE_ADDR"))

        # Return (user=None, token=api_key)
        # user=None is fine — the ingest view does not need a Django user
        return (None, api_key)

    def authenticate_header(self, request):
        """Tells DRF what to put in the WWW-Authenticate header on 401."""
        return "X-API-Key"