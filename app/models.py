from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    balance = Column(Numeric(15, 2), default=0.00, nullable=False)

    user = relationship("User", backref="accounts")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(36), unique=True, nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
