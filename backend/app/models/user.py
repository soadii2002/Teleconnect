import uuid
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    gender = Column(Enum("male", "female", name="gender_enum"), nullable=False)
    phone_number = Column(String(11), unique=True, nullable=False)
    city = Column(String(100), nullable=False)
    role = Column(Enum("customer", "admin", name="role_enum"),
                default="customer", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
