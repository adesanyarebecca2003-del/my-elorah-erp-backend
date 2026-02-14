from pydantic import BaseModel, validator
from pydantic import BaseModel, Field

import re


class LoginSchema(BaseModel):
    username: str
    password: str = Field(min_length=8, max_length=72)


class LoginResponse(BaseModel):
    username: str
    is_admin: bool
    permissions: list[str] = []


class CreateUserRequest(BaseModel):
    username: str
    password: str = Field(..., min_length=8)

    @validator("password")
    def validate_password(cls, v: str):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 characters")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain a number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain a special character")

        return v


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: str
    username: str
    is_admin: bool
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    is_admin: bool
    permissions: list[str] = []