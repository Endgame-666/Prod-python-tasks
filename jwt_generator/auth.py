from datetime import datetime, timedelta
from typing import Literal
from fastapi import APIRouter, HTTPException
import jwt
from pydantic import BaseModel
from config import settings

router = APIRouter()

class TokenRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["Bearer"]


@router.post("/auth/token", response_model=TokenResponse)
async def create_token(request: TokenRequest):
    if request.password != "secret123":
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    expiration = datetime.now() + timedelta(seconds=15)
    token_data = {
        "sub": request.username,
        "exp": expiration,
        "iat": datetime.now()
    }
    token = jwt.encode(
        token_data,
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    return TokenResponse(
        access_token=token,
        token_type="Bearer"
    )
