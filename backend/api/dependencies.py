"""
API 의존성 모듈
- API Key 인증
- 공통 의존성
"""

from typing import Optional
from fastapi import Depends, HTTPException, Header, status

from config import get_settings


settings = get_settings()


async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
) -> str:
    """
    API Key 검증
    
    헤더에서 API Key 확인:
    - X-API-Key 헤더
    - Authorization: Bearer <key> 형식
    """
    api_key = None
    
    # X-API-Key 헤더 확인
    if x_api_key:
        api_key = x_api_key
    
    # Authorization 헤더 확인 (Bearer 토큰 형식)
    elif authorization:
        if authorization.startswith("Bearer "):
            api_key = authorization[7:]
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )
    
    return api_key


async def optional_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None),
) -> Optional[str]:
    """선택적 API Key (없어도 OK)"""
    api_key = None
    
    if x_api_key:
        api_key = x_api_key
    elif authorization and authorization.startswith("Bearer "):
        api_key = authorization[7:]
    
    return api_key

