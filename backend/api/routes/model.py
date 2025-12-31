"""
모델 관리 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import verify_api_key
from core.model_manager import get_model_manager
from core.settings_manager import get_settings_manager
from schemas.model import (
    ModelStatus, ModelStatusResponse,
    ModelLoadRequest, ModelLoadResponse,
    ModelUnloadResponse, OptimizationUpdateRequest,
)
from schemas.settings import OptimizationSettings


router = APIRouter()


@router.get("/status", response_model=ModelStatusResponse)
async def get_model_status(api_key: str = Depends(verify_api_key)):
    """모델 상태 조회"""
    model_manager = get_model_manager()
    status = model_manager.get_status()
    
    return ModelStatusResponse(success=True, data=status)


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

