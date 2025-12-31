"""
갤러리 API 라우터
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from api.dependencies import verify_api_key
from db.database import AsyncSessionLocal
from db import crud
from config import get_settings
from utils.image_utils import image_to_url
from utils.file_utils import delete_file


settings = get_settings()

router = APIRouter()


@router.get("", response_model=dict)
async def list_gallery(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    favorites_only: bool = Query(False),
    api_key: str = Depends(verify_api_key),
):
    """생성된 이미지 목록"""
    async with AsyncSessionLocal() as db:
        items = await crud.get_gallery_list(
            db,
            limit=limit,
            offset=offset,
            favorites_only=favorites_only,
        )
        
        result = []
        for item in items:
            result.append({
                "id": item.id,
                "image_url": image_to_url(item.image_path),
                "thumbnail_url": image_to_url(item.thumbnail_path) if item.thumbnail_path else None,
                "title": item.title,
                "description": item.description,
                "is_favorite": item.is_favorite,
                "metadata": item.metadata,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            })
        
        return {
            "success": True,
            "data": result,
            "total": len(result),
            "limit": limit,
            "offset": offset,
        }


@router.get("/{gallery_id}", response_model=dict)
async def get_gallery_item(
    gallery_id: str,
    api_key: str = Depends(verify_api_key),
):
    """이미지 상세 정보"""
    async with AsyncSessionLocal() as db:
        item = await crud.get_gallery_by_id(db, gallery_id)
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Gallery item not found: {gallery_id}"
            )
        
        return {
            "success": True,
            "data": {
                "id": item.id,
                "image_url": image_to_url(item.image_path),
                "thumbnail_url": image_to_url(item.thumbnail_path) if item.thumbnail_path else None,
                "original_image_url": image_to_url(item.original_image_path) if item.original_image_path else None,
                "title": item.title,
                "description": item.description,
                "is_favorite": item.is_favorite,
                "metadata": item.metadata,
                "history_id": item.history_id,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            },
        }


@router.get("/{gallery_id}/compare", response_model=dict)
async def compare_images(
    gallery_id: str,
    api_key: str = Depends(verify_api_key),
):
    """원본/편집 이미지 비교 데이터"""
    async with AsyncSessionLocal() as db:
        item = await crud.get_gallery_by_id(db, gallery_id)
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Gallery item not found: {gallery_id}"
            )
        
        if not item.original_image_path:
            raise HTTPException(
                status_code=400,
                detail="Original image not available for comparison"
            )
        
        return {
            "success": True,
            "data": {
                "original_url": image_to_url(item.original_image_path),
                "edited_url": image_to_url(item.image_path),
                "metadata": item.metadata,
            },
        }


@router.delete("/{gallery_id}", response_model=dict)
async def delete_gallery_item(
    gallery_id: str,
    delete_files: bool = Query(True, description="파일도 함께 삭제"),
    api_key: str = Depends(verify_api_key),
):
    """갤러리 아이템 삭제"""
    async with AsyncSessionLocal() as db:
        item = await crud.get_gallery_by_id(db, gallery_id)
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Gallery item not found: {gallery_id}"
            )
        
        # 파일 삭제
        if delete_files:
            if item.image_path:
                delete_file(item.image_path)
            if item.thumbnail_path:
                delete_file(item.thumbnail_path)
        
        # DB 삭제
        await crud.delete_gallery(db, gallery_id)
        await db.commit()
        
        return {
            "success": True,
            "message": f"Gallery item {gallery_id} deleted",
        }


@router.get("/{gallery_id}/download")
async def download_image(
    gallery_id: str,
    api_key: str = Depends(verify_api_key),
):
    """이미지 다운로드"""
    async with AsyncSessionLocal() as db:
        item = await crud.get_gallery_by_id(db, gallery_id)
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Gallery item not found: {gallery_id}"
            )
        
        file_path = settings.storage_dir / item.image_path
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Image file not found"
            )
        
        filename = item.title or f"image_{gallery_id}.png"
        if not filename.endswith((".png", ".jpg", ".jpeg")):
            filename += ".png"
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="image/png",
        )


@router.patch("/{gallery_id}", response_model=dict)
async def update_gallery_item(
    gallery_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_favorite: Optional[bool] = None,
    api_key: str = Depends(verify_api_key),
):
    """갤러리 아이템 업데이트"""
    async with AsyncSessionLocal() as db:
        updates = {}
        if title is not None:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        if is_favorite is not None:
            updates["is_favorite"] = is_favorite
        
        if not updates:
            raise HTTPException(
                status_code=400,
                detail="No update fields provided"
            )
        
        item = await crud.update_gallery(db, gallery_id, **updates)
        await db.commit()
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Gallery item not found: {gallery_id}"
            )
        
        return {
            "success": True,
            "message": "Gallery item updated",
        }

