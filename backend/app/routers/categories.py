from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CategoryCreate, CategoryUpdate, CategoryOut
from app.crud.category import get_categories, create_category, update_category, delete_category

router = APIRouter(prefix="/api/categories", tags=["分类"])

@router.get("", response_model=list[CategoryOut], response_model_by_alias=True)
def list_categories(type: Optional[str] = Query(None, pattern="^(income|expense)$"), db: Session = Depends(get_db)):
    return get_categories(db, type)

@router.post("", response_model=CategoryOut, response_model_by_alias=True)
def add_category(data: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, data.model_dump(by_alias=True))

@router.put("/{cat_id}", response_model=CategoryOut, response_model_by_alias=True)
def edit_category(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    result = update_category(db, cat_id, data.model_dump(by_alias=True, exclude_unset=True))
    if not result:
        raise HTTPException(404, "分类不存在")
    return result

@router.delete("/{cat_id}")
def remove_category(cat_id: int, db: Session = Depends(get_db)):
    try:
        success = delete_category(db, cat_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not success:
        raise HTTPException(404, "分类不存在")
    return {"message": "删除成功"}