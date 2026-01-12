from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import (
    RoleCreate, RoleUpdate, RoleInDB,
    PermissionCreate, PermissionInDB,
    UserRoleUpdate, UserWithRoles
)
from app.dependencies import require_admin
from app.crud import (
    create_role, get_roles, update_role, delete_role,
    create_permission, get_permissions,
    update_user_roles, get_user_by_id
)
from app.models import User

router = APIRouter(prefix="/admin", tags=["administration"])


# Роли
@router.post("/roles", response_model=RoleInDB, status_code=status.HTTP_201_CREATED)
def create_new_role(
        role: RoleCreate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    return create_role(db, role)


@router.get("/roles", response_model=List[RoleInDB])
def read_roles(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    return get_roles(db, skip=skip, limit=limit)


@router.put("/roles/{role_id}", response_model=RoleInDB)
def update_existing_role(
        role_id: int,
        role_update: RoleUpdate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    updated_role = update_role(db, role_id, role_update)
    if not updated_role:
        raise HTTPException(status_code=404, detail="Роль не найдена")
    return updated_role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_role(
        role_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    success = delete_role(db, role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Роль не найдена")


# Разрешения
@router.post("/permissions", response_model=PermissionInDB, status_code=status.HTTP_201_CREATED)
def create_new_permission(
        permission: PermissionCreate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    return create_permission(db, permission)


@router.get("/permissions", response_model=List[PermissionInDB])
def read_permissions(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    return get_permissions(db, skip=skip, limit=limit)


# Управление ролями пользователей
@router.put("/users/{user_id}/roles", response_model=UserWithRoles)
def update_user_roles_admin(
        user_id: int,
        user_role_update: UserRoleUpdate,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    user = update_user_roles(db, user_id, user_role_update.role_ids)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user_data = UserWithRoles.from_orm(user)
    user_data.roles = [role.name for role in user.roles]
    return user_data


@router.get("/users/{user_id}", response_model=UserWithRoles)
def read_user_admin(
        user_id: int,
        current_user: User = Depends(require_admin),
        db: Session = Depends(get_db)
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user_data = UserWithRoles.from_orm(user)
    user_data.roles = [role.name for role in user.roles]
    return user_data