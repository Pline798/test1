from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import Category, Transaction


def get_transactions(
    db: Session,
    type_filter: Optional[str] = None,
    category_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Transaction]:
    query = db.query(Transaction)
    if type_filter:
        query = query.filter(Transaction.type == type_filter)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if year:
        query = query.filter(func.year(Transaction.date) == year)
    if month:
        query = query.filter(func.month(Transaction.date) == month)
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
        if value is not None:
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
    query = db.query(
        Transaction.type,
        func.sum(Transaction.amount).label("total"),
        func.count(Transaction.id).label("count"),
    )
    if year:
        query = query.filter(func.year(Transaction.date) == year)
    if month:
        query = query.filter(func.month(Transaction.date) == month)
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
    if year:
        cat_query = cat_query.filter(func.year(Transaction.date) == year)
    if month:
        cat_query = cat_query.filter(func.month(Transaction.date) == month)
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