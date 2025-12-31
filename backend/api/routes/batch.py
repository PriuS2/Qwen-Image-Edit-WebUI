"""
배치 처리 API 라우터
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import verify_api_key
from core.queue_manager import get_queue_manager
from core.model_manager import get_model_manager
from db.database import AsyncSessionLocal
from db import crud
from db.models import JobType, JobStatus
from schemas.job import BatchSubmitRequest, BatchSubmitResponse, JobItem, JobListResponse


router = APIRouter()


@router.post("/submit", response_model=BatchSubmitResponse)
async def submit_batch(
    request: BatchSubmitRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    배치 작업 제출
    
    여러 이미지를 한 번에 처리합니다.
    각 아이템은 {image: string, params: EditParams} 형식이어야 합니다.
    """
    if not request.items:
        raise HTTPException(
            status_code=400,
            detail="No items provided"
        )
    
    model_manager = get_model_manager()
    if not await model_manager.ensure_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    queue_manager = get_queue_manager()
    
    job_id = await queue_manager.submit_job(
        job_type=JobType.BATCH,
        input_data={
            "items": request.items,
            "response_format": request.response_format,
            "session_id": request.session_id,
            "save_to_gallery": request.save_to_gallery,
        },
        session_id=request.session_id,
    )
    
    return BatchSubmitResponse(
        success=True,
        job_id=job_id,
        total_items=len(request.items),
        message=f"Batch job submitted with {len(request.items)} items",
    )


@router.get("/{job_id}", response_model=dict)
async def get_batch_status(
    job_id: str,
    api_key: str = Depends(verify_api_key),
):
    """배치 작업 상태 조회"""
    queue_manager = get_queue_manager()
    status = await queue_manager.get_job_status(job_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Batch job not found: {job_id}"
        )
    
    return {
        "success": True,
        "data": status,
    }


@router.delete("/{job_id}", response_model=dict)
async def cancel_batch(
    job_id: str,
    api_key: str = Depends(verify_api_key),
):
    """배치 작업 취소"""
    queue_manager = get_queue_manager()
    
    cancelled = await queue_manager.cancel_job(job_id)
    
    if cancelled:
        return {
            "success": True,
            "message": f"Batch job {job_id} cancelled",
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel job (already processing or completed)"
        )


@router.get("/list", response_model=JobListResponse)
async def list_batch_jobs(
    session_id: Optional[str] = None,
    limit: int = 50,
    api_key: str = Depends(verify_api_key),
):
    """진행 중인 배치 작업 목록"""
    async with AsyncSessionLocal() as db:
        if session_id:
            jobs = await crud.get_jobs_by_session(db, session_id, limit)
        else:
            # 모든 배치 작업 (pending, processing 상태)
            from sqlalchemy import select, or_
            from db.models import Job
            
            result = await db.execute(
                select(Job)
                .where(Job.type == JobType.BATCH)
                .where(or_(
                    Job.status == JobStatus.PENDING,
                    Job.status == JobStatus.PROCESSING,
                ))
                .limit(limit)
            )
            jobs = list(result.scalars().all())
        
        items = [JobItem.model_validate(job) for job in jobs]
        
        return JobListResponse(
            success=True,
            data=items,
            total=len(items),
        )

