from sanic import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models import User
from app.services.security import decode_access_token
from app.database import AsyncSessionLocal

class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code

class InvalidTokenError(AuthError):
    pass

class ExpiredTokenError(AuthError):
    pass

class AdminRequiredError(AuthError):
    def __init__(self):
        super().__init__("Admin access required", status_code=403)

def _parce_bearer_token(request: Request) -> str:
    auth_header = request.headers.get("authorization", "")
    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        raise InvalidTokenError("Invalid authorization header format")
    
    return parts[1]


async def get_current_user(request: Request, db: AsyncSession) -> User:
    if hasattr(request.ctx, "current_user"):
        return request.ctx.current_user

    token = _parce_bearer_token(request)

    payload = decode_access_token(token)
    if payload is None:
        raise ExpiredTokenError("Token expired or invalid")

    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidTokenError("Invalid token payload")

    result = await db.execute(
        select(User)
        .options(selectinload(User.accounts))
        .where(User.id == int(user_id), User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise Exception("User not found")

    return user

async def require_admin(current_user):
    if not current_user or not current_user.is_admin:
        raise Exception("Admin access required")
    return current_user
