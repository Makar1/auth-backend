from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, SessionLocal, get_db
from schemas import UserCreate, UserResponse, UserLogin, Token
from auth import get_current_user, create_access_token, require_role
from security import verify_password
from models import User
import crud
import models
import secrets


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="RBAC Auth API")


@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db=db, user_data=user)



@app.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user_data.email)

    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if db_user.is_deleted:
        raise HTTPException(status_code=400, detail="User account has been deleted")

    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = crud.create_refresh_token_record(db, user_id=db_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }


@app.get("/admin/dashboard")
def admin_dashboard(current_user: User = Depends(require_role("admin"))):

    return {
        "message": "Welcome to the Admin Panel!",
        "admin_email": current_user.email,
        "secret_data": "Засекреченая информация"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)