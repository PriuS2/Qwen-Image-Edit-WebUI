"""
인증 API 라우터
"""

from fastapi import APIRouter, Depends

from api.dependencies import verify_api_key
from schemas.auth import AuthVerifyResponse


router = APIRouter()


@router.get("/verify", response_model=AuthVerifyResponse)
async def verify_auth(api_key: str = Depends(verify_api_key)):
    """
    API Key 검증
    
    헤더에 X-API-Key 또는 Authorization: Bearer <key> 필요
    """
    return AuthVerifyResponse(
        success=True,
        message="API Key is valid"
    )

