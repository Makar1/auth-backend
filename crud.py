from sqlalchemy.orm import Session
from models import User, Role, RefreshToken, Resource, Action, Permission
from schemas import UserCreate, UserUpdate
from security import get_password_hash
from datetime import datetime, timezone, timedelta
import secrets
import hashlib


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(
        User.email == email,
        User.is_deleted == False
    ).first()


def create_user(db: Session, user_data: UserCreate, role_name: str = "user"):
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise ValueError(f"Role '{role_name}' not found")

    hashed_pw = get_password_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        patronymic=user_data.patronymic,
        hashed_password=hashed_pw,
        is_deleted=False,
        role_id=role.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def create_refresh_token_record(db: Session, user_id: int):

    raw_token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    db_token = RefreshToken(
        token=token_hash,
        user_id=user_id,
        expires_at=expires_at
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return raw_token


def delete_refresh_token(db: Session, token: str, user_id: int) -> bool:
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_hash,
        RefreshToken.user_id == user_id
    ).first()
    if db_token:
        db.delete(db_token)
        db.commit()
        return True
    return False


def update_user(db: Session, user: User, update_data: UserUpdate) -> User:
    update_dict = update_data.model_dump(exclude_unset=True)
    if "email" in update_dict and update_dict["email"] != user.email:
        existing = db.query(User).filter(
            User.email == update_dict["email"],
            User.id != user.id
        ).first()
        if existing:
            raise ValueError("Email already registered")
    for field, value in update_dict.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def soft_delete_user(db: Session, user: User) -> bool:
    user.is_deleted = True
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
    db.commit()
    return True


def has_permission(db: Session, user: User, resource_name: str, action_name: str) -> bool:
    result = (
        db.query(Permission)
        .join(Resource, Permission.resource_id == Resource.id)
        .join(Action, Permission.action_id == Action.id)
        .filter(
            Permission.role_id == user.role_id,
            Resource.name == resource_name,
            Action.name == action_name
        )
        .first()
    )
    return result is not None



def get_all_roles(db: Session):
    return db.query(Role).all()


def get_all_permissions(db: Session):
    return (
        db.query(Permission)
        .join(Role).join(Resource).join(Action)
        .all()
    )


def create_permission(db: Session, role_name: str, resource_name: str, action_name: str):
    role = db.query(Role).filter(Role.name == role_name).first()
    resource = db.query(Resource).filter(Resource.name == resource_name).first()
    action = db.query(Action).filter(Action.name == action_name).first()

    if not role:
        raise ValueError(f"Role '{role_name}' not found")
    if not resource:
        raise ValueError(f"Resource '{resource_name}' not found")
    if not action:
        raise ValueError(f"Action '{action_name}' not found")


    existing = db.query(Permission).filter(
        Permission.role_id == role.id,
        Permission.resource_id == resource.id,
        Permission.action_id == action.id,
    ).first()
    if existing:
        raise ValueError("Permission already exists")

    perm = Permission(role_id=role.id, resource_id=resource.id, action_id=action.id)
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return perm


def delete_permission(db: Session, permission_id: int) -> bool:
    perm = db.query(Permission).filter(Permission.id == permission_id).first()
    if not perm:
        return False
    db.delete(perm)
    db.commit()
    return True


def assign_role(db: Session, user_id: int, role_name: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise ValueError(f"Role '{role_name}' not found")
    user.role_id = role.id
    db.commit()
    db.refresh(user)
    return user