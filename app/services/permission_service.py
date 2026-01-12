from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.models import Permission, Role, User


class PermissionService:
    def __init__(self, db: Session):
        self.db = db

    def check_access(self, user_id: int, resource: str, action: str) -> bool:
        """Проверяет доступ пользователя к ресурсу"""

        user = self.db.query(User).filter(User.id == user_id, User.is_active == True).first()

        if not user:
            return False

        # Проверяем каждую роль пользователя
        for role in user.roles:
            for permission in role.permissions:
                if (permission.resource == resource and
                        permission.action == action):
                    return True

        return False

    def get_user_permissions(self, user_id: int) -> List[Dict]:
        """Получает все разрешения пользователя"""

        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return []

        permissions = []
        for role in user.roles:
            for permission in role.permissions:
                permissions.append({
                    "name": permission.name,
                    "resource": permission.resource,
                    "action": permission.action,
                    "role": role.name
                })

        return permissions

    def create_default_permissions(self):
        """Создает стандартные разрешения"""
        default_permissions = [
            {"name": "users:read", "resource": "users", "action": "read", "description": "Чтение пользователей"},
            {"name": "users:write", "resource": "users", "action": "write",
             "description": "Редактирование пользователей"},
            {"name": "users:delete", "resource": "users", "action": "delete", "description": "Удаление пользователей"},
            {"name": "roles:manage", "resource": "roles", "action": "manage", "description": "Управление ролями"},
            {"name": "permissions:manage", "resource": "permissions", "action": "manage",
             "description": "Управление разрешениями"},
        ]

        for perm_data in default_permissions:
            existing = self.db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not existing:
                permission = Permission(**perm_data)
                self.db.add(permission)

        self.db.commit()

    def create_default_roles(self):
        """Создает стандартные роли"""
        # Роль администратора
        admin_role = self.db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(
                name="admin",
                description="Администратор системы",
                is_system=True
            )
            self.db.add(admin_role)
            self.db.commit()
            self.db.refresh(admin_role)

            # Добавляем все разрешения к роли администратора
            all_permissions = self.db.query(Permission).all()
            admin_role.permissions = all_permissions
            self.db.commit()

        # Роль пользователя
        user_role = self.db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            user_role = Role(
                name="user",
                description="Обычный пользователь",
                is_system=True
            )
            self.db.add(user_role)
            self.db.commit()