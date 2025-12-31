"""
SQLite + SQLAlchemy 비동기 데이터베이스 설정
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from config import get_settings


settings = get_settings()

# 비동기 엔진 생성
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 모델 베이스 클래스
Base = declarative_base()


async def init_db() -> None:
    """데이터베이스 초기화 (테이블 생성)"""
    # 모든 모델 임포트하여 메타데이터 등록
    from db import models  # noqa: F401
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """데이터베이스 연결 종료"""
    await engine.dispose()


async def get_db() -> AsyncSession:
    """
    데이터베이스 세션 의존성
    FastAPI Depends에서 사용
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

