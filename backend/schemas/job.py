"""
작업 관련 스키마
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class JobItem(BaseModel):
    """작업 아이템"""
    id: str
    type: str
    status: str
    progress: int = 0
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    error_message: Optional[str] = None
    session_id: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """작업 목록 응답"""
    success: bool = True
    data: List[JobItem]
    total: int


class BatchSubmitRequest(BaseModel):
    """배치 작업 제출 요청"""
    items: List[dict] = Field(description="편집 작업 목록")
    response_format: str = Field(default="url")
    session_id: Optional[str] = None
    save_to_gallery: bool = True


class BatchSubmitResponse(BaseModel):
    """배치 작업 제출 응답"""
    success: bool = True
    job_id: str
    total_items: int
    message: str

