"""
모델 관리자 모듈
- 모델 로드/언로드
- 모델 다운로드
- 안전한 메모리 해제
- GPU 상태 모니터링
- 자동 로드 지원
"""

import gc
import os
import asyncio
from typing import Optional, Any, Callable, List
from datetime import datetime
from pathlib import Path

from schemas.settings import OptimizationSettings
from schemas.model import ModelStatus, ModelDownloadProgress, DownloadStatus
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
            
            # 다운로드 관련
            self._download_progress: ModelDownloadProgress = ModelDownloadProgress(
                status=DownloadStatus.IDLE
            )
            self._downloading: bool = False
            self._download_lock = asyncio.Lock()
            self._download_cancelled: bool = False
            self._progress_callbacks: List[Callable[[ModelDownloadProgress], None]] = []
            
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
    def is_downloading(self) -> bool:
        """모델 다운로드 중 여부"""
        return self._downloading
    
    @property
    def download_progress(self) -> ModelDownloadProgress:
        """다운로드 진행 상황"""
        return self._download_progress
    
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
    
    def add_progress_callback(self, callback: Callable[[ModelDownloadProgress], None]):
        """다운로드 진행 상황 콜백 추가"""
        self._progress_callbacks.append(callback)
    
    def remove_progress_callback(self, callback: Callable[[ModelDownloadProgress], None]):
        """다운로드 진행 상황 콜백 제거"""
        if callback in self._progress_callbacks:
            self._progress_callbacks.remove(callback)
    
    def _notify_progress(self):
        """진행 상황 콜백 호출"""
        for callback in self._progress_callbacks:
            try:
                callback(self._download_progress)
            except Exception:
                pass
    
    def _update_progress(
        self,
        status: Optional[DownloadStatus] = None,
        progress_percent: Optional[float] = None,
        downloaded_size_mb: Optional[float] = None,
        total_size_mb: Optional[float] = None,
        current_file: Optional[str] = None,
        files_completed: Optional[int] = None,
        files_total: Optional[int] = None,
        error_message: Optional[str] = None,
    ):
        """다운로드 진행 상황 업데이트"""
        if status is not None:
            self._download_progress.status = status
        if progress_percent is not None:
            self._download_progress.progress_percent = progress_percent
        if downloaded_size_mb is not None:
            self._download_progress.downloaded_size_mb = downloaded_size_mb
        if total_size_mb is not None:
            self._download_progress.total_size_mb = total_size_mb
        if current_file is not None:
            self._download_progress.current_file = current_file
        if files_completed is not None:
            self._download_progress.files_completed = files_completed
        if files_total is not None:
            self._download_progress.files_total = files_total
        if error_message is not None:
            self._download_progress.error_message = error_message
        
        self._notify_progress()
    
    def is_model_downloaded(self, model_name: str) -> bool:
        """모델이 이미 다운로드되어 있는지 확인"""
        try:
            from huggingface_hub import HfApi, hf_hub_download
            from huggingface_hub.utils import LocalEntryNotFoundError
            
            api = HfApi()
            
            # 캐시 디렉토리 확인
            cache_dir = os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
            hub_cache = Path(cache_dir) / "hub"
            
            # 모델 디렉토리 형식: models--owner--model_name
            model_dir_name = f"models--{model_name.replace('/', '--')}"
            model_path = hub_cache / model_dir_name
            
            if model_path.exists():
                # snapshots 디렉토리에 파일이 있는지 확인
                snapshots = model_path / "snapshots"
                if snapshots.exists() and any(snapshots.iterdir()):
                    return True
            
            return False
        except Exception:
            return False
    
    async def download_model(
        self,
        model_name: str = "ovedrive/Qwen-Image-Edit-2511-4bit",
        force_download: bool = False,
    ) -> ModelDownloadProgress:
        """
        모델 다운로드
        
        Args:
            model_name: Hugging Face 모델 ID
            force_download: 이미 존재해도 다시 다운로드
        
        Returns:
            ModelDownloadProgress: 다운로드 완료 후 상태
        """
        async with self._download_lock:
            if self._downloading:
                return self._download_progress
            
            # 이미 다운로드된 경우
            if not force_download and self.is_model_downloaded(model_name):
                self._download_progress = ModelDownloadProgress(
                    status=DownloadStatus.COMPLETED,
                    model_name=model_name,
                    progress_percent=100,
                )
                return self._download_progress
            
            self._downloading = True
            self._download_cancelled = False
            self._download_progress = ModelDownloadProgress(
                status=DownloadStatus.DOWNLOADING,
                model_name=model_name,
            )
            
            try:
                print(f"📥 Starting download: {model_name}")
                
                # 비동기로 다운로드 실행
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None,
                    self._download_model_sync,
                    model_name,
                    force_download,
                )
                
                if self._download_cancelled:
                    self._update_progress(status=DownloadStatus.CANCELLED)
                    print(f"⚠️ Download cancelled: {model_name}")
                else:
                    self._update_progress(
                        status=DownloadStatus.COMPLETED,
                        progress_percent=100,
                    )
                    print(f"✅ Download completed: {model_name}")
                
                return self._download_progress
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Download failed: {error_msg}")
                self._update_progress(
                    status=DownloadStatus.FAILED,
                    error_message=error_msg,
                )
                return self._download_progress
                
            finally:
                self._downloading = False
    
    def _download_model_sync(self, model_name: str, force_download: bool):
        """동기 모델 다운로드 (별도 스레드에서 실행)"""
        from huggingface_hub import snapshot_download, HfApi
        from huggingface_hub.utils import tqdm as hf_tqdm
        import threading
        
        api = HfApi()
        
        try:
            # 모델 정보 가져오기
            model_info = api.model_info(model_name)
            siblings = model_info.siblings or []
            
            # 다운로드할 파일 목록
            files_to_download = [s.rfilename for s in siblings if s.rfilename]
            total_files = len(files_to_download)
            
            self._update_progress(
                files_total=total_files,
                files_completed=0,
            )
            
            # 전체 크기 계산 (가능한 경우)
            total_size = sum(
                getattr(s, 'size', 0) or 0
                for s in siblings
            )
            if total_size > 0:
                self._update_progress(total_size_mb=total_size / (1024 * 1024))
            
        except Exception as e:
            print(f"⚠️ Could not get model info: {e}")
            total_files = 0
        
        # 커스텀 진행 상황 추적
        downloaded_bytes = 0
        files_completed = 0
        current_file_lock = threading.Lock()
        
        def progress_callback(progress):
            nonlocal downloaded_bytes, files_completed
            
            if self._download_cancelled:
                raise InterruptedError("Download cancelled")
            
            with current_file_lock:
                # 진행률 업데이트
                if hasattr(progress, 'n') and hasattr(progress, 'total'):
                    if progress.total and progress.total > 0:
                        percent = (progress.n / progress.total) * 100
                        self._update_progress(
                            progress_percent=min(percent, 99.9),
                            downloaded_size_mb=progress.n / (1024 * 1024),
                        )
        
        # snapshot_download 사용
        try:
            cache_dir = snapshot_download(
                repo_id=model_name,
                force_download=force_download,
                resume_download=True,
            )
            print(f"📁 Model cached at: {cache_dir}")
            
        except InterruptedError:
            raise
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")
    
    def cancel_download(self):
        """다운로드 취소"""
        if self._downloading:
            self._download_cancelled = True
            print("⚠️ Download cancellation requested")
    
    def get_available_models(self) -> list:
        """사용 가능한 모델 목록 반환"""
        models = [
            {
                "model_id": "ovedrive/Qwen-Image-Edit-2511-4bit",
                "name": "Qwen Image Edit 4-bit (권장)",
                "description": "4비트 양자화 버전으로 낮은 VRAM 사용량",
                "size_gb": 8.0,
                "is_recommended": True,
            },
            {
                "model_id": "Qwen/Qwen-Image-Edit-2511",
                "name": "Qwen Image Edit (원본)",
                "description": "원본 모델, 높은 품질이지만 더 많은 VRAM 필요",
                "size_gb": 30.0,
                "is_recommended": False,
            },
        ]
        
        # 다운로드 여부 확인
        for model in models:
            model["is_downloaded"] = self.is_model_downloaded(model["model_id"])
        
        return models


# 싱글톤 인스턴스 접근자
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """모델 관리자 인스턴스 반환"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager

