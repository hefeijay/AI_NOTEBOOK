from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Note, User
from app.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/notes", tags=["notes"])


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[NoteResponse])
async def get_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的所有笔记"""
    notes = db.query(Note).filter(Note.user_id == current_user.id).order_by(Note.updated_at.desc()).all()
    return [note.to_dict() for note in notes]


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个笔记"""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")
    return note.to_dict()


@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新笔记"""
    note = Note(
        title=note_data.title,
        content=note_data.content,
        user_id=current_user.id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note.to_dict()


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新笔记"""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    if note_data.title is not None:
        note.title = note_data.title
    if note_data.content is not None:
        note.content = note_data.content

    db.commit()
    db.refresh(note)
    return note.to_dict()


@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除笔记"""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    db.delete(note)
    db.commit()
    return None

