from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role = (getattr(user, "role", "") or "").lower()
        if role == "manager":
            return True
        return user.groups.filter(name__iexact="managers").exists()


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(user.is_staff or (getattr(user, "role", "") or "").lower() == "admin")
