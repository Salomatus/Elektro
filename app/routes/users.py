from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import UserInDB, UserUpdate, UserWithRoles
from app.dependencies import get_current_active_user
from app.crud import (
    get_user_by_id, update_user, soft_delete_user,
    get_users as crud_get_users
)
from app.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserWithRoles)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    user_data = UserWithRoles.from_orm(current_user)
    user_data.roles = [role.name for role in current_user.roles]
    return user_data


@router.put("/me", response_model=UserInDB)
def update_current_user(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    updated_user = update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    success = soft_delete_user(db, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@router.get("/{user_id}", response_model=UserWithRoles)
def read_user(
        user_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    # Проверяем права на просмотр других пользователей
    if user_id != current_user.id and not current_user.has_permission("users:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра других пользователей"
        )

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user_data = UserWithRoles.from_orm(user)
    user_data.roles = [role.name for role in user.roles]
    return user_data


@router.get("/", response_model=List[UserWithRoles])
def get_users(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    # Проверяем права на просмотр всех пользователей
    if not current_user.has_permission("users:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )

    users = crud_get_users(db, skip=skip, limit=limit)
    result = []
    for user in users:
        user_data = UserWithRoles.from_orm(user)
        user_data.roles = [role.name for role in user.roles]
        result.append(user_data)

    return result