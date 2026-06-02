from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import TransactionCreate, TransactionUpdate, TransactionOut
from app.crud.transaction import get_transactions, create_transaction, update_transaction, delete_transaction

router = APIRouter(prefix="/api/transactions", tags=["流水"])

@router.get("", response_model=list[TransactionOut], response_model_by_alias=True)
def list_transactions(
    type: Optional[str] = Query(None, pattern="^(income|expense)$"),
    category_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    keyword: Optional[str] = Query(None),
    amount_min: Optional[float] = Query(None, ge=0),
    amount_max: Optional[float] = Query(None, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_transactions(db, type, category_id, year, month, keyword, amount_min, amount_max, skip, limit)

@router.post("", response_model=TransactionOut, response_model_by_alias=True)
def add_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    return create_transaction(db, data.model_dump(by_alias=True))

@router.put("/{txn_id}", response_model=TransactionOut, response_model_by_alias=True)
def edit_transaction(txn_id: int, data: TransactionUpdate, db: Session = Depends(get_db)):
    result = update_transaction(db, txn_id, data.model_dump(by_alias=True, exclude_unset=True))
    if not result:
        raise HTTPException(404, "记录不存在")
    return result

@router.delete("/{txn_id}")
def remove_transaction(txn_id: int, db: Session = Depends(get_db)):
    success = delete_transaction(db, txn_id)
    if not success:
        raise HTTPException(404, "记录不存在")
    return {"message": "删除成功"}