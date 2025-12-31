"""
WebSocket 진행률 핸들러
"""

import asyncio
import json
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from core.queue_manager import get_queue_manager


router = APIRouter()


class ConnectionManager:
    """WebSocket 연결 관리자"""
    
    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, job_id: str) -> None:
        """연결 수락"""
        await websocket.accept()
        
        if job_id not in self._connections:
            self._connections[job_id] = set()
        self._connections[job_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, job_id: str) -> None:
        """연결 해제"""
        if job_id in self._connections:
            self._connections[job_id].discard(websocket)
            if not self._connections[job_id]:
                del self._connections[job_id]
    
    async def send_message(self, job_id: str, message: dict) -> None:
        """특정 작업 구독자에게 메시지 전송"""
        if job_id not in self._connections:
            return
        
        dead_connections = set()
        
        for websocket in self._connections[job_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                dead_connections.add(websocket)
        
        # 죽은 연결 정리
        for websocket in dead_connections:
            self._connections[job_id].discard(websocket)


manager = ConnectionManager()


@router.websocket("/progress/{job_id}")
async def websocket_progress(
    websocket: WebSocket,
    job_id: str,
):
    """
    작업 진행률 WebSocket
    
    연결 후 작업 진행률을 실시간으로 수신합니다.
    
    메시지 형식:
    {
        "job_id": "xxx",
        "progress": 0-100,
        "result": {...}  // 완료 시
        "error": "..."   // 실패 시
    }
    """
    await manager.connect(websocket, job_id)
    
    queue_manager = get_queue_manager()
    
    # 진행률 콜백 등록
    async def progress_callback(message: dict):
        await manager.send_message(job_id, message)
    
    queue_manager.subscribe_progress(job_id, progress_callback)
    
    try:
        # 현재 상태 전송
        status = await queue_manager.get_job_status(job_id)
        if status:
            await websocket.send_json({
                "job_id": job_id,
                "progress": status.get("progress", 0),
                "status": status.get("status"),
                "result": status.get("output_data"),
                "error": status.get("error_message"),
            })
        
        # 연결 유지 (클라이언트가 끊을 때까지)
        while True:
            try:
                # ping/pong 또는 클라이언트 메시지 대기
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                # 클라이언트가 "ping" 보내면 "pong" 응답
                if data == "ping":
                    await websocket.send_text("pong")
                
            except asyncio.TimeoutError:
                # 타임아웃 시 ping 전송하여 연결 확인
                try:
                    await websocket.send_text("ping")
                except Exception:
                    break
    
    except WebSocketDisconnect:
        pass
    
    finally:
        queue_manager.unsubscribe_progress(job_id, progress_callback)
        manager.disconnect(websocket, job_id)

