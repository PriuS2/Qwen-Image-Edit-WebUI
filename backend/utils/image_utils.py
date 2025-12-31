"""
이미지 유틸리티 모듈
"""

import io
import base64
import uuid
from pathlib import Path
from typing import Optional, Tuple, Union
from PIL import Image

from config import get_settings


settings = get_settings()


def decode_base64_image(base64_str: str) -> Image.Image:
    """Base64 문자열을 PIL 이미지로 디코딩"""
    # data:image/xxx;base64, 접두사 제거
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
    
    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))
    
    # RGBA를 RGB로 변환
    if image.mode == "RGBA":
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    elif image.mode != "RGB":
        image = image.convert("RGB")
    
    return image


def encode_image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """PIL 이미지를 Base64 문자열로 인코딩"""
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def save_image(
    image: Image.Image,
    directory: Path,
    filename: Optional[str] = None,
    format: str = "PNG",
) -> str:
    """
    이미지 저장
    
    Args:
        image: PIL 이미지
        directory: 저장 디렉토리
        filename: 파일명 (없으면 UUID 생성)
        format: 이미지 포맷
    
    Returns:
        str: 저장된 파일 경로 (상대 경로)
    """
    directory.mkdir(parents=True, exist_ok=True)
    
    if filename is None:
        ext = format.lower()
        if ext == "jpeg":
            ext = "jpg"
        filename = f"{uuid.uuid4()}.{ext}"
    
    filepath = directory / filename
    image.save(filepath, format=format)
    
    # storage 기준 상대 경로 반환
    try:
        relative_path = filepath.relative_to(settings.storage_dir)
        return str(relative_path).replace("\\", "/")
    except ValueError:
        return str(filepath)


def create_thumbnail(
    image: Image.Image,
    size: int = 256,
) -> Image.Image:
    """
    썸네일 생성
    
    Args:
        image: 원본 이미지
        size: 썸네일 크기
    
    Returns:
        Image.Image: 썸네일 이미지
    """
    thumbnail = image.copy()
    thumbnail.thumbnail((size, size), Image.Resampling.LANCZOS)
    return thumbnail


def get_image_from_source(source: str) -> Image.Image:
    """
    소스에서 이미지 가져오기
    
    Args:
        source: Base64 문자열 또는 파일 경로
    
    Returns:
        Image.Image: PIL 이미지
    """
    # Base64인 경우
    if source.startswith("data:") or len(source) > 500:
        return decode_base64_image(source)
    
    # URL인 경우
    if source.startswith("http://") or source.startswith("https://"):
        import requests
        response = requests.get(source)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGB")
    
    # 파일 경로인 경우
    filepath = Path(source)
    if not filepath.is_absolute():
        filepath = settings.storage_dir / source
    
    return Image.open(filepath).convert("RGB")


def get_image_size(image: Image.Image) -> Tuple[int, int]:
    """이미지 크기 반환 (width, height)"""
    return image.size


def image_to_url(relative_path: str) -> str:
    """상대 경로를 URL로 변환"""
    return f"/storage/{relative_path}"

