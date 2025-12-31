"""
모델 관련 스키마
"""

from typing import Optional
from pydantic import BaseModel, Field

from schemas.settings import OptimizationSettings


class ModelStatus(BaseModel):
    """모델 상태"""
    is_loaded: bool = Field(description="모델 로드 여부")
    model_name: Optional[str] = Field(default=None, description="로드된 모델 이름")
    device: Optional[str] = Field(default=None, description="사용 중인 디바이스")
    dtype: Optional[str] = Field(default=None, description="데이터 타입")
    vram_used_gb: Optional[float] = Field(default=None, description="사용 중인 VRAM (GB)")
    vram_total_gb: Optional[float] = Field(default=None, description="전체 VRAM (GB)")
    optimization: Optional[OptimizationSettings] = Field(default=None, description="적용된 최적화")


class ModelStatusResponse(BaseModel):
    """모델 상태 응답"""
    success: bool = True
    data: ModelStatus


class ModelLoadRequest(BaseModel):
    """모델 로드 요청"""
    model_name: Optional[str] = Field(
        default=None,
        description="로드할 모델 (없으면 기본 모델 사용)"
    )
    optimization: Optional[OptimizationSettings] = Field(
        default=None,
        description="최적화 설정 (없으면 저장된 설정 사용)"
    )
    force_reload: bool = Field(
        default=False,
        description="이미 로드된 경우에도 다시 로드"
    )


class ModelLoadResponse(BaseModel):
    """모델 로드 응답"""
    success: bool = True
    message: str
    data: ModelStatus


class ModelUnloadResponse(BaseModel):
    """모델 언로드 응답"""
    success: bool = True
    message: str
    vram_freed_gb: Optional[float] = None


class OptimizationUpdateRequest(BaseModel):
    """최적화 설정 변경 요청"""
    optimization: OptimizationSettings
    apply_immediately: bool = Field(
        default=False,
        description="즉시 적용 (모델 재로드 필요)"
    )

