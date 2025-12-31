"""
인증 관련 스키마
"""

from pydantic import BaseModel


class AuthVerifyResponse(BaseModel):
    """인증 검증 응답"""
    success: bool = True
    message: str = "API Key is valid"

