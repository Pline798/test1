from datetime import datetime, date as date_type
from typing import Optional

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    record_type: str = Field(..., alias="type", pattern="^(income|expense)$", description="分类类型")
    icon: str = Field("📁", max_length=20, description="图标")
    color: str = Field("#409EFF", max_length=7, description="颜色")

    class Config:
        populate_by_name = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    record_type: Optional[str] = Field(None, alias="type", pattern="^(income|expense)$")
    icon: Optional[str] = Field(None, max_length=20)
    color: Optional[str] = Field(None, max_length=7)

    class Config:
        populate_by_name = True


class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True
        populate_by_name = True


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, description="金额")
    record_type: str = Field(..., alias="type", pattern="^(income|expense)$", description="收支类型")
    category_id: int = Field(..., description="分类ID")
    description: Optional[str] = Field(None, description="备注")
    record_date: date_type = Field(..., alias="date", description="交易日期")

    class Config:
        populate_by_name = True


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    record_type: Optional[str] = Field(None, alias="type", pattern="^(income|expense)$")
    category_id: Optional[int] = Field(None)
    description: Optional[str] = Field(None)
    record_date: Optional[date_type] = Field(None, alias="date")

    class Config:
        populate_by_name = True


class TransactionOut(TransactionBase):
    id: int
    created_at: Optional[datetime] = None
    category: Optional[CategoryOut] = None

    class Config:
        from_attributes = True
        populate_by_name = True
