from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Проверяет, аутентифицирован ли пользователь
    в роли администратора или автора."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.user.is_superuser
        )
