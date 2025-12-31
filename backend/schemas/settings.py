"""
설정 관련 스키마
"""

from typing import Optional
from pydantic import BaseModel, Field


class OptimizationSettings(BaseModel):
    """최적화 설정"""
    enable_model_cpu_offload: bool = Field(default=True, description="CPU 오프로딩")
    enable_attention_slicing: bool = Field(default=True, description="Attention 슬라이싱")
    enable_vae_slicing: bool = Field(default=True, description="VAE 슬라이싱")
    enable_vae_tiling: bool = Field(default=False, description="VAE 타일링")
    enable_xformers: bool = Field(default=False, description="xFormers 사용")


class EditDefaultParams(BaseModel):
    """편집 기본 파라미터"""
    num_inference_steps: int = Field(default=20, ge=1, le=100)
    true_cfg_scale: float = Field(default=4.0, ge=1.0, le=20.0)
    guidance_scale: float = Field(default=1.0, ge=0.0, le=20.0)


class AutoUnloadSettings(BaseModel):
    """자동 언로드 설정"""
    enabled: bool = Field(default=True, description="자동 언로드 활성화")
    timeout_minutes: int = Field(default=30, ge=1, le=1440, description="타임아웃 (분)")


class AutoLoadSettings(BaseModel):
    """자동 로드 설정"""
    enabled: bool = Field(default=True, description="요청 시 자동 로드")


class GallerySettings(BaseModel):
    """갤러리/히스토리 설정"""
    max_history_per_session: int = Field(default=10, ge=1, le=100)
    auto_cleanup_days: int = Field(default=7, ge=1, le=365)
    thumbnail_size: int = Field(default=256, ge=64, le=1024)


class AllSettings(BaseModel):
    """전체 설정"""
    # 자동 언로드/로드
    auto_unload: AutoUnloadSettings = Field(default_factory=AutoUnloadSettings)
    auto_load: AutoLoadSettings = Field(default_factory=AutoLoadSettings)
    
    # 모델 설정
    default_model: str = Field(default="ovedrive/Qwen-Image-Edit-2511-4bit")
    torch_dtype: str = Field(default="bfloat16")
    
    # 최적화
    optimization: OptimizationSettings = Field(default_factory=OptimizationSettings)
    
    # 편집 기본값
    edit_defaults: EditDefaultParams = Field(default_factory=EditDefaultParams)
    
    # 갤러리/히스토리
    gallery: GallerySettings = Field(default_factory=GallerySettings)


class SettingsResponse(BaseModel):
    """설정 응답"""
    success: bool = True
    data: AllSettings


class AutoUnloadSettingsUpdate(BaseModel):
    """자동 언로드 설정 업데이트"""
    enabled: Optional[bool] = None
    timeout_minutes: Optional[int] = Field(default=None, ge=1, le=1440)


class AutoLoadSettingsUpdate(BaseModel):
    """자동 로드 설정 업데이트"""
    enabled: Optional[bool] = None

