"""
CRUD 작업 모듈
데이터베이스 조작 함수들
"""

from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import select, update, delete, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import History, Gallery, Job, Setting, JobStatus, StylePreset


# ═══════════════════════════════════════════════════════════════
# History CRUD
# ═══════════════════════════════════════════════════════════════

async def create_history(
    db: AsyncSession,
    session_id: str,
    original_image_path: str,
    prompt: str,
    edited_image_path: Optional[str] = None,
    parameters: Optional[dict] = None,
    parent_id: Optional[str] = None,
    position: int = 0,
) -> History:
    """히스토리 생성"""
    history = History(
        session_id=session_id,
        original_image_path=original_image_path,
        edited_image_path=edited_image_path,
        prompt=prompt,
        parameters=parameters,
        parent_id=parent_id,
        position=position,
    )
    db.add(history)
    await db.flush()
    await db.refresh(history)
    return history


async def get_history_by_id(db: AsyncSession, history_id: str) -> Optional[History]:
    """ID로 히스토리 조회"""
    result = await db.execute(select(History).where(History.id == history_id))
    return result.scalar_one_or_none()


async def get_history_by_session(
    db: AsyncSession,
    session_id: str,
    limit: int = 50,
    offset: int = 0,
) -> List[History]:
    """세션별 히스토리 목록 조회"""
    result = await db.execute(
        select(History)
        .where(History.session_id == session_id)
        .order_by(desc(History.created_at))
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def delete_history(db: AsyncSession, history_id: str) -> bool:
    """히스토리 삭제"""
    result = await db.execute(delete(History).where(History.id == history_id))
    return result.rowcount > 0


# ═══════════════════════════════════════════════════════════════
# Gallery CRUD
# ═══════════════════════════════════════════════════════════════

async def create_gallery(
    db: AsyncSession,
    image_path: str,
    thumbnail_path: Optional[str] = None,
    original_image_path: Optional[str] = None,
    history_id: Optional[str] = None,
    image_metadata: Optional[dict] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Gallery:
    """갤러리 아이템 생성"""
    gallery = Gallery(
        image_path=image_path,
        thumbnail_path=thumbnail_path,
        original_image_path=original_image_path,
        history_id=history_id,
        image_metadata=image_metadata,
        title=title,
        description=description,
    )
    db.add(gallery)
    await db.flush()
    await db.refresh(gallery)
    return gallery


async def get_gallery_by_id(db: AsyncSession, gallery_id: str) -> Optional[Gallery]:
    """ID로 갤러리 아이템 조회"""
    result = await db.execute(select(Gallery).where(Gallery.id == gallery_id))
    return result.scalar_one_or_none()


async def get_gallery_list(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    favorites_only: bool = False,
) -> List[Gallery]:
    """갤러리 목록 조회"""
    query = select(Gallery)
    if favorites_only:
        query = query.where(Gallery.is_favorite == True)
    query = query.order_by(desc(Gallery.created_at)).limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_gallery(
    db: AsyncSession,
    gallery_id: str,
    **kwargs,
) -> Optional[Gallery]:
    """갤러리 아이템 업데이트"""
    await db.execute(
        update(Gallery).where(Gallery.id == gallery_id).values(**kwargs)
    )
    return await get_gallery_by_id(db, gallery_id)


async def delete_gallery(db: AsyncSession, gallery_id: str) -> bool:
    """갤러리 아이템 삭제"""
    result = await db.execute(delete(Gallery).where(Gallery.id == gallery_id))
    return result.rowcount > 0


# ═══════════════════════════════════════════════════════════════
# Job CRUD
# ═══════════════════════════════════════════════════════════════

async def create_job(
    db: AsyncSession,
    job_type: str,
    input_data: Optional[dict] = None,
    session_id: Optional[str] = None,
) -> Job:
    """작업 생성"""
    job = Job(
        type=job_type,
        input_data=input_data,
        session_id=session_id,
        status=JobStatus.PENDING,
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    return job


async def get_job_by_id(db: AsyncSession, job_id: str) -> Optional[Job]:
    """ID로 작업 조회"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def get_pending_jobs(db: AsyncSession, limit: int = 10) -> List[Job]:
    """대기 중인 작업 목록 조회"""
    result = await db.execute(
        select(Job)
        .where(Job.status == JobStatus.PENDING)
        .order_by(Job.created_at)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_jobs_by_session(
    db: AsyncSession,
    session_id: str,
    limit: int = 50,
) -> List[Job]:
    """세션별 작업 목록 조회"""
    result = await db.execute(
        select(Job)
        .where(Job.session_id == session_id)
        .order_by(desc(Job.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_job(
    db: AsyncSession,
    job_id: str,
    **kwargs,
) -> Optional[Job]:
    """작업 업데이트"""
    await db.execute(
        update(Job).where(Job.id == job_id).values(**kwargs)
    )
    await db.commit()
    return await get_job_by_id(db, job_id)


async def update_job_status(
    db: AsyncSession,
    job_id: str,
    status: str,
    progress: Optional[int] = None,
    error_message: Optional[str] = None,
    output_data: Optional[dict] = None,
) -> Optional[Job]:
    """작업 상태 업데이트"""
    values = {"status": status}
    
    if progress is not None:
        values["progress"] = progress
    
    if error_message is not None:
        values["error_message"] = error_message
    
    if output_data is not None:
        values["output_data"] = output_data
    
    if status == JobStatus.PROCESSING:
        values["started_at"] = datetime.utcnow()
    elif status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
        values["completed_at"] = datetime.utcnow()
    
    return await update_job(db, job_id, **values)


async def delete_job(db: AsyncSession, job_id: str) -> bool:
    """작업 삭제"""
    result = await db.execute(delete(Job).where(Job.id == job_id))
    return result.rowcount > 0


# ═══════════════════════════════════════════════════════════════
# Settings CRUD
# ═══════════════════════════════════════════════════════════════

async def get_setting(db: AsyncSession, key: str) -> Optional[Any]:
    """설정 값 조회"""
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    return setting.value if setting else None


async def set_setting(db: AsyncSession, key: str, value: Any) -> Setting:
    """설정 값 저장 (upsert)"""
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = value
        setting.updated_at = datetime.utcnow()
    else:
        setting = Setting(key=key, value=value)
        db.add(setting)
    
    await db.flush()
    await db.refresh(setting)
    return setting


async def get_all_settings(db: AsyncSession) -> dict:
    """모든 설정 조회"""
    result = await db.execute(select(Setting))
    settings = result.scalars().all()
    return {s.key: s.value for s in settings}


async def delete_setting(db: AsyncSession, key: str) -> bool:
    """설정 삭제"""
    result = await db.execute(delete(Setting).where(Setting.key == key))
    return result.rowcount > 0


async def delete_all_settings(db: AsyncSession) -> int:
    """모든 설정 삭제"""
    result = await db.execute(delete(Setting))
    return result.rowcount


# ═══════════════════════════════════════════════════════════════
# StylePreset CRUD
# ═══════════════════════════════════════════════════════════════

async def create_style_preset(
    db: AsyncSession,
    name: str,
    label: str,
    prompt: str,
    description: Optional[str] = None,
    icon: str = "🎨",
    negative_prompt: str = "",
    is_builtin: bool = False,
    is_enabled: bool = True,
    sort_order: int = 0,
) -> StylePreset:
    """스타일 프리셋 생성"""
    preset = StylePreset(
        name=name,
        label=label,
        description=description,
        icon=icon,
        prompt=prompt,
        negative_prompt=negative_prompt,
        is_builtin=is_builtin,
        is_enabled=is_enabled,
        sort_order=sort_order,
    )
    db.add(preset)
    await db.flush()
    await db.refresh(preset)
    return preset


async def get_style_preset_by_id(db: AsyncSession, preset_id: str) -> Optional[StylePreset]:
    """ID로 스타일 프리셋 조회"""
    result = await db.execute(select(StylePreset).where(StylePreset.id == preset_id))
    return result.scalar_one_or_none()


async def get_style_preset_by_name(db: AsyncSession, name: str) -> Optional[StylePreset]:
    """이름으로 스타일 프리셋 조회"""
    result = await db.execute(select(StylePreset).where(StylePreset.name == name))
    return result.scalar_one_or_none()


async def get_all_style_presets(
    db: AsyncSession,
    enabled_only: bool = False,
) -> List[StylePreset]:
    """모든 스타일 프리셋 조회"""
    query = select(StylePreset)
    if enabled_only:
        query = query.where(StylePreset.is_enabled == True)
    query = query.order_by(StylePreset.sort_order, StylePreset.created_at)
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_style_preset(
    db: AsyncSession,
    preset_id: str,
    **kwargs,
) -> Optional[StylePreset]:
    """스타일 프리셋 업데이트"""
    # None 값 필터링
    update_values = {k: v for k, v in kwargs.items() if v is not None}
    if not update_values:
        return await get_style_preset_by_id(db, preset_id)
    
    await db.execute(
        update(StylePreset).where(StylePreset.id == preset_id).values(**update_values)
    )
    await db.commit()
    return await get_style_preset_by_id(db, preset_id)


async def delete_style_preset(db: AsyncSession, preset_id: str) -> bool:
    """스타일 프리셋 삭제"""
    result = await db.execute(delete(StylePreset).where(StylePreset.id == preset_id))
    await db.commit()
    return result.rowcount > 0


async def delete_non_builtin_style_presets(db: AsyncSession) -> int:
    """사용자 정의 스타일 프리셋 모두 삭제"""
    result = await db.execute(
        delete(StylePreset).where(StylePreset.is_builtin == False)
    )
    return result.rowcount


async def style_preset_exists(db: AsyncSession, name: str) -> bool:
    """스타일 프리셋 이름 존재 여부 확인"""
    result = await db.execute(
        select(StylePreset.id).where(StylePreset.name == name)
    )
    return result.scalar_one_or_none() is not None


async def get_style_presets_count(db: AsyncSession) -> int:
    """스타일 프리셋 총 개수"""
    from sqlalchemy import func
    result = await db.execute(select(func.count(StylePreset.id)))
    return result.scalar() or 0

