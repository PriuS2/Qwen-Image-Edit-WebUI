"""
공통 스키마 정의
"""

from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar("T")


class ResponseBase(BaseModel):
    """기본 응답 스키마"""
    success: bool = True
    message: Optional[str] = None


class ResponseWithData(ResponseBase, Generic[T]):
    """데이터 포함 응답 스키마"""
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """에러 응답 스키마"""
    success: bool = False
    error: str
    detail: Optional[str] = None


class PaginationParams(BaseModel):
    """페이지네이션 파라미터"""
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PaginatedResponse(ResponseBase, Generic[T]):
    """페이지네이션된 응답"""
    data: list[T] = []
    total: int = 0
    limit: int = 50
    offset: int = 0
    has_more: bool = False


class ImageResponse(BaseModel):
    """이미지 응답 (Base64 또는 URL)"""
    format: str = Field(description="응답 형식: 'base64' 또는 'url'")
    data: str = Field(description="Base64 인코딩된 이미지 또는 URL")
    width: Optional[int] = None
    height: Optional[int] = None

