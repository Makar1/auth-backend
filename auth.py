from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordBearer
from database import SessionLocal
from fastapi import HTTPException, status, Depends
from models import User

from sqlalchemy.orm import joinedload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_password_hash(password: str) -> str:

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:

    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     import crud
#
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#
#     payload = verify_token(token)
#     if payload is None:
#         raise credentials_exception
#     email: str = payload.get("sub")
#     if email is None:
#         raise credentials_exception
#
#     db = SessionLocal()
#     try:
#         user = crud.get_user_by_email(db, email=email)
#         if user is None:
#             raise credentials_exception
#         return user
#     finally:
#         db.close()

def get_current_user(token: str = Depends(oauth2_scheme)):
    import crud  # Локальный импорт для разрыва цикла

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    db = SessionLocal()
    try:
    # 🔑 ИСПРАВЛЕНИЕ: joinedload заставляет загрузить роль сразу
        user = (db.query(User)
                .options(joinedload(User.role))  # ⬅️ ВОТ ЭТО РЕШАЕТ ПРОБЛЕМУ
                .filter(User.email == email)
                .first())

        if user is None:
            raise credentials_exception
        return user
    finally:
        db.close()


def require_role(required_role: str):


    def role_checker(current_user: User = Depends(get_current_user)):

        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role not assigned"
            )

        if current_user.role.name != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required role: {required_role}"
            )

        return current_user

    return role_checker