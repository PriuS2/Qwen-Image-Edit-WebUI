"""
최적화 옵션 관리 모듈
"""

from typing import Optional, Any
from dataclasses import dataclass

from schemas.settings import OptimizationSettings


@dataclass
class OptimizationResult:
    """최적화 적용 결과"""
    success: bool
    applied: list[str]
    failed: list[str]
    messages: list[str]


def apply_optimizations(
    pipeline: Any,
    settings: OptimizationSettings,
) -> OptimizationResult:
    """
    파이프라인에 최적화 옵션 적용
    
    Args:
        pipeline: diffusers 파이프라인 객체
        settings: 최적화 설정
    
    Returns:
        OptimizationResult: 적용 결과
    """
    applied = []
    failed = []
    messages = []
    
    # CPU Offload
    if settings.enable_model_cpu_offload:
        try:
            pipeline.enable_model_cpu_offload()
            applied.append("model_cpu_offload")
            messages.append("✅ CPU Offload enabled")
        except Exception as e:
            failed.append("model_cpu_offload")
            messages.append(f"⚠️ CPU Offload failed: {e}")
    
    # Attention Slicing
    if settings.enable_attention_slicing:
        try:
            pipeline.enable_attention_slicing("auto")
            applied.append("attention_slicing")
            messages.append("✅ Attention Slicing enabled")
        except Exception as e:
            failed.append("attention_slicing")
            messages.append(f"⚠️ Attention Slicing failed: {e}")
    
    # VAE Slicing
    if settings.enable_vae_slicing:
        try:
            pipeline.enable_vae_slicing()
            applied.append("vae_slicing")
            messages.append("✅ VAE Slicing enabled")
        except Exception as e:
            failed.append("vae_slicing")
            messages.append(f"⚠️ VAE Slicing failed: {e}")
    
    # VAE Tiling
    if settings.enable_vae_tiling:
        try:
            pipeline.enable_vae_tiling()
            applied.append("vae_tiling")
            messages.append("✅ VAE Tiling enabled")
        except Exception as e:
            failed.append("vae_tiling")
            messages.append(f"⚠️ VAE Tiling failed: {e}")
    
    # xFormers
    if settings.enable_xformers:
        try:
            pipeline.enable_xformers_memory_efficient_attention()
            applied.append("xformers")
            messages.append("✅ xFormers enabled")
        except Exception as e:
            failed.append("xformers")
            messages.append(f"⚠️ xFormers not available: {e}")
    
    return OptimizationResult(
        success=len(failed) == 0,
        applied=applied,
        failed=failed,
        messages=messages,
    )


def get_torch_dtype(dtype_str: str):
    """문자열에서 torch dtype 반환"""
    import torch
    
    dtype_map = {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    
    return dtype_map.get(dtype_str, torch.bfloat16)

