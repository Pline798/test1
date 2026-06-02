from typing import List, Optional
from datetime import date
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Category, Transaction


def _build_date_range(year: Optional[int], month: Optional[int]):
    """将 year/month 转为 [start, end) 日期范围，让查询可用上 date 列索引"""
    if not year:
        return None, None
    if month:
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
    else:
        start = date(year, 1, 1)
        end = date(year + 1, 1, 1)
    return start, end


def get_transactions(
    db: Session,
    type_filter: Optional[str] = None,
    category_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    keyword: Optional[str] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Transaction]:
    query = db.query(Transaction)
    if type_filter:
        query = query.filter(Transaction.type == type_filter)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    start, end = _build_date_range(year, month)
    if start:
        query = query.filter(Transaction.date >= start, Transaction.date < end)
    if keyword:
        query = query.filter(Transaction.description.ilike(f"%{keyword}%"))
    if amount_min is not None:
        query = query.filter(Transaction.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(Transaction.amount <= amount_max)
    return query.order_by(Transaction.date.desc(), Transaction.created_at.desc()).offset(skip).limit(limit).all()


def create_transaction(db: Session, data: dict) -> Transaction:
    txn = Transaction(**data)
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


def update_transaction(db: Session, txn_id: int, data: dict) -> Optional[Transaction]:
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not txn:
        return None
    for key, value in data.items():
        setattr(txn, key, value)
    db.commit()
    db.refresh(txn)
    return txn


def delete_transaction(db: Session, txn_id: int) -> bool:
    txn = db.query(Transaction).filter(Transaction.id == txn_id).first()
    if not txn:
        return False
    db.delete(txn)
    db.commit()
    return True


def get_stats(db: Session, year: Optional[int] = None, month: Optional[int] = None) -> dict:
    start, end = _build_date_range(year, month)

    query = db.query(
        Transaction.type,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count"),
    )
    if start:
        query = query.filter(Transaction.date >= start, Transaction.date < end)
    query = query.group_by(Transaction.type)
    result = {"income": {"total": 0, "count": 0}, "expense": {"total": 0, "count": 0}}
    for row in query.all():
        result[row.type] = {"total": float(row.total), "count": row.count}

    cat_query = db.query(
        Transaction.category_id,
        Transaction.type,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count"),
        Category.name,
        Category.icon,
        Category.color,
    ).join(Category, Transaction.category_id == Category.id)
    if start:
        cat_query = cat_query.filter(Transaction.date >= start, Transaction.date < end)
    cat_query = cat_query.group_by(Transaction.category_id, Transaction.type, Category.name, Category.icon, Category.color)
    result["by_category"] = [
        {
            "category_id": row.category_id,
            "category_name": row.name,
            "icon": row.icon,
            "color": row.color,
            "type": row.type,
            "total": float(row.total),
            "count": row.count,
        }
        for row in cat_query.all()
    ]
    return result