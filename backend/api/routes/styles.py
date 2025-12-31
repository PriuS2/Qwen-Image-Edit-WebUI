"""
스타일 프리셋 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import verify_api_key
from db.database import AsyncSessionLocal
from db import crud
from schemas.style import (
    StylePresetCreate,
    StylePresetUpdate,
    StylePresetResponse,
    StylePresetListResponse,
    StylePresetSingleResponse,
    StylePresetDeleteResponse,
    DEFAULT_STYLE_PRESETS,
)
from core.image_editor import invalidate_style_cache


router = APIRouter()


async def initialize_default_styles():
    """기본 스타일 프리셋 초기화 (앱 시작 시 호출)"""
    async with AsyncSessionLocal() as db:
        count = await crud.get_style_presets_count(db)
        if count == 0:
            # 기본 스타일 프리셋 생성
            for preset_data in DEFAULT_STYLE_PRESETS:
                await crud.create_style_preset(
                    db=db,
                    name=preset_data["name"],
                    label=preset_data["label"],
                    description=preset_data.get("description"),
                    icon=preset_data.get("icon", "🎨"),
                    prompt=preset_data["prompt"],
                    negative_prompt=preset_data.get("negative_prompt", ""),
                    is_builtin=preset_data.get("is_builtin", True),
                    sort_order=preset_data.get("sort_order", 0),
                )
            await db.commit()
            print(f"✅ Initialized {len(DEFAULT_STYLE_PRESETS)} default style presets")


@router.get("", response_model=StylePresetListResponse)
async def get_all_styles(
    enabled_only: bool = False,
    api_key: str = Depends(verify_api_key),
):
    """
    모든 스타일 프리셋 조회
    
    - **enabled_only**: True면 활성화된 스타일만 반환
    """
    async with AsyncSessionLocal() as db:
        presets = await crud.get_all_style_presets(db, enabled_only=enabled_only)
        return StylePresetListResponse(
            success=True,
            data=[
                StylePresetResponse(
                    id=p.id,
                    name=p.name,
                    label=p.label,
                    description=p.description,
                    icon=p.icon,
                    prompt=p.prompt,
                    negative_prompt=p.negative_prompt or "",
                    is_builtin=p.is_builtin,
                    is_enabled=p.is_enabled,
                    sort_order=p.sort_order,
                    created_at=p.created_at.isoformat() if p.created_at else None,
                    updated_at=p.updated_at.isoformat() if p.updated_at else None,
                )
                for p in presets
            ]
        )


@router.get("/{style_id}", response_model=StylePresetSingleResponse)
async def get_style(
    style_id: str,
    api_key: str = Depends(verify_api_key),
):
    """
    특정 스타일 프리셋 조회
    
    style_id는 UUID 또는 스타일 이름(예: ghibli)을 사용할 수 있습니다.
    """
    async with AsyncSessionLocal() as db:
        # ID로 먼저 시도
        preset = await crud.get_style_preset_by_id(db, style_id)
        if not preset:
            # 이름으로 시도
            preset = await crud.get_style_preset_by_name(db, style_id)
        
        if not preset:
            raise HTTPException(status_code=404, detail=f"Style not found: {style_id}")
        
        return StylePresetSingleResponse(
            success=True,
            data=StylePresetResponse(
                id=preset.id,
                name=preset.name,
                label=preset.label,
                description=preset.description,
                icon=preset.icon,
                prompt=preset.prompt,
                negative_prompt=preset.negative_prompt or "",
                is_builtin=preset.is_builtin,
                is_enabled=preset.is_enabled,
                sort_order=preset.sort_order,
                created_at=preset.created_at.isoformat() if preset.created_at else None,
                updated_at=preset.updated_at.isoformat() if preset.updated_at else None,
            )
        )


@router.post("", response_model=StylePresetSingleResponse)
async def create_style(
    request: StylePresetCreate,
    api_key: str = Depends(verify_api_key),
):
    """
    새 스타일 프리셋 생성
    """
    async with AsyncSessionLocal() as db:
        # 이름 중복 확인
        if await crud.style_preset_exists(db, request.name):
            raise HTTPException(
                status_code=400,
                detail=f"Style name already exists: {request.name}"
            )
        
        preset = await crud.create_style_preset(
            db=db,
            name=request.name,
            label=request.label,
            description=request.description,
            icon=request.icon,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            is_builtin=False,  # 사용자 생성 스타일
            is_enabled=request.is_enabled,
            sort_order=request.sort_order,
        )
        await db.commit()
        
        # 스타일 캐시 무효화
        invalidate_style_cache()
        
        return StylePresetSingleResponse(
            success=True,
            data=StylePresetResponse(
                id=preset.id,
                name=preset.name,
                label=preset.label,
                description=preset.description,
                icon=preset.icon,
                prompt=preset.prompt,
                negative_prompt=preset.negative_prompt or "",
                is_builtin=preset.is_builtin,
                is_enabled=preset.is_enabled,
                sort_order=preset.sort_order,
                created_at=preset.created_at.isoformat() if preset.created_at else None,
                updated_at=preset.updated_at.isoformat() if preset.updated_at else None,
            )
        )


@router.put("/{style_id}", response_model=StylePresetSingleResponse)
async def update_style(
    style_id: str,
    request: StylePresetUpdate,
    api_key: str = Depends(verify_api_key),
):
    """
    스타일 프리셋 업데이트
    
    style_id는 UUID 또는 스타일 이름을 사용할 수 있습니다.
    """
    async with AsyncSessionLocal() as db:
        # ID로 먼저 시도
        preset = await crud.get_style_preset_by_id(db, style_id)
        if not preset:
            # 이름으로 시도
            preset = await crud.get_style_preset_by_name(db, style_id)
        
        if not preset:
            raise HTTPException(status_code=404, detail=f"Style not found: {style_id}")
        
        # 이름 변경 시 중복 확인
        if request.name and request.name != preset.name:
            if await crud.style_preset_exists(db, request.name):
                raise HTTPException(
                    status_code=400,
                    detail=f"Style name already exists: {request.name}"
                )
        
        # 업데이트
        update_data = request.model_dump(exclude_unset=True)
        updated_preset = await crud.update_style_preset(db, preset.id, **update_data)
        
        # 스타일 캐시 무효화
        invalidate_style_cache()
        
        return StylePresetSingleResponse(
            success=True,
            data=StylePresetResponse(
                id=updated_preset.id,
                name=updated_preset.name,
                label=updated_preset.label,
                description=updated_preset.description,
                icon=updated_preset.icon,
                prompt=updated_preset.prompt,
                negative_prompt=updated_preset.negative_prompt or "",
                is_builtin=updated_preset.is_builtin,
                is_enabled=updated_preset.is_enabled,
                sort_order=updated_preset.sort_order,
                created_at=updated_preset.created_at.isoformat() if updated_preset.created_at else None,
                updated_at=updated_preset.updated_at.isoformat() if updated_preset.updated_at else None,
            )
        )


@router.delete("/{style_id}", response_model=StylePresetDeleteResponse)
async def delete_style(
    style_id: str,
    api_key: str = Depends(verify_api_key),
):
    """
    스타일 프리셋 삭제
    
    기본 제공 스타일(is_builtin=True)은 삭제할 수 없습니다.
    """
    async with AsyncSessionLocal() as db:
        # ID로 먼저 시도
        preset = await crud.get_style_preset_by_id(db, style_id)
        if not preset:
            # 이름으로 시도
            preset = await crud.get_style_preset_by_name(db, style_id)
        
        if not preset:
            raise HTTPException(status_code=404, detail=f"Style not found: {style_id}")
        
        if preset.is_builtin:
            raise HTTPException(
                status_code=400,
                detail="기본 제공 스타일은 삭제할 수 없습니다. 비활성화만 가능합니다."
            )
        
        await crud.delete_style_preset(db, preset.id)
        
        # 스타일 캐시 무효화
        invalidate_style_cache()
        
        return StylePresetDeleteResponse(
            success=True,
            message=f"스타일 '{preset.label}'이(가) 삭제되었습니다."
        )


@router.post("/reset", response_model=StylePresetListResponse)
async def reset_styles(
    api_key: str = Depends(verify_api_key),
):
    """
    스타일 프리셋 초기화
    
    사용자 정의 스타일을 모두 삭제하고 기본 스타일을 원래 프롬프트로 복원합니다.
    """
    async with AsyncSessionLocal() as db:
        # 사용자 정의 스타일 삭제
        await crud.delete_non_builtin_style_presets(db)
        
        # 기본 스타일 복원
        for preset_data in DEFAULT_STYLE_PRESETS:
            existing = await crud.get_style_preset_by_name(db, preset_data["name"])
            if existing:
                # 기존 스타일 업데이트
                await crud.update_style_preset(
                    db, 
                    existing.id,
                    label=preset_data["label"],
                    description=preset_data.get("description"),
                    icon=preset_data.get("icon", "🎨"),
                    prompt=preset_data["prompt"],
                    negative_prompt=preset_data.get("negative_prompt", ""),
                    is_enabled=True,
                    sort_order=preset_data.get("sort_order", 0),
                )
            else:
                # 새로 생성
                await crud.create_style_preset(
                    db=db,
                    name=preset_data["name"],
                    label=preset_data["label"],
                    description=preset_data.get("description"),
                    icon=preset_data.get("icon", "🎨"),
                    prompt=preset_data["prompt"],
                    negative_prompt=preset_data.get("negative_prompt", ""),
                    is_builtin=True,
                    sort_order=preset_data.get("sort_order", 0),
                )
        
        await db.commit()
        
        # 스타일 캐시 무효화
        invalidate_style_cache()
        
        # 전체 목록 반환
        presets = await crud.get_all_style_presets(db)
        return StylePresetListResponse(
            success=True,
            data=[
                StylePresetResponse(
                    id=p.id,
                    name=p.name,
                    label=p.label,
                    description=p.description,
                    icon=p.icon,
                    prompt=p.prompt,
                    negative_prompt=p.negative_prompt or "",
                    is_builtin=p.is_builtin,
                    is_enabled=p.is_enabled,
                    sort_order=p.sort_order,
                    created_at=p.created_at.isoformat() if p.created_at else None,
                    updated_at=p.updated_at.isoformat() if p.updated_at else None,
                )
                for p in presets
            ]
        )
