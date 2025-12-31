"""
Qwen Image Edit API - FastAPI 메인 진입점
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import get_settings
from db.database import init_db, close_db
from core.settings_manager import get_settings_manager
from core.model_manager import get_model_manager
from core.queue_manager import get_queue_manager
from api.routes import auth, model, edit, batch, history, gallery, styles
from api.routes import settings as settings_routes
from api.websocket import router as websocket_router


app_settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    애플리케이션 생명주기 관리
    - 시작: DB 초기화, 설정 로드, 큐 워커 시작
    - 종료: 모델 언로드, DB 연결 종료
    """
    # ═══════════════════════════════════════════════════════════════
    # 시작 시 초기화
    # ═══════════════════════════════════════════════════════════════
    print(f"🚀 Starting {app_settings.app_name} v{app_settings.app_version}")
    
    # 디렉토리 생성
    app_settings.ensure_directories()
    
    # 데이터베이스 초기화
    await init_db()
    print("✅ Database initialized")
    
    # 설정 관리자 초기화
    settings_manager = await get_settings_manager()
    await settings_manager.initialize()
    print("✅ Settings manager initialized")
    
    # 큐 매니저 시작
    queue_manager = get_queue_manager()
    asyncio.create_task(queue_manager.start_worker())
    print("✅ Queue worker started")
    
    # 자동 언로드 타이머 시작
    asyncio.create_task(settings_manager.start_auto_unload_timer())
    print("✅ Auto-unload timer started")
    
    # 기본 스타일 프리셋 초기화
    await styles.initialize_default_styles()
    print("✅ Style presets initialized")
    
    print(f"🌐 Server running at http://{app_settings.host}:{app_settings.port}")
    print(f"📚 API docs at http://{app_settings.host}:{app_settings.port}/docs")
    
    yield
    
    # ═══════════════════════════════════════════════════════════════
    # 종료 시 정리
    # ═══════════════════════════════════════════════════════════════
    print("🛑 Shutting down...")
    
    # 큐 매니저 중지
    queue_manager = get_queue_manager()
    await queue_manager.stop_worker()
    print("✅ Queue worker stopped")
    
    # 모델 언로드
    model_manager = get_model_manager()
    await model_manager.unload_model()
    print("✅ Model unloaded")
    
    # 데이터베이스 연결 종료
    await close_db()
    print("✅ Database connection closed")
    
    print("👋 Goodbye!")


# ═══════════════════════════════════════════════════════════════
# FastAPI 앱 생성
# ═══════════════════════════════════════════════════════════════
app = FastAPI(
    title=app_settings.app_name,
    version=app_settings.app_version,
    description="Qwen-Image-Edit-2511 기반 이미지 편집 API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ═══════════════════════════════════════════════════════════════
# CORS 미들웨어
# ═══════════════════════════════════════════════════════════════
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════
# 정적 파일 서빙 (이미지)
# ═══════════════════════════════════════════════════════════════
app.mount(
    "/storage",
    StaticFiles(directory=str(app_settings.storage_dir)),
    name="storage"
)

# ═══════════════════════════════════════════════════════════════
# API 라우터 등록
# ═══════════════════════════════════════════════════════════════
app.include_router(auth.router, prefix="/api/auth", tags=["인증"])
app.include_router(model.router, prefix="/api/model", tags=["모델 관리"])
app.include_router(edit.router, prefix="/api/edit", tags=["이미지 편집"])
app.include_router(batch.router, prefix="/api/batch", tags=["배치 처리"])
app.include_router(history.router, prefix="/api/history", tags=["히스토리"])
app.include_router(gallery.router, prefix="/api/gallery", tags=["갤러리"])
app.include_router(settings_routes.router, prefix="/api/settings", tags=["Settings"])
app.include_router(styles.router, prefix="/api/styles", tags=["스타일 프리셋"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])


# ═══════════════════════════════════════════════════════════════
# 헬스 체크 엔드포인트
# ═══════════════════════════════════════════════════════════════
@app.get("/", tags=["헬스 체크"])
async def root():
    """API 루트 - 헬스 체크"""
    return {
        "name": app_settings.app_name,
        "version": app_settings.app_version,
        "status": "running"
    }


@app.get("/health", tags=["헬스 체크"])
async def health_check():
    """상세 헬스 체크"""
    model_manager = get_model_manager()
    
    return {
        "status": "healthy",
        "model_loaded": model_manager.is_loaded,
        "version": app_settings.app_version
    }


# ═══════════════════════════════════════════════════════════════
# 메인 실행
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=app_settings.debug
    )

