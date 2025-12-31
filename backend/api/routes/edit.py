"""
이미지 편집 API 라우터
"""

import base64
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from api.dependencies import verify_api_key
from core.queue_manager import get_queue_manager
from core.model_manager import get_model_manager
from db.models import JobType
from schemas.edit import (
    SingleEditRequest, MultiEditRequest, StyleTransferRequest,
    EditResponse, EditJobStatus,
)


router = APIRouter()


async def file_to_base64(file: UploadFile) -> str:
    """UploadFile을 Base64 문자열로 변환"""
    content = await file.read()
    base64_str = base64.b64encode(content).decode("utf-8")
    
    # MIME 타입 추출
    content_type = file.content_type or "image/png"
    
    return f"data:{content_type};base64,{base64_str}"


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


# ═══════════════════════════════════════════════════════════════
# 파일 업로드 방식 엔드포인트
# ═══════════════════════════════════════════════════════════════

@router.post("/upload/single", response_model=EditResponse)
async def edit_single_image_upload(
    image: UploadFile = File(..., description="편집할 이미지 파일"),
    prompt: str = Form(..., description="편집 지시 프롬프트"),
    negative_prompt: str = Form(default=" ", description="제외할 요소"),
    num_inference_steps: int = Form(default=20, ge=1, le=100, description="추론 스텝 수"),
    true_cfg_scale: float = Form(default=4.0, ge=1.0, le=20.0, description="True CFG 스케일"),
    guidance_scale: float = Form(default=1.0, ge=0.0, le=20.0, description="가이던스 스케일"),
    seed: int = Form(default=-1, description="시드 (-1: 랜덤)"),
    num_images_per_prompt: int = Form(default=1, ge=1, le=4, description="생성할 이미지 수"),
    response_format: str = Form(default="url", description="응답 형식: 'url' 또는 'base64'"),
    session_id: Optional[str] = Form(default=None, description="세션 ID"),
    save_to_gallery: bool = Form(default=True, description="갤러리에 저장"),
    api_key: str = Depends(verify_api_key),
):
    """
    파일 업로드로 단일 이미지 편집
    
    이미지를 직접 업로드하여 편집합니다.
    
    **응답 형식 (response_format):**
    - `url`: 저장된 이미지의 URL 반환 (기본값)
    - `base64`: Base64 인코딩된 이미지 데이터 반환
    """
    # 파일 타입 검증
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only image files are allowed."
        )
    
    # 모델 로드 확인
    model_manager = get_model_manager()
    if not await model_manager.ensure_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please load the model first or enable auto_load."
        )
    
    # 이미지를 Base64로 변환
    image_base64 = await file_to_base64(image)
    
    queue_manager = get_queue_manager()
    
    job_id = await queue_manager.submit_job(
        job_type=JobType.SINGLE,
        input_data={
            "image": image_base64,
            "params": {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": num_inference_steps,
                "true_cfg_scale": true_cfg_scale,
                "guidance_scale": guidance_scale,
                "seed": seed,
                "num_images_per_prompt": num_images_per_prompt,
            },
            "response_format": response_format,
            "session_id": session_id,
            "save_to_gallery": save_to_gallery,
        },
        session_id=session_id,
    )
    
    return EditResponse(
        success=True,
        job_id=job_id,
        message="File upload job submitted successfully",
    )


@router.post("/upload/multi", response_model=EditResponse)
async def edit_multi_images_upload(
    images: List[UploadFile] = File(..., description="편집할 이미지 파일들 (최대 3개)"),
    prompt: str = Form(..., description="편집 지시 프롬프트"),
    negative_prompt: str = Form(default=" ", description="제외할 요소"),
    num_inference_steps: int = Form(default=20, ge=1, le=100),
    true_cfg_scale: float = Form(default=4.0, ge=1.0, le=20.0),
    guidance_scale: float = Form(default=1.0, ge=0.0, le=20.0),
    seed: int = Form(default=-1),
    num_images_per_prompt: int = Form(default=1, ge=1, le=4),
    response_format: str = Form(default="url", description="응답 형식: 'url' 또는 'base64'"),
    session_id: Optional[str] = Form(default=None),
    save_to_gallery: bool = Form(default=True),
    api_key: str = Depends(verify_api_key),
):
    """
    파일 업로드로 다중 이미지 편집 (합성)
    
    최대 3개의 이미지를 업로드하여 합성합니다.
    
    **응답 형식 (response_format):**
    - `url`: 저장된 이미지의 URL 반환 (기본값)
    - `base64`: Base64 인코딩된 이미지 데이터 반환
    """
    if len(images) > 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum 3 images allowed"
        )
    
    # 파일 타입 검증
    for img in images:
        if not img.content_type or not img.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type for {img.filename}. Only image files are allowed."
            )
    
    model_manager = get_model_manager()
    if not await model_manager.ensure_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    # 이미지들을 Base64로 변환
    images_base64 = [await file_to_base64(img) for img in images]
    
    queue_manager = get_queue_manager()
    
    job_id = await queue_manager.submit_job(
        job_type=JobType.MULTI,
        input_data={
            "images": images_base64,
            "params": {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "num_inference_steps": num_inference_steps,
                "true_cfg_scale": true_cfg_scale,
                "guidance_scale": guidance_scale,
                "seed": seed,
                "num_images_per_prompt": num_images_per_prompt,
            },
            "response_format": response_format,
            "session_id": session_id,
            "save_to_gallery": save_to_gallery,
        },
        session_id=session_id,
    )
    
    return EditResponse(
        success=True,
        job_id=job_id,
        message="Multi-image file upload job submitted",
    )


@router.post("/upload/style-transfer", response_model=EditResponse)
async def style_transfer_upload(
    image: UploadFile = File(..., description="스타일 변환할 이미지 파일"),
    style: str = Form(..., description="스타일 (ghibli, anime, realistic, oil_painting, watercolor, sketch, cyberpunk, vintage)"),
    intensity: float = Form(default=1.0, ge=0.1, le=2.0, description="스타일 강도"),
    additional_prompt: Optional[str] = Form(default=None, description="추가 프롬프트"),
    response_format: str = Form(default="url", description="응답 형식: 'url' 또는 'base64'"),
    session_id: Optional[str] = Form(default=None),
    save_to_gallery: bool = Form(default=True),
    api_key: str = Depends(verify_api_key),
):
    """
    파일 업로드로 스타일 변환
    
    **사용 가능한 스타일:**
    - ghibli: 지브리 스타일
    - anime: 애니메이션 스타일
    - realistic: 사실적 스타일
    - oil_painting: 유화 스타일
    - watercolor: 수채화 스타일
    - sketch: 스케치 스타일
    - cyberpunk: 사이버펑크 스타일
    - vintage: 빈티지 스타일
    
    **응답 형식 (response_format):**
    - `url`: 저장된 이미지의 URL 반환 (기본값)
    - `base64`: Base64 인코딩된 이미지 데이터 반환
    """
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only image files are allowed."
        )
    
    model_manager = get_model_manager()
    if not await model_manager.ensure_loaded():
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    image_base64 = await file_to_base64(image)
    
    queue_manager = get_queue_manager()
    
    job_id = await queue_manager.submit_job(
        job_type=JobType.STYLE_TRANSFER,
        input_data={
            "image": image_base64,
            "style": style,
            "intensity": intensity,
            "additional_prompt": additional_prompt,
            "response_format": response_format,
            "session_id": session_id,
            "save_to_gallery": save_to_gallery,
        },
        session_id=session_id,
    )
    
    return EditResponse(
        success=True,
        job_id=job_id,
        message="Style transfer file upload job submitted",
    )

