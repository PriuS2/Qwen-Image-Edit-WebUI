"""
설정 관리 API 라우터
"""

from fastapi import APIRouter, Depends

from api.dependencies import verify_api_key
from core.settings_manager import get_settings_manager
from schemas.settings import (
    AllSettings, SettingsResponse,
    AutoUnloadSettings, AutoUnloadSettingsUpdate,
    AutoLoadSettings, AutoLoadSettingsUpdate,
)


router = APIRouter()


@router.get("", response_model=SettingsResponse)
async def get_all_settings(api_key: str = Depends(verify_api_key)):
    """전체 설정 조회"""
    settings_manager = await get_settings_manager()
    settings = await settings_manager.get_all()
    
    return SettingsResponse(success=True, data=settings)


@router.put("", response_model=SettingsResponse)
async def update_all_settings(
    settings: AllSettings,
    api_key: str = Depends(verify_api_key),
):
    """전체 설정 업데이트"""
    settings_manager = await get_settings_manager()
    await settings_manager.update_all(settings)
    
    updated = await settings_manager.get_all()
    return SettingsResponse(success=True, data=updated)


@router.get("/auto-unload", response_model=dict)
async def get_auto_unload_settings(api_key: str = Depends(verify_api_key)):
    """자동 언로드 설정 조회"""
    settings_manager = await get_settings_manager()
    settings = await settings_manager.get_all()
    
    return {
        "success": True,
        "data": settings.auto_unload.model_dump(),
        "idle_minutes": settings_manager.idle_minutes,
    }


@router.put("/auto-unload", response_model=dict)
async def update_auto_unload_settings(
    update: AutoUnloadSettingsUpdate,
    api_key: str = Depends(verify_api_key),
):
    """자동 언로드 설정 변경"""
    settings_manager = await get_settings_manager()
    
    updated = await settings_manager.update_auto_unload(
        enabled=update.enabled,
        timeout_minutes=update.timeout_minutes,
    )
    
    return {
        "success": True,
        "message": "Auto-unload settings updated",
        "data": updated.model_dump(),
    }


@router.get("/auto-load", response_model=dict)
async def get_auto_load_settings(api_key: str = Depends(verify_api_key)):
    """자동 로드 설정 조회"""
    settings_manager = await get_settings_manager()
    settings = await settings_manager.get_all()
    
    return {
        "success": True,
        "data": settings.auto_load.model_dump(),
    }


@router.put("/auto-load", response_model=dict)
async def update_auto_load_settings(
    update: AutoLoadSettingsUpdate,
    api_key: str = Depends(verify_api_key),
):
    """자동 로드 설정 변경"""
    settings_manager = await get_settings_manager()
    
    updated = await settings_manager.update_auto_load(enabled=update.enabled)
    
    return {
        "success": True,
        "message": "Auto-load settings updated",
        "data": updated.model_dump(),
    }


@router.post("/reset", response_model=SettingsResponse)
async def reset_settings(api_key: str = Depends(verify_api_key)):
    """설정 초기화 (기본값으로 리셋)"""
    settings_manager = await get_settings_manager()
    settings = await settings_manager.reset_to_defaults()
    
    return SettingsResponse(success=True, data=settings)

