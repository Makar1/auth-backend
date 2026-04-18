from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


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
    full_name: str | None = None
    is_deleted: bool
    role_id: int

    class Config:
        from_attributes = True