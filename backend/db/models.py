"""
SQLAlchemy ORM 모델 정의
- History: 편집 히스토리
- Gallery: 갤러리 이미지
- Jobs: 작업 큐
- Settings: 설정 저장
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean,
    DateTime, ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from db.database import Base


def generate_uuid() -> str:
    """UUID 문자열 생성"""
    return str(uuid.uuid4())


class History(Base):
    """편집 히스토리 테이블"""
    
    __tablename__ = "history"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), nullable=False, index=True)
    original_image_path = Column(String(500), nullable=False)
    edited_image_path = Column(String(500), nullable=True)
    prompt = Column(Text, nullable=False)
    parameters = Column(SQLiteJSON, nullable=True)
    parent_id = Column(String(36), ForeignKey("history.id"), nullable=True)
    position = Column(Integer, default=0)  # Undo/Redo 위치 추적
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    parent = relationship("History", remote_side=[id], backref="children")
    gallery_items = relationship("Gallery", back_populates="history", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<History(id={self.id}, session_id={self.session_id}, prompt={self.prompt[:30]}...)>"


class Gallery(Base):
    """갤러리 테이블"""
    
    __tablename__ = "gallery"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    history_id = Column(String(36), ForeignKey("history.id"), nullable=True)
    image_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=True)
    original_image_path = Column(String(500), nullable=True)  # 비교용 원본 경로
    metadata = Column(SQLiteJSON, nullable=True)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    history = relationship("History", back_populates="gallery_items")
    
    def __repr__(self) -> str:
        return f"<Gallery(id={self.id}, title={self.title})>"


class JobStatus:
    """작업 상태 상수"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType:
    """작업 유형 상수"""
    SINGLE = "single"
    MULTI = "multi"
    BATCH = "batch"
    STYLE_TRANSFER = "style_transfer"


class Job(Base):
    """작업 큐 테이블"""
    
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    type = Column(String(20), nullable=False, default=JobType.SINGLE)
    status = Column(String(20), nullable=False, default=JobStatus.PENDING, index=True)
    progress = Column(Integer, default=0)
    input_data = Column(SQLiteJSON, nullable=True)
    output_data = Column(SQLiteJSON, nullable=True)
    error_message = Column(Text, nullable=True)
    session_id = Column(String(36), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Job(id={self.id}, type={self.type}, status={self.status})>"
    
    @property
    def is_finished(self) -> bool:
        """작업 완료 여부"""
        return self.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)
    
    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "progress": self.progress,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class Setting(Base):
    """설정 테이블 (Key-Value 저장)"""
    
    __tablename__ = "settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(SQLiteJSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Setting(key={self.key})>"

