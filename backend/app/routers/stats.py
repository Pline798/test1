from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.transaction import get_stats

router = APIRouter(prefix="/api/stats", tags=["统计"])

@router.get("")
def stats(year: Optional[int] = None, month: Optional[int] = None, db: Session = Depends(get_db)):
    return get_stats(db, year, month)