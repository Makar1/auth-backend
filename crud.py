from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate
from auth import get_password_hash


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user_data: UserCreate):
    hashed_pw = get_password_hash(user_data.password)

    new_user = User(username=user_data.username, hashed_password=hashed_pw, role_id=1)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user