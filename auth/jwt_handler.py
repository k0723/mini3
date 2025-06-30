from time import time
from fastapi import HTTPException, status
from jose import jwt
from database.connection import Settings


settings = Settings()


# JWT 토큰 생성
def create_jwt_token(email: str, user_id: int, role: str) -> str:
    now = int(time())  # 현재 시간을 정수형으로 변환
    payload = {
        "user": email,
        "user_id": user_id,
        "role": role,
        "iat": now,           # ✅ int
        "exp": now + 3600     # ✅ int
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


# JWT 토큰 검증
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp = payload.get("exp")
        if exp is None: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
        if time() > exp:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token expired")
        return payload
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")