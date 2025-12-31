"""
이미지 편집 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import verify_api_key
from core.queue_manager import get_queue_manager
from core.model_manager import get_model_manager
from db.models import JobType
from schemas.edit import (
    SingleEditRequest, MultiEditRequest, StyleTransferRequest,
    EditResponse, EditJobStatus,
)


router = APIRouter()


@router.post("/single", response_model=EditResponse)
async def edit_single_image(
    request: SingleEditRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    단일 이미지 편집
    
    작업이 큐에 추가되고 job_id가 반환됩니다.
    WebSocket /ws/progress/{job_id}로 진행률을 받을 수 있습니다.
    """
    # 모델 로드 확인
    model_manager = get_model_manager()
    if not await model_manager.ensure_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please load the model first or enable auto_load."
        )
    
    queue_manager = get_queue_manager()
    
    job_id = await queue_manager.submit_job(
        job_type=JobType.SINGLE,
        input_data={
            "image": request.image,
            "params": request.params.model_dump(),
            "response_format": request.response_format,
            "session_id": request.session_id,
            "save_to_gallery": request.save_to_gallery,
        },
        session_id=request.session_id,
    )
    
    return EditResponse(
        success=True,
        job_id=job_id,
        message="Job submitted successfully",
    )


@router.post("/multi", response_model=EditResponse)
async def edit_multi_images(
    request: MultiEditRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    다중 이미지 편집 (합성)
    
    최대 3개의 이미지를 합성합니다.
    """
    model_manager = get_model_manager()
    if not await model_manager.ensure_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    queue_manager = get_queue_manager()
    
    job_id = await queue_manager.submit_job(
        job_type=JobType.MULTI,
        input_data={
            "images": request.images,
            "params": request.params.model_dump(),
            "response_format": request.response_format,
            "session_id": request.session_id,
            "save_to_gallery": request.save_to_gallery,
        },
        session_id=request.session_id,
    )
    
    return EditResponse(
        success=True,
        job_id=job_id,
        message="Multi-image job submitted",
    )


@router.post("/style-transfer", response_model=EditResponse)
async def style_transfer(
    request: StyleTransferRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    스타일 변환
    
    사용 가능한 스타일:
    - ghibli: 지브리 스타일
    - anime: 애니메이션 스타일
    - realistic: 사실적 스타일
    - oil_painting: 유화 스타일
    - watercolor: 수채화 스타일
    - sketch: 스케치 스타일
    - cyberpunk: 사이버펑크 스타일
    - vintage: 빈티지 스타일
    
    또는 커스텀 프롬프트를 직접 입력할 수 있습니다.
    """
    model_manager = get_model_manager()
    if not await model_manager.ensure_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    queue_manager = get_queue_manager()
    
    job_id = await queue_manager.submit_job(
        job_type=JobType.STYLE_TRANSFER,
        input_data={
            "image": request.image,
            "style": request.style,
            "intensity": request.intensity,
            "additional_prompt": request.additional_prompt,
            "response_format": request.response_format,
            "session_id": request.session_id,
            "save_to_gallery": request.save_to_gallery,
        },
        session_id=request.session_id,
    )
    
    return EditResponse(
        success=True,
        job_id=job_id,
        message="Style transfer job submitted",
    )


@router.get("/job/{job_id}", response_model=EditJobStatus)
async def get_job_status(
    job_id: str,
    api_key: str = Depends(verify_api_key),
):
    """작업 상태 조회"""
    queue_manager = get_queue_manager()
    status = await queue_manager.get_job_status(job_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {job_id}"
        )
    
    result = None
    if status.get("output_data"):
        result = status["output_data"]
    
    return EditJobStatus(
        job_id=job_id,
        status=status["status"],
        progress=status.get("progress", 0),
        result=result,
        error=status.get("error_message"),
    )

