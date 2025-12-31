"""
파일 유틸리티 모듈
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta

from config import get_settings


settings = get_settings()


def delete_file(filepath: str) -> bool:
    """
    파일 삭제
    
    Args:
        filepath: 파일 경로 (절대 또는 storage 기준 상대)
    
    Returns:
        bool: 삭제 성공 여부
    """
    path = Path(filepath)
    
    if not path.is_absolute():
        path = settings.storage_dir / filepath
    
    try:
        if path.exists():
            path.unlink()
            return True
    except Exception as e:
        print(f"Failed to delete file {path}: {e}")
    
    return False


def delete_files(filepaths: List[str]) -> int:
    """
    여러 파일 삭제
    
    Returns:
        int: 삭제된 파일 수
    """
    count = 0
    for filepath in filepaths:
        if delete_file(filepath):
            count += 1
    return count


def cleanup_old_files(
    directory: Path,
    days: int = 7,
    extensions: Optional[List[str]] = None,
) -> int:
    """
    오래된 파일 정리
    
    Args:
        directory: 대상 디렉토리
        days: 기준 일수
        extensions: 대상 확장자 (없으면 모든 파일)
    
    Returns:
        int: 삭제된 파일 수
    """
    if not directory.exists():
        return 0
    
    cutoff = datetime.now() - timedelta(days=days)
    count = 0
    
    for filepath in directory.iterdir():
        if filepath.is_file():
            # 확장자 필터
            if extensions:
                if filepath.suffix.lower() not in extensions:
                    continue
            
            # 수정 시간 확인
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
            if mtime < cutoff:
                try:
                    filepath.unlink()
                    count += 1
                except Exception as e:
                    print(f"Failed to delete {filepath}: {e}")
    
    return count


def cleanup_temp_files() -> int:
    """임시 파일 정리"""
    return cleanup_old_files(
        settings.temp_dir,
        days=1,
        extensions=[".png", ".jpg", ".jpeg", ".webp"]
    )


def cleanup_old_images(days: Optional[int] = None) -> dict:
    """
    오래된 이미지 정리
    
    Returns:
        dict: 디렉토리별 삭제 수
    """
    if days is None:
        # 설정에서 가져오기
        from core.settings_manager import SettingsManager
        manager = SettingsManager()
        days = manager.settings.gallery.auto_cleanup_days
    
    result = {
        "images": cleanup_old_files(settings.images_dir, days),
        "thumbnails": cleanup_old_files(settings.thumbnails_dir, days),
        "temp": cleanup_old_files(settings.temp_dir, days=1),
    }
    
    return result


def get_file_size(filepath: str) -> int:
    """파일 크기 반환 (bytes)"""
    path = Path(filepath)
    
    if not path.is_absolute():
        path = settings.storage_dir / filepath
    
    if path.exists():
        return path.stat().st_size
    
    return 0


def ensure_directory(directory: Path) -> None:
    """디렉토리 생성 확인"""
    directory.mkdir(parents=True, exist_ok=True)

