from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, get_db
from auth import get_current_user, create_access_token, require_role, require_permission
from security import verify_password
from models import User
import crud
import models
from schemas import (
    UserCreate, UserResponse, UserLogin, Token,
    LogoutRequest, UserUpdate,
    PermissionCreate, PermissionResponse, RoleResponse, AssignRoleRequest
)


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

@app.post("/logout")
def logout(
    request: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not crud.delete_refresh_token(db, token=request.refresh_token, user_id=current_user.id):
        raise HTTPException(
            status_code=400,
            detail="Invalid or already revoked token"
        )
    return {"detail": "Successfully logged out"}

@app.patch("/users/me", response_model=UserResponse)
def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        updated_user = crud.update_user(db, user=current_user, update_data=update_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):

    crud.soft_delete_user(db, user=current_user)
    return None

@app.get("/admin/roles", response_model=list[RoleResponse])
def get_roles(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return crud.get_all_roles(db)

@app.get("/admin/permissions")
def get_permissions(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    perms = crud.get_all_permissions(db)
    return [
        {
            "id": p.id,
            "role": p.role.name,
            "resource": p.resource.name,
            "action": p.action.name,
        }
        for p in perms
    ]


@app.post("/admin/permissions", status_code=201)
def create_permission(
    data: PermissionCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    try:
        perm = crud.create_permission(db, data.role, data.resource, data.action)
        return {
            "id": perm.id,
            "role": data.role,
            "resource": data.resource,
            "action": data.action,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/admin/permissions/{permission_id}", status_code=204)
def delete_permission(
    permission_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    if not crud.delete_permission(db, permission_id):
        raise HTTPException(status_code=404, detail="Permission not found")


@app.patch("/admin/users/{user_id}/role", response_model=UserResponse)
def assign_role(
    user_id: int,
    data: AssignRoleRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    try:
        return crud.assign_role(db, user_id, data.role_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


MOCK_PRODUCTS = [
    {"id": 1, "name": "Ноутбук Pro 15", "price": 89990},
    {"id": 2, "name": "Механическая клавиатура", "price": 7500},
    {"id": 3, "name": "Монитор 27 дюймов", "price": 32000},
]

MOCK_ORDERS = [
    {"id": 101, "product_id": 1, "status": "delivered", "total": 89990},
    {"id": 102, "product_id": 3, "status": "pending",   "total": 32000},
]


@app.get("/products")
def get_products(current_user: User = Depends(require_permission("product", "read"))):
    return {"products": MOCK_PRODUCTS}


@app.post("/products")
def create_product(current_user: User = Depends(require_permission("product", "create"))):
    return {"message": "Product created (mock)", "created_by": current_user.email}


@app.get("/orders")
def get_orders(current_user: User = Depends(require_permission("order", "read"))):
    return {"orders": MOCK_ORDERS}


@app.post("/orders")
def create_order(current_user: User = Depends(require_permission("order", "create"))):
    return {"message": "Order created (mock)", "created_by": current_user.email}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)