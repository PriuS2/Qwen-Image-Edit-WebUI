"""
API 의존성 모듈
- API Key 인증
- 공통 의존성
"""

from typing import Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from config import get_settings


settings = get_settings()

# API Key Header Security Scheme
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="API Key for authentication"
)


async def verify_api_key(
    api_key: Optional[str] = Security(api_key_header),
) -> str:
    """
    API Key 검증
    
    헤더에서 API Key 확인:
    - X-API-Key 헤더
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required. Use X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )
    
    return api_key


async def optional_api_key(
    api_key: Optional[str] = Security(api_key_header),
) -> Optional[str]:
    """선택적 API Key (없어도 OK)"""
    return api_key

