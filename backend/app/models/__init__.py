from datetime import date, datetime

from sqlalchemy import (
    Column, Integer, String, Float, Enum, Date, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="分类名称")
    type = Column(Enum("income", "expense", name="category_type"), nullable=False, comment="分类类型")
    icon = Column(String(20), default="📁", comment="图标 emoji")
    color = Column(String(7), default="#409EFF", comment="颜色 hex")

    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False, comment="金额")
    type = Column(Enum("income", "expense", name="transaction_type"), nullable=False, comment="收支类型")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, comment="分类ID")
    description = Column(Text, comment="备注")
    date = Column(Date, nullable=False, comment="交易日期")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    category = relationship("Category", back_populates="transactions")
