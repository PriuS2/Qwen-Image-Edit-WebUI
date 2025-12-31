"""
환경 설정 모듈
Pydantic Settings를 사용하여 환경 변수 및 설정 관리
"""

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # 서버 설정
    # ═══════════════════════════════════════════════════════════════
    app_name: str = "Qwen Image Edit API"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, description="디버그 모드")
    host: str = Field(default="0.0.0.0", description="서버 호스트")
    port: int = Field(default=8000, description="서버 포트")
    
    # ═══════════════════════════════════════════════════════════════
    # API 인증
    # ═══════════════════════════════════════════════════════════════
    api_key: str = Field(
        default="qwen-image-edit-default-key",
        description="API 인증 키"
    )
    api_key_header: str = Field(
        default="X-API-Key",
        description="API 키 헤더 이름"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # 경로 설정
    # ═══════════════════════════════════════════════════════════════
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent,
        description="베이스 디렉토리"
    )
    
    @property
    def storage_dir(self) -> Path:
        """저장소 디렉토리"""
        return self.base_dir / "storage"
    
    @property
    def images_dir(self) -> Path:
        """편집된 이미지 저장 디렉토리"""
        return self.storage_dir / "images"
    
    @property
    def thumbnails_dir(self) -> Path:
        """썸네일 저장 디렉토리"""
        return self.storage_dir / "thumbnails"
    
    @property
    def temp_dir(self) -> Path:
        """임시 파일 디렉토리"""
        return self.storage_dir / "temp"
    
    @property
    def uploads_dir(self) -> Path:
        """업로드된 원본 이미지 디렉토리"""
        return self.storage_dir / "uploads"
    
    # ═══════════════════════════════════════════════════════════════
    # 데이터베이스 설정
    # ═══════════════════════════════════════════════════════════════
    database_url: str = Field(
        default="sqlite+aiosqlite:///./storage/qwen_image_edit.db",
        description="데이터베이스 URL"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # 모델 기본 설정
    # ═══════════════════════════════════════════════════════════════
    default_model: str = Field(
        default="ovedrive/Qwen-Image-Edit-2511-4bit",
        description="기본 모델 경로"
    )
    torch_dtype: str = Field(
        default="bfloat16",
        description="PyTorch 데이터 타입 (bfloat16, float16, float32)"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # 자동 로드/언로드 기본 설정
    # ═══════════════════════════════════════════════════════════════
    auto_unload_enabled: bool = Field(
        default=True,
        description="자동 언로드 활성화"
    )
    auto_unload_timeout_minutes: int = Field(
        default=30,
        description="자동 언로드 타임아웃 (분)"
    )
    auto_load_on_request: bool = Field(
        default=True,
        description="요청 시 자동 로드"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # 최적화 기본 설정
    # ═══════════════════════════════════════════════════════════════
    enable_model_cpu_offload: bool = Field(
        default=True,
        description="CPU 오프로딩 활성화"
    )
    enable_attention_slicing: bool = Field(
        default=True,
        description="Attention 슬라이싱 활성화"
    )
    enable_vae_slicing: bool = Field(
        default=True,
        description="VAE 슬라이싱 활성화"
    )
    enable_vae_tiling: bool = Field(
        default=False,
        description="VAE 타일링 활성화"
    )
    enable_xformers: bool = Field(
        default=False,
        description="xFormers 활성화"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # 편집 기본 설정
    # ═══════════════════════════════════════════════════════════════
    default_num_inference_steps: int = Field(
        default=20,
        description="기본 추론 스텝 수"
    )
    default_true_cfg_scale: float = Field(
        default=4.0,
        description="기본 True CFG 스케일"
    )
    default_guidance_scale: float = Field(
        default=1.0,
        description="기본 가이던스 스케일"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # 갤러리/히스토리 설정
    # ═══════════════════════════════════════════════════════════════
    max_history_per_session: int = Field(
        default=10,
        description="세션당 최대 히스토리 수"
    )
    auto_cleanup_days: int = Field(
        default=7,
        description="자동 정리 일수"
    )
    thumbnail_size: int = Field(
        default=256,
        description="썸네일 크기"
    )
    
    # ═══════════════════════════════════════════════════════════════
    # CORS 설정
    # ═══════════════════════════════════════════════════════════════
    cors_origins: list[str] = Field(
        default=["*"],
        description="허용된 CORS 오리진"
    )
    
    def ensure_directories(self) -> None:
        """필요한 디렉토리 생성"""
        directories = [
            self.storage_dir,
            self.images_dir,
            self.thumbnails_dir,
            self.temp_dir,
            self.uploads_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    settings = Settings()
    settings.ensure_directories()
    return settings

