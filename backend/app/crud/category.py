from typing import List, Optional
from sqlalchemy import exc
from sqlalchemy.orm import Session
from app.models import Category


def get_categories(db: Session, type_filter: Optional[str] = None) -> List[Category]:
    query = db.query(Category)
    if type_filter:
        query = query.filter(Category.type == type_filter)
    return query.all()


def create_category(db: Session, data: dict) -> Category:
    cat = Category(**data)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, cat_id: int, data: dict) -> Optional[Category]:
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        return None
    for key, value in data.items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return cat


def delete_category(db: Session, cat_id: int) -> bool:
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        return False
    try:
        db.delete(cat)
        db.commit()
        return True
    except exc.IntegrityError:
        db.rollback()
        raise ValueError("该分类下有流水记录，无法删除")