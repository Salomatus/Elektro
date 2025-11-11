from rest_framework import permissions


class IsActiveEmployee(permissions.BasePermission):
    """
    Разрешение только для активных сотрудников.
    В реальном приложении здесь должна быть проверка роли сотрудника.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active
