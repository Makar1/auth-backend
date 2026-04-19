from pydantic import BaseModel, EmailStr, model_validator


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    patronymic: str | None = None
    email: EmailStr
    password: str
    password_confirm: str

    @model_validator(mode='before')
    def check_passwords_match(cls, values):
        pw1, pw2 = values.get('password'), values.get('password_confirm')
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError('Passwords do not match')
        return values



class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    is_deleted: bool
    role_id: int

    class Config:
        from_attributes = True

class LogoutRequest(BaseModel):
    refresh_token: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    email: EmailStr | None = None

    class Config:
        extra = "forbid"


class PermissionResponse(BaseModel):
    id: int
    role_id: int
    resource_id: int
    action_id: int
    role_name: str
    resource_name: str
    action_name: str

    class Config:
        from_attributes = True


class PermissionCreate(BaseModel):
    role: str       # "manager"
    resource: str   # "product"
    action: str     # "read"


class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class AssignRoleRequest(BaseModel):
    role_name: str