from sqlalchemy.orm import Session
from typing import Optional, List
from models import User, Role, Permission
from schemas import UserCreate, UserUpdate, RoleCreate, RoleUpdate, PermissionCreate
from auth import get_password_hash


# CRUD для пользователей
def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Добавляем базовую роль пользователя
    user_role = db.query(Role).filter(Role.name == "user").first()
    if user_role:
        db_user.roles.append(user_role)
        db.commit()
        db.refresh(db_user)

    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None


def soft_delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()


# CRUD для ролей
def create_role(db: Session, role: RoleCreate) -> Role:
    db_role = Role(
        name=role.name,
        description=role.description
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)

    # Добавляем разрешения
    if role.permission_ids:
        permissions = db.query(Permission).filter(Permission.id.in_(role.permission_ids)).all()
        db_role.permissions.extend(permissions)
        db.commit()
        db.refresh(db_role)

    return db_role


def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    return db.query(Role).filter(Role.name == name).first()


def get_role_by_id(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    return db.query(Role).offset(skip).limit(limit).all()


def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Optional[Role]:
    db_role = get_role_by_id(db, role_id)
    if not db_role:
        return None


def delete_role(db: Session, role_id: int) -> bool:
    db_role = get_role_by_id(db, role_id)
    if not db_role:
        return False


def update_user_roles(db: Session, user_id: int, role_ids: List[int]) -> Optional[User]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None


# CRUD для разрешений
def create_permission(db: Session, permission: PermissionCreate) -> Permission:
    db_permission = Permission(
        name=permission.name,
        description=permission.description,
        resource=permission.resource,
        action=permission.action
    )
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
    return db.query(Permission).filter(Permission.name == name).first()


def get_permissions(db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
    return db.query(Permission).offset(skip).limit(limit).all()
