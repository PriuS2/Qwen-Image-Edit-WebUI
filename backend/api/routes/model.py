"""
모델 관리 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from api.dependencies import verify_api_key
from core.model_manager import get_model_manager
from core.settings_manager import get_settings_manager
from schemas.model import (
    ModelStatus, ModelStatusResponse,
    ModelLoadRequest, ModelLoadResponse,
    ModelUnloadResponse, OptimizationUpdateRequest,
    ModelDownloadRequest, ModelDownloadResponse,
    ModelDownloadProgress, DownloadStatus,
    AvailableModel, AvailableModelsResponse,
)
from schemas.settings import OptimizationSettings


router = APIRouter()


@router.get("/status", response_model=ModelStatusResponse)
async def get_model_status(api_key: str = Depends(verify_api_key)):
    """모델 상태 조회"""
    model_manager = get_model_manager()
    status = model_manager.get_status()
    
    return ModelStatusResponse(success=True, data=status)


# ═══════════════════════════════════════════════════════════════
# 모델 다운로드 관련 엔드포인트
# ═══════════════════════════════════════════════════════════════

@router.get("/available", response_model=AvailableModelsResponse)
async def get_available_models(api_key: str = Depends(verify_api_key)):
    """사용 가능한 모델 목록 조회"""
    model_manager = get_model_manager()
    models_data = model_manager.get_available_models()
    
    models = [AvailableModel(**m) for m in models_data]
    
    return AvailableModelsResponse(success=True, models=models)


@router.get("/download/status", response_model=ModelDownloadResponse)
async def get_download_status(api_key: str = Depends(verify_api_key)):
    """모델 다운로드 상태 조회"""
    model_manager = get_model_manager()
    progress = model_manager.download_progress
    
    return ModelDownloadResponse(
        success=True,
        message=f"Download status: {progress.status.value}",
        data=progress,
    )


@router.post("/download", response_model=ModelDownloadResponse)
async def download_model(
    background_tasks: BackgroundTasks,
    request: ModelDownloadRequest = None,
    api_key: str = Depends(verify_api_key),
):
    """
    모델 다운로드 시작
    
    백그라운드에서 비동기로 다운로드가 진행됩니다.
    진행 상황은 /download/status 또는 WebSocket을 통해 확인할 수 있습니다.
    """
    model_manager = get_model_manager()
    
    if model_manager.is_downloading:
        return ModelDownloadResponse(
            success=False,
            message="Download already in progress",
            data=model_manager.download_progress,
        )
    
    model_name = request.model_name if request else "ovedrive/Qwen-Image-Edit-2511-4bit"
    force_download = request.force_download if request else False
    
    # 이미 다운로드 완료된 경우
    if not force_download and model_manager.is_model_downloaded(model_name):
        return ModelDownloadResponse(
            success=True,
            message="Model already downloaded",
            data=ModelDownloadProgress(
                status=DownloadStatus.COMPLETED,
                model_name=model_name,
                progress_percent=100,
            ),
        )
    
    # 백그라운드에서 다운로드 시작
    async def start_download():
        await model_manager.download_model(
            model_name=model_name,
            force_download=force_download,
        )
    
    background_tasks.add_task(start_download)
    
    return ModelDownloadResponse(
        success=True,
        message=f"Download started for {model_name}",
        data=ModelDownloadProgress(
            status=DownloadStatus.DOWNLOADING,
            model_name=model_name,
        ),
    )


@router.post("/download/cancel", response_model=ModelDownloadResponse)
async def cancel_download(api_key: str = Depends(verify_api_key)):
    """모델 다운로드 취소"""
    model_manager = get_model_manager()
    
    if not model_manager.is_downloading:
        return ModelDownloadResponse(
            success=False,
            message="No download in progress",
            data=model_manager.download_progress,
        )
    
    model_manager.cancel_download()
    
    return ModelDownloadResponse(
        success=True,
        message="Download cancellation requested",
        data=model_manager.download_progress,
    )


@router.get("/download/check/{model_name:path}", response_model=dict)
async def check_model_downloaded(
    model_name: str,
    api_key: str = Depends(verify_api_key),
):
    """특정 모델이 다운로드되어 있는지 확인"""
    model_manager = get_model_manager()
    is_downloaded = model_manager.is_model_downloaded(model_name)
    
    return {
        "success": True,
        "model_name": model_name,
        "is_downloaded": is_downloaded,
    }


@router.post("/load", response_model=ModelLoadResponse)
async def load_model(
    request: ModelLoadRequest = None,
    api_key: str = Depends(verify_api_key),
):
    """
    모델 로드
    
    요청 본문이 없으면 저장된 설정 사용
    """
    model_manager = get_model_manager()
    
    if model_manager.is_loading:
        raise HTTPException(
            status_code=409,
            detail="Model is already loading"
        )
    
    try:
        model_name = None
        optimization = None
        force_reload = False
        
        if request:
            model_name = request.model_name
            optimization = request.optimization
            force_reload = request.force_reload
        
        status = await model_manager.load_model(
            model_name=model_name,
            optimization=optimization,
            force_reload=force_reload,
        )
        
        return ModelLoadResponse(
            success=True,
            message="Model loaded successfully",
            data=status,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model: {str(e)}"
        )


@router.post("/unload", response_model=ModelUnloadResponse)
async def unload_model(api_key: str = Depends(verify_api_key)):
    """
    모델 언로드
    
    이 모델만 안전하게 언로드 (다른 CUDA 프로세스에 영향 없음)
    """
    model_manager = get_model_manager()
    
    if not model_manager.is_loaded:
        return ModelUnloadResponse(
            success=True,
            message="Model is not loaded",
            vram_freed_gb=0,
        )
    
    freed = await model_manager.unload_model()
    
    return ModelUnloadResponse(
        success=True,
        message="Model unloaded successfully",
        vram_freed_gb=freed,
    )


@router.get("/optimization", response_model=dict)
async def get_optimization(api_key: str = Depends(verify_api_key)):
    """현재 최적화 설정 조회"""
    settings_manager = await get_settings_manager()
    settings = await settings_manager.get_all()
    
    model_manager = get_model_manager()
    
    return {
        "success": True,
        "saved_settings": settings.optimization.model_dump(),
        "applied_settings": model_manager._optimization.model_dump() if model_manager._optimization else None,
        "is_model_loaded": model_manager.is_loaded,
    }


@router.put("/optimization", response_model=dict)
async def update_optimization(
    request: OptimizationUpdateRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    최적화 설정 변경
    
    apply_immediately=True인 경우 모델 재로드 필요
    """
    settings_manager = await get_settings_manager()
    
    # 설정 저장
    current = await settings_manager.get_all()
    current.optimization = request.optimization
    await settings_manager.update_all(current)
    
    # 즉시 적용
    if request.apply_immediately:
        model_manager = get_model_manager()
        if model_manager.is_loaded:
            await model_manager.load_model(
                optimization=request.optimization,
                force_reload=True,
            )
    
    return {
        "success": True,
        "message": "Optimization settings updated",
        "applied_immediately": request.apply_immediately,
    }

