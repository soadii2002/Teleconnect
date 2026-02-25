import re
from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum
from uuid import UUID
from datetime import datetime


class GenderEnum(str, Enum):
    male = "male"
    female = "female"


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    gender: GenderEnum
    phone_number: str
    city: str

    @field_validator("phone_number")
    @classmethod
    def validate_egyptian_phone(cls, v):
        pattern = r"^(010|011|012|015)\d{8}$"
        if not re.match(pattern, v):
            raise ValueError(
                "Phone number must be 11 digits and start with 010, 011, 012, or 015"
            )
        return v

    @field_validator("city")
    @classmethod
    def validate_city_not_empty(cls, v):
        if not v.strip():
            raise ValueError("City cannot be empty")
        return v.strip()

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip()


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    gender: GenderEnum
    phone_number: str
    city: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse