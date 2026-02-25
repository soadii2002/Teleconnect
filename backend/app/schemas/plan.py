from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class CategoryEnum(str, Enum):
    mobile = "mobile"
    internet = "internet"


class PlanCreate(BaseModel):
    name: str
    category: CategoryEnum
    description: Optional[str] = None
    price: float
    data_limit_gb: Optional[int] = None
    speed_mbps: Optional[int] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Plan name cannot be empty")
        return v.strip()

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than zero")
        return v


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    data_limit_gb: Optional[int] = None
    speed_mbps: Optional[int] = None


class PlanResponse(BaseModel):
    id: UUID
    name: str
    category: CategoryEnum
    description: Optional[str]
    price: float
    data_limit_gb: Optional[int]
    speed_mbps: Optional[int]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}