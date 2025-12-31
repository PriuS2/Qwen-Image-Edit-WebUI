"""
이미지 편집 모듈
- diffusers 파이프라인 연동
- 단일/다중 이미지 편집
- 스타일 변환
"""

import asyncio
import random
from typing import Optional, List, Callable, Any
from PIL import Image

from core.model_manager import get_model_manager
from core.settings_manager import get_settings_manager
from schemas.edit import EditParams, EditResult
from utils.image_utils import (
    get_image_from_source,
    save_image,
    create_thumbnail,
    encode_image_to_base64,
    image_to_url,
)
from config import get_settings


settings = get_settings()


# 스타일 프리셋 캐시 (DB에서 로드)
_style_presets_cache: dict = {}
_cache_loaded: bool = False


async def get_style_presets() -> dict:
    """
    DB에서 스타일 프리셋 로드 (캐시 사용)
    
    Returns:
        dict: {style_name: {"prompt": str, "negative_prompt": str}}
    """
    global _style_presets_cache, _cache_loaded
    
    if _cache_loaded:
        return _style_presets_cache
    
    from db.database import AsyncSessionLocal
    from db import crud
    
    async with AsyncSessionLocal() as db:
        presets = await crud.get_all_style_presets(db, enabled_only=True)
        _style_presets_cache = {
            p.name: {
                "prompt": p.prompt,
                "negative_prompt": p.negative_prompt or "",
            }
            for p in presets
        }
        _cache_loaded = True
    
    return _style_presets_cache


def invalidate_style_cache():
    """스타일 캐시 무효화 (스타일 업데이트 시 호출)"""
    global _style_presets_cache, _cache_loaded
    _style_presets_cache = {}
    _cache_loaded = False


class ImageEditor:
    """이미지 편집기"""
    
    def __init__(self):
        self._model_manager = get_model_manager()
    
    async def _ensure_model(self) -> bool:
        """모델 로드 확인"""
        if not self._model_manager.is_loaded:
            success = await self._model_manager.ensure_loaded()
            if not success:
                raise RuntimeError("Model not loaded and auto-load is disabled")
        return True
    
    async def edit_single(
        self,
        image_source: str,
        params: EditParams,
        response_format: str = "url",
        session_id: Optional[str] = None,
        save_to_gallery: bool = True,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> EditResult:
        """
        단일 이미지 편집
        
        Args:
            image_source: 이미지 소스 (Base64 또는 경로)
            params: 편집 파라미터
            response_format: 응답 형식 ("base64" 또는 "url")
            session_id: 세션 ID
            save_to_gallery: 갤러리 저장 여부
            progress_callback: 진행률 콜백
        
        Returns:
            EditResult: 편집 결과
        """
        await self._ensure_model()
        
        # 활동 시간 업데이트
        settings_manager = await get_settings_manager()
        settings_manager.update_activity()
        
        # 진행률 시작
        if progress_callback:
            await _safe_progress_callback(progress_callback, 0)
        
        # 이미지 로드
        image = get_image_from_source(image_source)
        
        # 시드 설정
        seed = params.seed if params.seed >= 0 else random.randint(0, 2**32 - 1)
        
        # 이미지 로드 완료, 편집 시작 준비
        if progress_callback:
            await _safe_progress_callback(progress_callback, 5)
        
        # 편집 실행
        result_image = await self._run_pipeline(
            images=[image],
            params=params,
            seed=seed,
            progress_callback=progress_callback,
        )
        
        # 결과 저장 및 반환 (85% ~ 100%)
        return await self._save_and_return(
            original_image=image,
            result_image=result_image,
            params=params,
            seed=seed,
            response_format=response_format,
            session_id=session_id,
            save_to_gallery=save_to_gallery,
            progress_callback=progress_callback,
        )
    
    async def edit_multi(
        self,
        image_sources: List[str],
        params: EditParams,
        response_format: str = "url",
        session_id: Optional[str] = None,
        save_to_gallery: bool = True,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> EditResult:
        """
        다중 이미지 편집 (합성)
        
        Args:
            image_sources: 이미지 소스들 (최대 3개)
            params: 편집 파라미터
            response_format: 응답 형식
            session_id: 세션 ID
            save_to_gallery: 갤러리 저장 여부
            progress_callback: 진행률 콜백
        
        Returns:
            EditResult: 편집 결과
        """
        await self._ensure_model()
        
        # 활동 시간 업데이트
        settings_manager = await get_settings_manager()
        settings_manager.update_activity()
        
        # 진행률 시작
        if progress_callback:
            await _safe_progress_callback(progress_callback, 0)
        
        # 이미지들 로드
        images = [get_image_from_source(src) for src in image_sources[:3]]
        
        # 시드 설정
        seed = params.seed if params.seed >= 0 else random.randint(0, 2**32 - 1)
        
        # 이미지 로드 완료, 편집 시작 준비
        if progress_callback:
            await _safe_progress_callback(progress_callback, 5)
        
        # 편집 실행
        result_image = await self._run_pipeline(
            images=images,
            params=params,
            seed=seed,
            progress_callback=progress_callback,
        )
        
        # 결과 저장 및 반환 (85% ~ 100%)
        return await self._save_and_return(
            original_image=images[0],
            result_image=result_image,
            params=params,
            seed=seed,
            response_format=response_format,
            session_id=session_id,
            save_to_gallery=save_to_gallery,
            progress_callback=progress_callback,
        )
    
    async def style_transfer(
        self,
        image_source: str,
        style: str,
        intensity: float = 1.0,
        additional_prompt: Optional[str] = None,
        response_format: str = "url",
        session_id: Optional[str] = None,
        save_to_gallery: bool = True,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> EditResult:
        """
        스타일 변환
        
        Args:
            image_source: 이미지 소스
            style: 스타일 이름 또는 커스텀 프롬프트
            intensity: 스타일 강도
            additional_prompt: 추가 프롬프트
            response_format: 응답 형식
            session_id: 세션 ID
            save_to_gallery: 갤러리 저장 여부
            progress_callback: 진행률 콜백
        
        Returns:
            EditResult: 편집 결과
        """
        # DB에서 스타일 프리셋 로드
        style_presets = await get_style_presets()
        
        # 스타일 프롬프트 구성
        negative_prompt = ""
        if style.lower() in style_presets:
            style_data = style_presets[style.lower()]
            prompt = style_data["prompt"]
            negative_prompt = style_data.get("negative_prompt", "")
        else:
            # 커스텀 프롬프트로 사용
            prompt = style
        
        if additional_prompt:
            prompt = f"{prompt}. {additional_prompt}"
        
        # CFG 스케일 조정 (intensity 반영)
        settings_manager = await get_settings_manager()
        app_settings = await settings_manager.get_all()
        
        params = EditParams(
            prompt=prompt,
            negative_prompt=negative_prompt if negative_prompt else " ",
            num_inference_steps=app_settings.edit_defaults.num_inference_steps,
            true_cfg_scale=app_settings.edit_defaults.true_cfg_scale * intensity,
            guidance_scale=app_settings.edit_defaults.guidance_scale,
        )
        
        return await self.edit_single(
            image_source=image_source,
            params=params,
            response_format=response_format,
            session_id=session_id,
            save_to_gallery=save_to_gallery,
            progress_callback=progress_callback,
        )
    
    async def _run_pipeline(
        self,
        images: List[Image.Image],
        params: EditParams,
        seed: int,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> Image.Image:
        """파이프라인 실행"""
        import torch
        from concurrent.futures import ThreadPoolExecutor
        
        pipeline = self._model_manager.pipeline
        total_steps = params.num_inference_steps
        
        # 진행률 상태를 저장하기 위한 컨테이너
        progress_state = {"last_progress": 5}
        
        # 이벤트 루프 참조 저장 (스레드에서 사용)
        loop = asyncio.get_event_loop()
        
        # Step 콜백 함수 (실제 진행률 업데이트)
        def step_callback(pipe, step_index, timestep, callback_kwargs):
            if progress_callback:
                # 5% ~ 85% 범위에서 step에 따라 진행률 계산
                # (0-5%: 이미지 로드, 85-100%: 저장)
                # step_index는 0부터 시작, +1 해서 완료된 step 기준으로 계산
                step_progress = 5 + int(((step_index + 1) / total_steps) * 80)
                if step_progress > progress_state["last_progress"]:
                    progress_state["last_progress"] = step_progress
                    # 스레드에서 안전하게 비동기 콜백 호출
                    loop.call_soon_threadsafe(
                        lambda p=step_progress: asyncio.ensure_future(
                            _safe_progress_callback(progress_callback, p)
                        )
                    )
            return callback_kwargs
        
        # 입력 구성
        inputs = {
            "image": images,
            "prompt": params.prompt,
            "negative_prompt": params.negative_prompt,
            "num_inference_steps": params.num_inference_steps,
            "true_cfg_scale": params.true_cfg_scale,
            "guidance_scale": params.guidance_scale,
            "generator": torch.manual_seed(seed),
            "num_images_per_prompt": 1,
            "callback_on_step_end": step_callback,
        }
        
        def run_inference():
            with torch.inference_mode():
                output = pipeline(**inputs)
                return output.images[0]
        
        result = await loop.run_in_executor(None, run_inference)
        
        if progress_callback:
            await _safe_progress_callback(progress_callback, 85)
        
        return result
    
    async def _save_and_return(
        self,
        original_image: Image.Image,
        result_image: Image.Image,
        params: EditParams,
        seed: int,
        response_format: str,
        session_id: Optional[str],
        save_to_gallery: bool,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> EditResult:
        """결과 저장 및 반환"""
        from db.database import AsyncSessionLocal
        from db import crud
        
        width, height = result_image.size
        
        gallery_id = None
        history_id = None
        
        # 이미지 저장
        if save_to_gallery or response_format == "url":
            # 결과 이미지 저장
            image_path = save_image(result_image, settings.images_dir)
            
            # 썸네일 생성 및 저장
            settings_manager = await get_settings_manager()
            app_settings = await settings_manager.get_all()
            thumbnail = create_thumbnail(result_image, app_settings.gallery.thumbnail_size)
            thumbnail_path = save_image(thumbnail, settings.thumbnails_dir)
            
            # 원본 이미지 저장
            original_path = save_image(original_image, settings.uploads_dir)
            
            if save_to_gallery:
                async with AsyncSessionLocal() as db:
                    # 히스토리 저장
                    history = await crud.create_history(
                        db=db,
                        session_id=session_id or "default",
                        original_image_path=original_path,
                        edited_image_path=image_path,
                        prompt=params.prompt,
                        parameters={
                            "negative_prompt": params.negative_prompt,
                            "num_inference_steps": params.num_inference_steps,
                            "true_cfg_scale": params.true_cfg_scale,
                            "guidance_scale": params.guidance_scale,
                            "seed": seed,
                        },
                    )
                    history_id = history.id
                    
                    # 갤러리 저장
                    gallery = await crud.create_gallery(
                        db=db,
                        image_path=image_path,
                        thumbnail_path=thumbnail_path,
                        original_image_path=original_path,
                        history_id=history_id,
                        image_metadata={
                            "width": width,
                            "height": height,
                            "prompt": params.prompt,
                            "seed": seed,
                        },
                    )
                    gallery_id = gallery.id
                    
                    await db.commit()
        
        if progress_callback:
            await _safe_progress_callback(progress_callback, 100)
        
        # 응답 형식에 따라 반환
        if response_format == "base64":
            image_data = encode_image_to_base64(result_image)
        else:
            image_data = image_to_url(image_path)
        
        return EditResult(
            image=image_data,
            format=response_format,
            width=width,
            height=height,
            seed_used=seed,
            gallery_id=gallery_id,
            history_id=history_id,
        )


async def _safe_progress_callback(callback: Callable[[int], None], progress: int) -> None:
    """진행률 콜백을 안전하게 호출"""
    try:
        result = callback(progress)
        if asyncio.iscoroutine(result):
            await result
    except Exception as e:
        print(f"Progress callback error: {e}")


# 싱글톤
_image_editor: Optional[ImageEditor] = None


def get_image_editor() -> ImageEditor:
    """이미지 편집기 인스턴스 반환"""
    global _image_editor
    if _image_editor is None:
        _image_editor = ImageEditor()
    return _image_editor

