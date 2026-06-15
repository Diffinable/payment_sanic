from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sanic import Blueprint
from sanic.response import json
from sanic_ext import openapi
from app.database import AsyncSessionLocal
from app.models import User
from app.services.security import create_access_token, verify_password


auth_bp = Blueprint("auth", url_prefix="/auth")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@auth_bp.post("/login")
@openapi.definition(
    summary="Авторизация пользователя",
    body={"application/json": LoginRequest}
)
async def login(request):
    try:
        data = LoginRequest(**request.json)
    except Exception as e:
        return json({"error": f"Validation error: {str(e)}"}, status=400)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            return json({"error": "Invalid credentials"}, status=401)

        token = create_access_token(data={"sub": str(user.id)})

    return json({
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "is_admin": user.is_admin
    })