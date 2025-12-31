"""
설정 관리자 모듈
- 설정 영구 저장 (SQLite)
- 자동 언로드 타이머
- 기본값 초기화
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Any
from functools import lru_cache

from db.database import AsyncSessionLocal
from db import crud
from schemas.settings import (
    AllSettings, AutoUnloadSettings, AutoLoadSettings,
    OptimizationSettings, EditDefaultParams, GallerySettings
)
from config import get_settings as get_app_settings


class SettingsManager:
    """설정 관리자 싱글톤"""
    
    _instance: Optional["SettingsManager"] = None
    _initialized: bool = False
    
    def __new__(cls) -> "SettingsManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._settings: Optional[AllSettings] = None
            self._last_activity: datetime = datetime.utcnow()
            self._auto_unload_task: Optional[asyncio.Task] = None
            self._running: bool = False
            SettingsManager._initialized = True
    
    async def initialize(self) -> None:
        """설정 초기화 (DB에서 로드 또는 기본값 생성)"""
        async with AsyncSessionLocal() as db:
            # DB에서 설정 로드
            all_settings = await crud.get_all_settings(db)
            
            if not all_settings:
                # 기본값으로 초기화
                await self._initialize_defaults(db)
                all_settings = await crud.get_all_settings(db)
            
            # 설정 객체 구성
            self._settings = self._build_settings(all_settings)
            await db.commit()
    
    async def _initialize_defaults(self, db) -> None:
        """기본 설정값 저장"""
        app_settings = get_app_settings()
        
        defaults = {
            "auto_unload.enabled": app_settings.auto_unload_enabled,
            "auto_unload.timeout_minutes": app_settings.auto_unload_timeout_minutes,
            "auto_load.enabled": app_settings.auto_load_on_request,
            "default_model": app_settings.default_model,
            "torch_dtype": app_settings.torch_dtype,
            "optimization.enable_model_cpu_offload": app_settings.enable_model_cpu_offload,
            "optimization.enable_attention_slicing": app_settings.enable_attention_slicing,
            "optimization.enable_vae_slicing": app_settings.enable_vae_slicing,
            "optimization.enable_vae_tiling": app_settings.enable_vae_tiling,
            "optimization.enable_xformers": app_settings.enable_xformers,
            "edit_defaults.num_inference_steps": app_settings.default_num_inference_steps,
            "edit_defaults.true_cfg_scale": app_settings.default_true_cfg_scale,
            "edit_defaults.guidance_scale": app_settings.default_guidance_scale,
            "gallery.max_history_per_session": app_settings.max_history_per_session,
            "gallery.auto_cleanup_days": app_settings.auto_cleanup_days,
            "gallery.thumbnail_size": app_settings.thumbnail_size,
        }
        
        for key, value in defaults.items():
            await crud.set_setting(db, key, value)
    
    def _build_settings(self, raw_settings: dict) -> AllSettings:
        """딕셔너리에서 설정 객체 구성"""
        return AllSettings(
            auto_unload=AutoUnloadSettings(
                enabled=raw_settings.get("auto_unload.enabled", True),
                timeout_minutes=raw_settings.get("auto_unload.timeout_minutes", 30),
            ),
            auto_load=AutoLoadSettings(
                enabled=raw_settings.get("auto_load.enabled", True),
            ),
            default_model=raw_settings.get("default_model", "ovedrive/Qwen-Image-Edit-2511-4bit"),
            torch_dtype=raw_settings.get("torch_dtype", "bfloat16"),
            optimization=OptimizationSettings(
                enable_model_cpu_offload=raw_settings.get("optimization.enable_model_cpu_offload", True),
                enable_attention_slicing=raw_settings.get("optimization.enable_attention_slicing", True),
                enable_vae_slicing=raw_settings.get("optimization.enable_vae_slicing", True),
                enable_vae_tiling=raw_settings.get("optimization.enable_vae_tiling", False),
                enable_xformers=raw_settings.get("optimization.enable_xformers", False),
            ),
            edit_defaults=EditDefaultParams(
                num_inference_steps=raw_settings.get("edit_defaults.num_inference_steps", 20),
                true_cfg_scale=raw_settings.get("edit_defaults.true_cfg_scale", 4.0),
                guidance_scale=raw_settings.get("edit_defaults.guidance_scale", 1.0),
            ),
            gallery=GallerySettings(
                max_history_per_session=raw_settings.get("gallery.max_history_per_session", 10),
                auto_cleanup_days=raw_settings.get("gallery.auto_cleanup_days", 7),
                thumbnail_size=raw_settings.get("gallery.thumbnail_size", 256),
            ),
        )
    
    @property
    def settings(self) -> AllSettings:
        """현재 설정 반환"""
        if self._settings is None:
            return AllSettings()
        return self._settings
    
    async def get_all(self) -> AllSettings:
        """전체 설정 조회"""
        if self._settings is None:
            await self.initialize()
        return self.settings
    
    async def update_setting(self, key: str, value: Any) -> None:
        """개별 설정 업데이트"""
        async with AsyncSessionLocal() as db:
            await crud.set_setting(db, key, value)
            await db.commit()
        
        # 메모리 설정도 업데이트
        await self.initialize()
    
    async def update_all(self, settings: AllSettings) -> None:
        """전체 설정 업데이트"""
        async with AsyncSessionLocal() as db:
            # 자동 언로드
            await crud.set_setting(db, "auto_unload.enabled", settings.auto_unload.enabled)
            await crud.set_setting(db, "auto_unload.timeout_minutes", settings.auto_unload.timeout_minutes)
            
            # 자동 로드
            await crud.set_setting(db, "auto_load.enabled", settings.auto_load.enabled)
            
            # 모델
            await crud.set_setting(db, "default_model", settings.default_model)
            await crud.set_setting(db, "torch_dtype", settings.torch_dtype)
            
            # 최적화
            await crud.set_setting(db, "optimization.enable_model_cpu_offload", settings.optimization.enable_model_cpu_offload)
            await crud.set_setting(db, "optimization.enable_attention_slicing", settings.optimization.enable_attention_slicing)
            await crud.set_setting(db, "optimization.enable_vae_slicing", settings.optimization.enable_vae_slicing)
            await crud.set_setting(db, "optimization.enable_vae_tiling", settings.optimization.enable_vae_tiling)
            await crud.set_setting(db, "optimization.enable_xformers", settings.optimization.enable_xformers)
            
            # 편집 기본값
            await crud.set_setting(db, "edit_defaults.num_inference_steps", settings.edit_defaults.num_inference_steps)
            await crud.set_setting(db, "edit_defaults.true_cfg_scale", settings.edit_defaults.true_cfg_scale)
            await crud.set_setting(db, "edit_defaults.guidance_scale", settings.edit_defaults.guidance_scale)
            
            # 갤러리
            await crud.set_setting(db, "gallery.max_history_per_session", settings.gallery.max_history_per_session)
            await crud.set_setting(db, "gallery.auto_cleanup_days", settings.gallery.auto_cleanup_days)
            await crud.set_setting(db, "gallery.thumbnail_size", settings.gallery.thumbnail_size)
            
            await db.commit()
        
        self._settings = settings
    
    async def update_auto_unload(self, enabled: Optional[bool] = None, timeout_minutes: Optional[int] = None) -> AutoUnloadSettings:
        """자동 언로드 설정 업데이트"""
        async with AsyncSessionLocal() as db:
            if enabled is not None:
                await crud.set_setting(db, "auto_unload.enabled", enabled)
            if timeout_minutes is not None:
                await crud.set_setting(db, "auto_unload.timeout_minutes", timeout_minutes)
            await db.commit()
        
        await self.initialize()
        return self.settings.auto_unload
    
    async def update_auto_load(self, enabled: Optional[bool] = None) -> AutoLoadSettings:
        """자동 로드 설정 업데이트"""
        async with AsyncSessionLocal() as db:
            if enabled is not None:
                await crud.set_setting(db, "auto_load.enabled", enabled)
            await db.commit()
        
        await self.initialize()
        return self.settings.auto_load
    
    async def reset_to_defaults(self) -> AllSettings:
        """설정 초기화"""
        async with AsyncSessionLocal() as db:
            await crud.delete_all_settings(db)
            await self._initialize_defaults(db)
            await db.commit()
        
        await self.initialize()
        return self.settings
    
    # ═══════════════════════════════════════════════════════════════
    # 활동 추적 및 자동 언로드
    # ═══════════════════════════════════════════════════════════════
    
    def update_activity(self) -> None:
        """마지막 활동 시간 업데이트"""
        self._last_activity = datetime.utcnow()
    
    @property
    def last_activity(self) -> datetime:
        """마지막 활동 시간"""
        return self._last_activity
    
    @property
    def idle_minutes(self) -> float:
        """유휴 시간 (분)"""
        delta = datetime.utcnow() - self._last_activity
        return delta.total_seconds() / 60
    
    async def start_auto_unload_timer(self) -> None:
        """자동 언로드 타이머 시작"""
        self._running = True
        
        while self._running:
            try:
                await asyncio.sleep(60)  # 1분마다 체크
                
                if not self._running:
                    break
                
                settings = await self.get_all()
                
                if not settings.auto_unload.enabled:
                    continue
                
                if self.idle_minutes >= settings.auto_unload.timeout_minutes:
                    # 모델 언로드
                    from core.model_manager import get_model_manager
                    model_manager = get_model_manager()
                    
                    if model_manager.is_loaded:
                        print(f"⏰ Auto-unloading model after {self.idle_minutes:.1f} minutes of inactivity")
                        await model_manager.unload_model()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Auto-unload timer error: {e}")
    
    def stop_auto_unload_timer(self) -> None:
        """자동 언로드 타이머 중지"""
        self._running = False


# 싱글톤 인스턴스 접근자
_settings_manager: Optional[SettingsManager] = None


async def get_settings_manager() -> SettingsManager:
    """설정 관리자 인스턴스 반환"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager

