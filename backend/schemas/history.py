"""
히스토리 관련 스키마
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class HistoryItem(BaseModel):
    """히스토리 아이템"""
    id: str
    session_id: str
    original_image_path: str
    edited_image_path: Optional[str]
    prompt: str
    parameters: Optional[dict]
    parent_id: Optional[str]
    position: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class HistoryListResponse(BaseModel):
    """히스토리 목록 응답"""
    success: bool = True
    data: List[HistoryItem]
    total: int


class HistoryDetailResponse(BaseModel):
    """히스토리 상세 응답"""
    success: bool = True
    data: HistoryItem


class UndoRedoResponse(BaseModel):
    """Undo/Redo 응답"""
    success: bool = True
    message: str
    current_position: int
    image_path: str
    can_undo: bool
    can_redo: bool

