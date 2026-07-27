from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime
from backend.database.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True) # Now optional for TG users
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)
    telegram_id: Mapped[int] = mapped_column(index=True, unique=True, nullable=True)
    credits: Mapped[int] = mapped_column(default=3) # Free searches initially
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
