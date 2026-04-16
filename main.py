from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from schemas import UserCreate, UserResponse, UserLogin, Token
from auth import get_current_user, create_access_token, verify_password, require_role
from models import User
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



@app.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):

    db_user = crud.get_user_by_email(db, email=user_data.email)

    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(data={"sub": db_user.email})

    return {"access_token": access_token, "token_type": "bearer"}


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