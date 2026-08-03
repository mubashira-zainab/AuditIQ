"""
Memory router — persistent AI memory facts per user.

Endpoints:
  GET    /api/memory       — get all memory facts for current user
  POST   /api/memory       — upsert a key-value memory fact
  DELETE /api/memory/{key} — remove a specific memory fact
  DELETE /api/memory       — clear all memory for current user
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSessionType

from app.db import get_db
from app.models import Memory, User
from app.routers.auth import get_current_user
from app.schemas import MemoryItem, MemoryResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/memory", tags=["memory"])


# ─── GET ALL ──────────────────────────────────────────────────────────────────
@router.get("", response_model=MemoryResponse)
def get_memory(
    db: DBSessionType = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.query(Memory).filter(Memory.user_id == current_user.id).all()
    return MemoryResponse(items=[MemoryItem(key=m.key, value=m.value) for m in items])


# ─── UPSERT ───────────────────────────────────────────────────────────────────
@router.post("", response_model=MemoryItem)
def upsert_memory(
    body: MemoryItem,
    db: DBSessionType = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Memory).filter(
        Memory.user_id == current_user.id,
        Memory.key == body.key,
    ).first()

    if existing:
        existing.value = body.value
    else:
        existing = Memory(user_id=current_user.id, key=body.key, value=body.value)
        db.add(existing)

    db.commit()
    logger.info("Memory upsert: user=%s key=%s", current_user.email, body.key)
    return MemoryItem(key=existing.key, value=existing.value)


# ─── DELETE ONE ───────────────────────────────────────────────────────────────
@router.delete("/{key}")
def delete_memory_key(
    key: str,
    db: DBSessionType = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(Memory).filter(
        Memory.user_id == current_user.id,
        Memory.key == key,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Memory key '{key}' not found.")
    db.delete(item)
    db.commit()
    return {"status": "deleted", "key": key}


# ─── CLEAR ALL ────────────────────────────────────────────────────────────────
@router.delete("")
def clear_all_memory(
    db: DBSessionType = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = db.query(Memory).filter(Memory.user_id == current_user.id).delete()
    db.commit()
    logger.info("Memory cleared: user=%s count=%d", current_user.email, count)
    return {"status": "cleared", "deleted_count": count}
