from sqlalchemy.orm import Session
from models import User, Role
from schemas import UserCreate
from auth import get_password_hash


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


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
        is_active=True,
        role_id=role.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user