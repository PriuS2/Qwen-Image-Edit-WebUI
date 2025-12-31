"""
히스토리 API 라우터
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import verify_api_key
from db.database import AsyncSessionLocal
from db import crud
from schemas.history import (
    HistoryItem, HistoryListResponse, HistoryDetailResponse, UndoRedoResponse
)
from utils.image_utils import image_to_url


router = APIRouter()


@router.get("", response_model=HistoryListResponse)
async def list_history(
    session_id: Optional[str] = Query(None, description="세션 ID로 필터"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    api_key: str = Depends(verify_api_key),
):
    """작업 히스토리 목록"""
    async with AsyncSessionLocal() as db:
        if session_id:
            histories = await crud.get_history_by_session(db, session_id, limit, offset)
        else:
            # 모든 히스토리 (최신순)
            from sqlalchemy import select, desc
            from db.models import History
            
            result = await db.execute(
                select(History)
                .order_by(desc(History.created_at))
                .limit(limit)
                .offset(offset)
            )
            histories = list(result.scalars().all())
        
        items = [HistoryItem.model_validate(h) for h in histories]
        
        return HistoryListResponse(
            success=True,
            data=items,
            total=len(items),
        )


@router.get("/{history_id}", response_model=HistoryDetailResponse)
async def get_history(
    history_id: str,
    api_key: str = Depends(verify_api_key),
):
    """특정 작업 상세 조회"""
    async with AsyncSessionLocal() as db:
        history = await crud.get_history_by_id(db, history_id)
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"History not found: {history_id}"
            )
        
        return HistoryDetailResponse(
            success=True,
            data=HistoryItem.model_validate(history),
        )


@router.post("/{history_id}/undo", response_model=UndoRedoResponse)
async def undo_edit(
    history_id: str,
    api_key: str = Depends(verify_api_key),
):
    """
    이전 상태로 복원 (Undo)
    
    현재 히스토리의 parent로 이동합니다.
    """
    async with AsyncSessionLocal() as db:
        history = await crud.get_history_by_id(db, history_id)
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"History not found: {history_id}"
            )
        
        # parent가 없으면 더 이상 undo 불가
        if not history.parent_id:
            return UndoRedoResponse(
                success=True,
                message="Already at the beginning, cannot undo further",
                current_position=history.position,
                image_path=image_to_url(history.original_image_path),
                can_undo=False,
                can_redo=True,
            )
        
        # parent 히스토리 조회
        parent = await crud.get_history_by_id(db, history.parent_id)
        
        if not parent:
            raise HTTPException(
                status_code=404,
                detail="Parent history not found"
            )
        
        # 현재 위치에서 parent의 편집 이미지 또는 원본 반환
        image_path = parent.edited_image_path or parent.original_image_path
        
        # parent에 더 parent가 있는지 확인
        can_undo = parent.parent_id is not None
        
        return UndoRedoResponse(
            success=True,
            message="Undo successful",
            current_position=parent.position,
            image_path=image_to_url(image_path),
            can_undo=can_undo,
            can_redo=True,
        )


@router.post("/{history_id}/redo", response_model=UndoRedoResponse)
async def redo_edit(
    history_id: str,
    api_key: str = Depends(verify_api_key),
):
    """
    다음 상태로 복원 (Redo)
    
    현재 히스토리의 child로 이동합니다.
    """
    async with AsyncSessionLocal() as db:
        history = await crud.get_history_by_id(db, history_id)
        
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"History not found: {history_id}"
            )
        
        # children 확인
        from sqlalchemy import select
        from db.models import History
        
        result = await db.execute(
            select(History)
            .where(History.parent_id == history_id)
            .order_by(History.created_at.desc())
            .limit(1)
        )
        child = result.scalar_one_or_none()
        
        if not child:
            return UndoRedoResponse(
                success=True,
                message="Already at the latest, cannot redo further",
                current_position=history.position,
                image_path=image_to_url(history.edited_image_path or history.original_image_path),
                can_undo=history.parent_id is not None,
                can_redo=False,
            )
        
        image_path = child.edited_image_path or child.original_image_path
        
        # child에 더 child가 있는지 확인
        result = await db.execute(
            select(History)
            .where(History.parent_id == child.id)
            .limit(1)
        )
        can_redo = result.scalar_one_or_none() is not None
        
        return UndoRedoResponse(
            success=True,
            message="Redo successful",
            current_position=child.position,
            image_path=image_to_url(image_path),
            can_undo=True,
            can_redo=can_redo,
        )


@router.delete("/{history_id}", response_model=dict)
async def delete_history(
    history_id: str,
    api_key: str = Depends(verify_api_key),
):
    """히스토리 항목 삭제"""
    async with AsyncSessionLocal() as db:
        deleted = await crud.delete_history(db, history_id)
        await db.commit()
        
        if deleted:
            return {
                "success": True,
                "message": f"History {history_id} deleted",
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"History not found: {history_id}"
            )

