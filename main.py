from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import engine, SessionLocal
from schemas import UserCreate, UserResponse, UserLogin, Token
from auth import verify_password, create_access_token
import crud

app = FastAPI(title="RBAC Auth API")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db=db, user_data=user)


# ... (твой предыдущий код с импортами и get_db) ...

# ⬇️ ДОБАВИТЬ ВОТ ЭТОТ БЛОК ⬇️




@app.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Аутентификация пользователя.
    Принимает email и пароль -> Возвращает JWT токен.
    """

    # 1. Ищем пользователя по email
    db_user = crud.get_user_by_email(db, email=user_data.email)

    # Если пользователя нет ИЛИ пароль неверный -> Ошибка 401 (Unauthorized)
    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Если пользователь отключен (soft delete) -> Ошибка 400
    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # 2. Создаем токен
    # Мы кладем email пользователя в поле "sub" (стандарт JWT)
    access_token = create_access_token(data={"sub": db_user.email})

    # 3. Возвращаем токен
    return {"access_token": access_token, "token_type": "bearer"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)