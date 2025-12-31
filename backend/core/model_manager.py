"""
모델 관리자 모듈
- 모델 로드/언로드
- 안전한 메모리 해제
- GPU 상태 모니터링
- 자동 로드 지원
"""

import gc
import asyncio
from typing import Optional, Any
from datetime import datetime

from schemas.settings import OptimizationSettings
from schemas.model import ModelStatus
from core.optimization import apply_optimizations, get_torch_dtype


class ModelManager:
    """모델 관리자 싱글톤"""
    
    _instance: Optional["ModelManager"] = None
    _initialized: bool = False
    
    def __new__(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._pipeline: Optional[Any] = None
            self._model_name: Optional[str] = None
            self._device: str = "cuda"
            self._dtype: Optional[str] = None
            self._optimization: Optional[OptimizationSettings] = None
            self._loading: bool = False
            self._load_lock = asyncio.Lock()
            ModelManager._initialized = True
    
    @property
    def is_loaded(self) -> bool:
        """모델 로드 여부"""
        return self._pipeline is not None
    
    @property
    def is_loading(self) -> bool:
        """모델 로딩 중 여부"""
        return self._loading
    
    @property
    def pipeline(self) -> Optional[Any]:
        """파이프라인 객체"""
        return self._pipeline
    
    @property
    def model_name(self) -> Optional[str]:
        """로드된 모델 이름"""
        return self._model_name
    
    def get_gpu_memory_info(self) -> tuple[Optional[float], Optional[float]]:
        """GPU 메모리 정보 반환 (used_gb, total_gb)"""
        try:
            import torch
            if torch.cuda.is_available():
                used = torch.cuda.memory_allocated() / (1024 ** 3)
                total = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
                return round(used, 2), round(total, 2)
        except Exception:
            pass
        return None, None
    
    def get_status(self) -> ModelStatus:
        """모델 상태 반환"""
        vram_used, vram_total = self.get_gpu_memory_info()
        
        return ModelStatus(
            is_loaded=self.is_loaded,
            model_name=self._model_name,
            device=self._device if self.is_loaded else None,
            dtype=self._dtype,
            vram_used_gb=vram_used,
            vram_total_gb=vram_total,
            optimization=self._optimization,
        )
    
    async def load_model(
        self,
        model_name: Optional[str] = None,
        optimization: Optional[OptimizationSettings] = None,
        force_reload: bool = False,
    ) -> ModelStatus:
        """
        모델 로드
        
        Args:
            model_name: 로드할 모델 (없으면 설정에서 가져옴)
            optimization: 최적화 설정 (없으면 설정에서 가져옴)
            force_reload: 강제 재로드
        
        Returns:
            ModelStatus: 로드 후 상태
        """
        async with self._load_lock:
            # 이미 로드된 경우
            if self.is_loaded and not force_reload:
                if model_name is None or model_name == self._model_name:
                    return self.get_status()
            
            # 기존 모델 언로드
            if self.is_loaded:
                await self.unload_model()
            
            self._loading = True
            
            try:
                # 설정에서 값 가져오기
                from core.settings_manager import get_settings_manager
                settings_manager = await get_settings_manager()
                settings = await settings_manager.get_all()
                
                if model_name is None:
                    model_name = settings.default_model
                
                if optimization is None:
                    optimization = settings.optimization
                
                dtype_str = settings.torch_dtype
                
                print(f"🔄 Loading model: {model_name}")
                
                # 동기 로드를 비동기로 실행
                loop = asyncio.get_event_loop()
                self._pipeline = await loop.run_in_executor(
                    None,
                    self._load_pipeline_sync,
                    model_name,
                    dtype_str,
                    optimization,
                )
                
                self._model_name = model_name
                self._dtype = dtype_str
                self._optimization = optimization
                
                print(f"✅ Model loaded: {model_name}")
                
                return self.get_status()
            
            except Exception as e:
                print(f"❌ Failed to load model: {e}")
                self._pipeline = None
                self._model_name = None
                raise
            
            finally:
                self._loading = False
    
    def _load_pipeline_sync(
        self,
        model_name: str,
        dtype_str: str,
        optimization: OptimizationSettings,
    ) -> Any:
        """동기 파이프라인 로드 (별도 스레드에서 실행)"""
        import torch
        from diffusers import QwenImageEditPlusPipeline
        
        dtype = get_torch_dtype(dtype_str)
        
        # 파이프라인 로드
        pipeline = QwenImageEditPlusPipeline.from_pretrained(
            model_name,
            torch_dtype=dtype,
        )
        
        # CPU Offload가 아닌 경우 GPU로 이동
        if not optimization.enable_model_cpu_offload:
            pipeline.to(self._device)
        
        # 최적화 적용
        result = apply_optimizations(pipeline, optimization)
        for msg in result.messages:
            print(f"  {msg}")
        
        # 프로그레스 바 설정
        pipeline.set_progress_bar_config(disable=None)
        
        return pipeline
    
    async def unload_model(self) -> float:
        """
        모델 언로드 (안전하게 이 모델만 언로드)
        
        Returns:
            float: 해제된 VRAM (GB)
        """
        if not self.is_loaded:
            return 0.0
        
        print("🔄 Unloading model...")
        
        # 언로드 전 VRAM
        vram_before, _ = self.get_gpu_memory_info()
        
        # 1. 파이프라인 참조 제거
        del self._pipeline
        self._pipeline = None
        self._model_name = None
        self._dtype = None
        self._optimization = None
        
        # 2. Python 가비지 컬렉션
        gc.collect()
        
        # 3. CUDA 캐시 정리 (이 프로세스만)
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except Exception:
            pass
        
        # 언로드 후 VRAM
        vram_after, _ = self.get_gpu_memory_info()
        
        freed = 0.0
        if vram_before is not None and vram_after is not None:
            freed = round(vram_before - vram_after, 2)
        
        print(f"✅ Model unloaded. VRAM freed: {freed:.2f} GB")
        
        return freed
    
    async def ensure_loaded(self) -> bool:
        """
        모델이 로드되어 있는지 확인하고, 없으면 자동 로드
        
        Returns:
            bool: 로드 성공 여부
        """
        if self.is_loaded:
            return True
        
        # 자동 로드 설정 확인
        from core.settings_manager import get_settings_manager
        settings_manager = await get_settings_manager()
        settings = await settings_manager.get_all()
        
        if not settings.auto_load.enabled:
            return False
        
        try:
            await self.load_model()
            return True
        except Exception as e:
            print(f"❌ Auto-load failed: {e}")
            return False


# 싱글톤 인스턴스 접근자
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """모델 관리자 인스턴스 반환"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager

