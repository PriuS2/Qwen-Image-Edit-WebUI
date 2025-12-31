"""
스타일 프리셋 관련 스키마
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class StylePresetBase(BaseModel):
    """스타일 프리셋 기본 스키마"""
    name: str = Field(description="스타일 고유 ID (예: ghibli, anime)")
    label: str = Field(description="표시 이름 (예: Ghibli, Anime)")
    description: Optional[str] = Field(default=None, description="스타일 설명")
    icon: str = Field(default="🎨", description="이모지 아이콘")
    prompt: str = Field(description="스타일 적용 프롬프트")
    negative_prompt: str = Field(default="", description="네거티브 프롬프트")
    is_enabled: bool = Field(default=True, description="활성화 여부")
    sort_order: int = Field(default=0, description="정렬 순서")


class StylePresetCreate(StylePresetBase):
    """스타일 프리셋 생성 요청"""
    pass


class StylePresetUpdate(BaseModel):
    """스타일 프리셋 업데이트 요청"""
    name: Optional[str] = Field(default=None, description="스타일 고유 ID")
    label: Optional[str] = Field(default=None, description="표시 이름")
    description: Optional[str] = Field(default=None, description="스타일 설명")
    icon: Optional[str] = Field(default=None, description="이모지 아이콘")
    prompt: Optional[str] = Field(default=None, description="스타일 적용 프롬프트")
    negative_prompt: Optional[str] = Field(default=None, description="네거티브 프롬프트")
    is_enabled: Optional[bool] = Field(default=None, description="활성화 여부")
    sort_order: Optional[int] = Field(default=None, description="정렬 순서")


class StylePresetResponse(StylePresetBase):
    """스타일 프리셋 응답"""
    id: str
    is_builtin: bool = Field(default=False, description="기본 제공 스타일 여부")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class StylePresetListResponse(BaseModel):
    """스타일 프리셋 목록 응답"""
    success: bool = True
    data: List[StylePresetResponse]


class StylePresetSingleResponse(BaseModel):
    """단일 스타일 프리셋 응답"""
    success: bool = True
    data: StylePresetResponse


class StylePresetDeleteResponse(BaseModel):
    """스타일 프리셋 삭제 응답"""
    success: bool = True
    message: str = "스타일이 삭제되었습니다."


# 기본 제공 스타일 프리셋 (더 구체적인 프롬프트)
DEFAULT_STYLE_PRESETS = [
    {
        "name": "ghibli",
        "label": "Ghibli",
        "description": "지브리 스타일",
        "icon": "🏯",
        "prompt": "Transform this image into Studio Ghibli animation style. Apply soft, dreamy watercolor-like textures with warm, nostalgic color palette. Add gentle lighting with soft shadows, hand-painted background details, and characteristic Ghibli aesthetic with rounded, friendly character features and whimsical natural elements.",
        "negative_prompt": "harsh lighting, photorealistic, 3D render, sharp edges, dark colors, horror, grotesque, low quality, blurry",
        "is_builtin": True,
        "sort_order": 0,
    },
    {
        "name": "anime",
        "label": "Anime",
        "description": "애니메이션",
        "icon": "🎌",
        "prompt": "Convert this image to high-quality Japanese anime style. Apply clean, bold outlines with cel-shading technique. Use vibrant, saturated colors with anime-typical color grading. Add detailed eyes with highlights, smooth skin rendering, and dynamic lighting effects typical of modern anime productions.",
        "negative_prompt": "western cartoon, 3D, photorealistic, blurry, low quality, sketch, unfinished, watercolor",
        "is_builtin": True,
        "sort_order": 1,
    },
    {
        "name": "realistic",
        "label": "Realistic",
        "description": "사실적",
        "icon": "📷",
        "prompt": "Enhance this image to achieve photorealistic quality. Apply natural lighting with accurate shadows and highlights. Add realistic skin textures, detailed hair strands, and natural environmental elements. Ensure proper depth of field, accurate color reproduction, and professional photography-level quality.",
        "negative_prompt": "cartoon, anime, painting, illustration, drawing, artificial, plastic, oversaturated, unrealistic colors",
        "is_builtin": True,
        "sort_order": 2,
    },
    {
        "name": "oil_painting",
        "label": "Oil Paint",
        "description": "유화",
        "icon": "🎨",
        "prompt": "Transform this image into a classical oil painting masterpiece. Apply visible, textured brush strokes with impasto technique. Use rich, deep colors with Renaissance-era color palette. Add dramatic chiaroscuro lighting, canvas texture, and the characteristic glossy finish of traditional oil paintings.",
        "negative_prompt": "digital art, flat colors, smooth texture, photorealistic, cartoon, anime, watercolor, sketch",
        "is_builtin": True,
        "sort_order": 3,
    },
    {
        "name": "watercolor",
        "label": "Watercolor",
        "description": "수채화",
        "icon": "💧",
        "prompt": "Convert this image to delicate watercolor painting style. Apply soft, flowing color washes with transparent layering effects. Add gentle color bleeding at edges, visible paper texture, and subtle granulation. Create dreamy, ethereal atmosphere with pastel tones and soft transitions between colors.",
        "negative_prompt": "oil painting, digital art, sharp edges, bold colors, photorealistic, 3D, harsh lighting",
        "is_builtin": True,
        "sort_order": 4,
    },
    {
        "name": "sketch",
        "label": "Sketch",
        "description": "스케치",
        "icon": "✏️",
        "prompt": "Transform this image into a detailed pencil sketch drawing. Apply fine cross-hatching and shading techniques for depth. Use varying line weights for emphasis, detailed line work for textures, and subtle smudging effects. Create professional artist-quality sketch with careful attention to proportions and shadows.",
        "negative_prompt": "color, painting, photorealistic, 3D, cartoon, blurry, low detail, watercolor",
        "is_builtin": True,
        "sort_order": 5,
    },
    {
        "name": "cyberpunk",
        "label": "Cyberpunk",
        "description": "사이버펑크",
        "icon": "🤖",
        "prompt": "Transform this image into cyberpunk aesthetic. Apply neon color palette with dominant pink, cyan, and purple tones. Add futuristic elements like holographic overlays, digital glitches, and rain-slicked surfaces reflecting neon lights. Create dystopian urban atmosphere with high-tech, low-life visual elements.",
        "negative_prompt": "natural, pastoral, bright daylight, vintage, retro, watercolor, oil painting, warm colors",
        "is_builtin": True,
        "sort_order": 6,
    },
    {
        "name": "vintage",
        "label": "Vintage",
        "description": "빈티지",
        "icon": "📼",
        "prompt": "Apply vintage film photography aesthetic to this image. Add warm sepia-tinted color grading with faded blacks and lifted shadows. Include subtle film grain texture, light leaks, and vignetting effects. Create nostalgic 1970s-80s photograph look with slightly desaturated colors and soft focus edges.",
        "negative_prompt": "modern, digital, sharp, vibrant colors, high contrast, neon, futuristic, HDR",
        "is_builtin": True,
        "sort_order": 7,
    },
    {
        "name": "pixel_art",
        "label": "Pixel Art",
        "description": "픽셀 아트",
        "icon": "👾",
        "prompt": "Convert this image into retro pixel art style. Apply limited color palette with dithering technique. Create clear, blocky pixels with deliberate low resolution aesthetic. Add 8-bit or 16-bit video game inspired look with clean pixel edges and nostalgic gaming visual style.",
        "negative_prompt": "high resolution, smooth, photorealistic, blurry, 3D render, gradients, anti-aliasing",
        "is_builtin": True,
        "sort_order": 8,
    },
    {
        "name": "comic",
        "label": "Comic",
        "description": "만화/코믹",
        "icon": "💥",
        "prompt": "Transform this image into American comic book style. Apply bold black outlines with Ben-Day dots halftone shading. Use primary colors with flat shading technique. Add dramatic action lines, strong shadows, and superhero comic aesthetic with dynamic, punchy visual impact.",
        "negative_prompt": "anime, realistic, watercolor, soft, pastel, 3D, photographic, subtle",
        "is_builtin": True,
        "sort_order": 9,
    },
    {
        "name": "photo_restoration",
        "label": "Photo Restore",
        "description": "사진 복원",
        "icon": "🔧",
        "prompt": "Restore and enhance this old or damaged photograph to pristine condition. Remove scratches, dust spots, stains, creases, and tears. Fix faded colors and restore proper contrast and brightness. Sharpen blurry areas while preserving natural film grain. Repair missing or damaged portions seamlessly. Enhance facial details and skin tones naturally. Maintain the original era's photographic characteristics while dramatically improving overall quality.",
        "negative_prompt": "artificial looking, over-processed, plastic skin, unnatural colors, cartoon, anime, painting, artistic filter, HDR effect, oversaturated, blur, noise, artifacts",
        "is_builtin": True,
        "sort_order": 10,
    },
]
