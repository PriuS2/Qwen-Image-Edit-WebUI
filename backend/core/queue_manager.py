"""
작업 큐 관리자 모듈
- asyncio 기반 In-Memory Queue
- 작업 상태 관리
- WebSocket 진행률 브로드캐스트
"""

import asyncio
from typing import Optional, Dict, Any, Callable, Set
from datetime import datetime
from dataclasses import dataclass, field

from db.database import AsyncSessionLocal
from db import crud
from db.models import JobStatus, JobType


@dataclass
class QueueJob:
    """큐 작업 데이터"""
    job_id: str
    job_type: str
    input_data: dict
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class QueueManager:
    """작업 큐 관리자 싱글톤"""
    
    _instance: Optional["QueueManager"] = None
    _initialized: bool = False
    
    def __new__(cls) -> "QueueManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._queue: asyncio.Queue[QueueJob] = asyncio.Queue()
            self._running: bool = False
            self._current_job: Optional[str] = None
            self._progress_subscribers: Dict[str, Set[Callable]] = {}
            self._worker_task: Optional[asyncio.Task] = None
            QueueManager._initialized = True
    
    @property
    def is_running(self) -> bool:
        """워커 실행 중 여부"""
        return self._running
    
    @property
    def current_job_id(self) -> Optional[str]:
        """현재 처리 중인 작업 ID"""
        return self._current_job
    
    @property
    def queue_size(self) -> int:
        """큐 크기"""
        return self._queue.qsize()
    
    async def submit_job(
        self,
        job_type: str,
        input_data: dict,
        session_id: Optional[str] = None,
    ) -> str:
        """
        작업 제출
        
        Args:
            job_type: 작업 유형
            input_data: 입력 데이터
            session_id: 세션 ID
        
        Returns:
            str: 작업 ID
        """
        # DB에 작업 생성
        async with AsyncSessionLocal() as db:
            job = await crud.create_job(
                db=db,
                job_type=job_type,
                input_data=input_data,
                session_id=session_id,
            )
            job_id = job.id
            await db.commit()
        
        # 큐에 추가
        queue_job = QueueJob(
            job_id=job_id,
            job_type=job_type,
            input_data=input_data,
            session_id=session_id,
        )
        await self._queue.put(queue_job)
        
        print(f"📥 Job submitted: {job_id} ({job_type})")
        
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[dict]:
        """작업 상태 조회"""
        async with AsyncSessionLocal() as db:
            job = await crud.get_job_by_id(db, job_id)
            if job:
                return job.to_dict()
        return None
    
    async def cancel_job(self, job_id: str) -> bool:
        """작업 취소"""
        async with AsyncSessionLocal() as db:
            job = await crud.get_job_by_id(db, job_id)
            if job and job.status == JobStatus.PENDING:
                await crud.update_job_status(db, job_id, JobStatus.CANCELLED)
                await db.commit()
                return True
        return False
    
    async def start_worker(self) -> None:
        """워커 시작"""
        self._running = True
        
        while self._running:
            try:
                # 작업 대기 (타임아웃 1초)
                try:
                    queue_job = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # 취소된 작업 건너뛰기
                async with AsyncSessionLocal() as db:
                    job = await crud.get_job_by_id(db, queue_job.job_id)
                    if job and job.status == JobStatus.CANCELLED:
                        print(f"⏭️ Job skipped (cancelled): {queue_job.job_id}")
                        continue
                
                self._current_job = queue_job.job_id
                
                print(f"🔄 Processing job: {queue_job.job_id}")
                
                # 작업 처리
                await self._process_job(queue_job)
                
                self._current_job = None
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Worker error: {e}")
                if self._current_job:
                    await self._update_job_error(self._current_job, str(e))
                self._current_job = None
    
    async def stop_worker(self) -> None:
        """워커 중지"""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
    
    async def _process_job(self, queue_job: QueueJob) -> None:
        """작업 처리"""
        job_id = queue_job.job_id
        
        # 상태 업데이트: 처리 중
        async with AsyncSessionLocal() as db:
            await crud.update_job_status(db, job_id, JobStatus.PROCESSING, progress=0)
            await db.commit()
        
        await self._broadcast_progress(job_id, 0)
        
        try:
            # 작업 유형에 따라 처리
            if queue_job.job_type == JobType.SINGLE:
                result = await self._process_single_edit(job_id, queue_job.input_data)
            elif queue_job.job_type == JobType.MULTI:
                result = await self._process_multi_edit(job_id, queue_job.input_data)
            elif queue_job.job_type == JobType.STYLE_TRANSFER:
                result = await self._process_style_transfer(job_id, queue_job.input_data)
            elif queue_job.job_type == JobType.BATCH:
                result = await self._process_batch(job_id, queue_job.input_data)
            else:
                raise ValueError(f"Unknown job type: {queue_job.job_type}")
            
            # 완료 상태 업데이트
            async with AsyncSessionLocal() as db:
                await crud.update_job_status(
                    db, job_id, JobStatus.COMPLETED,
                    progress=100,
                    output_data=result,
                )
                await db.commit()
            
            await self._broadcast_progress(job_id, 100, result=result)
            
            print(f"✅ Job completed: {job_id}")
            
        except Exception as e:
            await self._update_job_error(job_id, str(e))
            print(f"❌ Job failed: {job_id} - {e}")
    
    async def _process_single_edit(self, job_id: str, input_data: dict) -> dict:
        """단일 이미지 편집 처리"""
        from core.image_editor import get_image_editor
        from schemas.edit import EditParams
        
        editor = get_image_editor()
        
        params = EditParams(**input_data.get("params", {}))
        
        # 진행률 콜백 (비동기 함수 직접 전달)
        async def progress_callback(p: int):
            await self._broadcast_progress(job_id, p)
        
        result = await editor.edit_single(
            image_source=input_data["image"],
            params=params,
            response_format=input_data.get("response_format", "url"),
            session_id=input_data.get("session_id"),
            save_to_gallery=input_data.get("save_to_gallery", True),
            progress_callback=progress_callback,
        )
        
        return result.model_dump()
    
    async def _process_multi_edit(self, job_id: str, input_data: dict) -> dict:
        """다중 이미지 편집 처리"""
        from core.image_editor import get_image_editor
        from schemas.edit import EditParams
        
        editor = get_image_editor()
        
        params = EditParams(**input_data.get("params", {}))
        
        # 진행률 콜백 (비동기 함수 직접 전달)
        async def progress_callback(p: int):
            await self._broadcast_progress(job_id, p)
        
        result = await editor.edit_multi(
            image_sources=input_data["images"],
            params=params,
            response_format=input_data.get("response_format", "url"),
            session_id=input_data.get("session_id"),
            save_to_gallery=input_data.get("save_to_gallery", True),
            progress_callback=progress_callback,
        )
        
        return result.model_dump()
    
    async def _process_style_transfer(self, job_id: str, input_data: dict) -> dict:
        """스타일 변환 처리"""
        from core.image_editor import get_image_editor
        
        editor = get_image_editor()
        
        # 진행률 콜백 (비동기 함수 직접 전달)
        async def progress_callback(p: int):
            await self._broadcast_progress(job_id, p)
        
        result = await editor.style_transfer(
            image_source=input_data["image"],
            style=input_data["style"],
            intensity=input_data.get("intensity", 1.0),
            additional_prompt=input_data.get("additional_prompt"),
            response_format=input_data.get("response_format", "url"),
            session_id=input_data.get("session_id"),
            save_to_gallery=input_data.get("save_to_gallery", True),
            progress_callback=progress_callback,
        )
        
        return result.model_dump()
    
    async def _process_batch(self, job_id: str, input_data: dict) -> dict:
        """배치 처리"""
        from core.image_editor import get_image_editor
        from schemas.edit import EditParams
        
        editor = get_image_editor()
        items = input_data.get("items", [])
        results = []
        
        for i, item in enumerate(items):
            progress = int((i / len(items)) * 90)
            await self._broadcast_progress(job_id, progress)
            
            params = EditParams(**item.get("params", {}))
            
            result = await editor.edit_single(
                image_source=item["image"],
                params=params,
                response_format=input_data.get("response_format", "url"),
                session_id=input_data.get("session_id"),
                save_to_gallery=input_data.get("save_to_gallery", True),
            )
            
            results.append(result.model_dump())
        
        return {"results": results, "total": len(results)}
    
    async def _update_job_error(self, job_id: str, error: str) -> None:
        """작업 오류 상태 업데이트"""
        async with AsyncSessionLocal() as db:
            await crud.update_job_status(
                db, job_id, JobStatus.FAILED,
                error_message=error,
            )
            await db.commit()
        
        await self._broadcast_progress(job_id, -1, error=error)
    
    # ═══════════════════════════════════════════════════════════════
    # 진행률 브로드캐스트
    # ═══════════════════════════════════════════════════════════════
    
    def subscribe_progress(self, job_id: str, callback: Callable) -> None:
        """진행률 구독"""
        if job_id not in self._progress_subscribers:
            self._progress_subscribers[job_id] = set()
        self._progress_subscribers[job_id].add(callback)
    
    def unsubscribe_progress(self, job_id: str, callback: Callable) -> None:
        """진행률 구독 해제"""
        if job_id in self._progress_subscribers:
            self._progress_subscribers[job_id].discard(callback)
            if not self._progress_subscribers[job_id]:
                del self._progress_subscribers[job_id]
    
    async def _broadcast_progress(
        self,
        job_id: str,
        progress: int,
        result: Optional[dict] = None,
        error: Optional[str] = None,
    ) -> None:
        """진행률 브로드캐스트"""
        if job_id not in self._progress_subscribers:
            return
        
        message = {
            "job_id": job_id,
            "progress": progress,
            "result": result,
            "error": error,
        }
        
        for callback in self._progress_subscribers[job_id].copy():
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                print(f"Progress callback error: {e}")


# 싱글톤
_queue_manager: Optional[QueueManager] = None


def get_queue_manager() -> QueueManager:
    """큐 관리자 인스턴스 반환"""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = QueueManager()
    return _queue_manager

