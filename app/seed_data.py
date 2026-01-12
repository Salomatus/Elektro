from sqlalchemy.orm import Session
from database import SessionLocal
from services.permission_service import PermissionService
from crud import create_user
from schemas import UserCreate


def seed_database():
    db = SessionLocal()

    try:
        # Создаем стандартные разрешения
        permission_service = PermissionService(db)
        permission_service.create_default_permissions()
        permission_service.create_default_roles()

        # Создаем тестового администратора
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            admin_data = UserCreate(
                email="admin@example.com",
                first_name="Админ",
                last_name="Админов",
                middle_name="Админович",
                password="Admin123!",
                password_confirm="Admin123!"
            )
            admin_user = create_user(db, admin_data)

            # Назначаем роль администратора
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if admin_role:
                admin_user.roles = [admin_role]
                db.commit()

        # Создаем тестового пользователя
        test_user = db.query(User).filter(User.email == "user@example.com").first()
        if not test_user:
            user_data = UserCreate(
                email="user@example.com",
                first_name="Иван",
                last_name="Иванов",
                middle_name="Иванович",
                password="User123!",
                password_confirm="User123!"
            )
            create_user(db, user_data)

        print("База данных успешно заполнена тестовыми данными")

    except Exception as e:
        print(f"Ошибка при заполнении базы данных: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()