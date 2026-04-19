import sys
import os
sys.path.append(os.path.dirname(__file__))

from database import SessionLocal
from models import User, Role
from security import get_password_hash

def seed():
    db = SessionLocal()

    try:
        for role_name in ["admin", "manager", "user"]:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                db.add(Role(name=role_name))
                print(f"  + Роль '{role_name}' создана")
            else:
                print(f"  ✓ Роль '{role_name}' уже есть")
        db.commit()

        users_to_create = [
            {
                "email": "admin@test.com",
                "password": "Admin1234",
                "first_name": "Admin",
                "last_name": "User",
                "role_name": "admin"
            },
            {
                "email": "manager@test.com",
                "password": "Manager1234",
                "first_name": "Manager",
                "last_name": "User",
                "role_name": "manager"
            },
            {
                "email": "viewer@test.com",
                "password": "Viewer1234",
                "first_name": "Viewer",
                "last_name": "User",
                "role_name": "user"
            },
        ]

        for u in users_to_create:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                print(f"  ✓ {u['email']} уже существует")
                continue

            role = db.query(Role).filter(Role.name == u["role_name"]).first()
            new_user = User(
                email=u["email"],
                first_name=u["first_name"],
                last_name=u["last_name"],
                patronymic=None,
                hashed_password=get_password_hash(u["password"]),
                is_deleted=False,
                role_id=role.id
            )
            db.add(new_user)
            print(f"  + {u['email']} создан (роль: {u['role_name']})")

        db.commit()
        print("\nГотово!")
        print("\nТестовые пользователи:")
        print("  admin@test.com    / Admin1234    → роль: admin")
        print("  manager@test.com  / Manager1234  → роль: manager")
        print("  viewer@test.com   / Viewer1234   → роль: user")

    finally:
        db.close()

if __name__ == "__main__":
    seed()