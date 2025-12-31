"""
이미지 편집 관련 스키마
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class EditParams(BaseModel):
    """편집 파라미터"""
    prompt: str = Field(description="편집 지시 프롬프트")
    negative_prompt: str = Field(default=" ", description="제외할 요소")
    num_inference_steps: int = Field(default=20, ge=1, le=100, description="추론 스텝 수")
    true_cfg_scale: float = Field(default=4.0, ge=1.0, le=20.0, description="True CFG 스케일")
    guidance_scale: float = Field(default=1.0, ge=0.0, le=20.0, description="가이던스 스케일")
    seed: int = Field(default=-1, description="시드 (-1: 랜덤)")
    num_images_per_prompt: int = Field(default=1, ge=1, le=4, description="생성할 이미지 수")


class SingleEditRequest(BaseModel):
    """단일 이미지 편집 요청"""
    image: str = Field(description="Base64 인코딩된 이미지 또는 URL")
    params: EditParams
    response_format: Literal["base64", "url"] = Field(default="url", description="응답 형식")
    session_id: Optional[str] = Field(default=None, description="세션 ID (히스토리용)")
    save_to_gallery: bool = Field(default=True, description="갤러리에 저장")


class MultiEditRequest(BaseModel):
    """다중 이미지 편집 요청 (합성)"""
    images: List[str] = Field(
        description="Base64 인코딩된 이미지들 (최대 3개)",
        min_length=1,
        max_length=3
    )
    params: EditParams
    response_format: Literal["base64", "url"] = Field(default="url")
    session_id: Optional[str] = Field(default=None)
    save_to_gallery: bool = Field(default=True)


class StyleTransferRequest(BaseModel):
    """스타일 변환 요청"""
    image: str = Field(description="Base64 인코딩된 이미지 또는 URL")
    style: str = Field(description="스타일 (예: 'ghibli', 'anime', 'realistic')")
    intensity: float = Field(default=1.0, ge=0.1, le=2.0, description="스타일 강도")
    additional_prompt: Optional[str] = Field(default=None, description="추가 프롬프트")
    response_format: Literal["base64", "url"] = Field(default="url")
    session_id: Optional[str] = Field(default=None)
    save_to_gallery: bool = Field(default=True)


class EditResult(BaseModel):
    """편집 결과"""
    image: str = Field(description="결과 이미지 (Base64 또는 URL)")
    format: Literal["base64", "url"]
    width: int
    height: int
    seed_used: int
    gallery_id: Optional[str] = None
    history_id: Optional[str] = None


class EditResponse(BaseModel):
    """편집 응답"""
    success: bool = True
    job_id: str = Field(description="작업 ID")
    message: str = Field(default="Job submitted")


class EditResultResponse(BaseModel):
    """편집 결과 응답 (완료 시)"""
    success: bool = True
    data: EditResult


class EditJobStatus(BaseModel):
    """편집 작업 상태"""
    job_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    result: Optional[EditResult] = None
    error: Optional[str] = None

