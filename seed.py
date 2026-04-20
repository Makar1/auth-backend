import sys
import os

sys.path.append(os.path.dirname(__file__))

from database import SessionLocal
from models import User, Role, Resource, Action, Permission
from security import get_password_hash


def seed():
    db = SessionLocal()

    try:
        for role_name in ["admin", "manager", "user"]:
            if not db.query(Role).filter(Role.name == role_name).first():
                db.add(Role(name=role_name))
        db.commit()

        for name in ["product", "order", "user"]:
            if not db.query(Resource).filter(Resource.name == name).first():
                db.add(Resource(name=name))
        db.commit()

        for name in ["read", "create", "update", "delete"]:
            if not db.query(Action).filter(Action.name == name).first():
                db.add(Action(name=name))
        db.commit()

        permission_matrix = {
            "admin": {
                "product": ["read", "create", "update", "delete"],
                "order": ["read", "create", "update", "delete"],
                "user": ["read", "create", "update", "delete"],
            },
            "manager": {
                "product": ["read", "create"],
                "order": ["read", "create"],
            },
            "user": {
                "product": ["read"],
            },
        }

        for role_name, resources in permission_matrix.items():
            role = db.query(Role).filter(Role.name == role_name).first()
            for resource_name, action_names in resources.items():
                resource = db.query(Resource).filter(Resource.name == resource_name).first()
                for action_name in action_names:
                    action = db.query(Action).filter(Action.name == action_name).first()
                    if not db.query(Permission).filter(
                        Permission.role_id == role.id,
                        Permission.resource_id == resource.id,
                        Permission.action_id == action.id,
                    ).first():
                        db.add(Permission(
                            role_id=role.id,
                            resource_id=resource.id,
                            action_id=action.id
                        ))
        db.commit()

        users_to_create = [
            {"email": "admin@test.com", "password": "Admin1234", "first_name": "Admin", "last_name": "User", "role_name": "admin"},
            {"email": "manager@test.com", "password": "Manager1234", "first_name": "Manager", "last_name": "User", "role_name": "manager"},
            {"email": "viewer@test.com", "password": "Viewer1234", "first_name": "Viewer", "last_name": "User", "role_name": "user"},
        ]

        for u in users_to_create:
            if db.query(User).filter(User.email == u["email"]).first():
                continue
            role = db.query(Role).filter(Role.name == u["role_name"]).first()
            db.add(User(
                email=u["email"],
                first_name=u["first_name"],
                last_name=u["last_name"],
                patronymic=None,
                hashed_password=get_password_hash(u["password"]),
                is_deleted=False,
                role_id=role.id
            ))
        db.commit()

        print("Все готово! База заполнена тестовыми данными.")

    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
