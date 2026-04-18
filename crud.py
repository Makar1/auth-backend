from sqlalchemy.orm import Session
from models import User, Role, RefreshToken
from schemas import UserCreate
from security import get_password_hash
from datetime import datetime, timezone, timedelta
import secrets


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(
        User.email == email,
        User.is_deleted == False
    ).first()


def create_user(db: Session, user_data: UserCreate, role_name: str = "user"):


    from models import Role

    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise ValueError(f"Role '{role_name}' not found")

    hashed_pw = get_password_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_pw,
        is_deleted=False,
        role_id=role.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def create_refresh_token_record(db: Session, user_id: int):

    token_str = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    db_token = RefreshToken(
        token=token_str,
        user_id=user_id,
        expires_at=expires_at
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return token_str