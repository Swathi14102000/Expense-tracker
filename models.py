from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime
from sqlalchemy.sql import func
from database import Base

class Expense(Base):
    __tablename__ = "expenses"

    expense_id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100))
    amount = Column(DECIMAL(10,2))
    description = Column(Text)
    payment_mode = Column(String(50))
    merchant_name = Column(String(100))
    location = Column(String(100))
    notes = Column(Text)
    created_by = Column(String(50))

    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_date = Column(DateTime, nullable=True)
