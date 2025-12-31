"""
모델 관련 스키마
"""

from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

from schemas.settings import OptimizationSettings


class DownloadStatus(str, Enum):
    """다운로드 상태"""
    IDLE = "idle"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModelDownloadProgress(BaseModel):
    """모델 다운로드 진행 상황"""
    status: DownloadStatus = Field(description="다운로드 상태")
    model_name: Optional[str] = Field(default=None, description="다운로드 중인 모델")
    progress_percent: float = Field(default=0, description="진행률 (%)")
    downloaded_size_mb: float = Field(default=0, description="다운로드된 크기 (MB)")
    total_size_mb: Optional[float] = Field(default=None, description="전체 크기 (MB)")
    current_file: Optional[str] = Field(default=None, description="현재 다운로드 중인 파일")
    files_completed: int = Field(default=0, description="완료된 파일 수")
    files_total: int = Field(default=0, description="전체 파일 수")
    error_message: Optional[str] = Field(default=None, description="에러 메시지")


class ModelDownloadRequest(BaseModel):
    """모델 다운로드 요청"""
    model_name: str = Field(
        default="ovedrive/Qwen-Image-Edit-2511-4bit",
        description="다운로드할 모델 (Hugging Face 모델 ID)"
    )
    force_download: bool = Field(
        default=False,
        description="이미 존재해도 다시 다운로드"
    )


class ModelDownloadResponse(BaseModel):
    """모델 다운로드 응답"""
    success: bool = True
    message: str
    data: ModelDownloadProgress


class AvailableModel(BaseModel):
    """사용 가능한 모델 정보"""
    model_id: str = Field(description="모델 ID (Hugging Face)")
    name: str = Field(description="표시 이름")
    description: str = Field(description="설명")
    size_gb: Optional[float] = Field(default=None, description="모델 크기 (GB)")
    is_downloaded: bool = Field(default=False, description="다운로드 여부")
    is_recommended: bool = Field(default=False, description="권장 모델 여부")


class AvailableModelsResponse(BaseModel):
    """사용 가능한 모델 목록 응답"""
    success: bool = True
    models: List[AvailableModel]


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

