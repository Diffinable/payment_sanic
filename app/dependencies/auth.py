from sqlalchemy import select
from app.models import User
from app.services.security import decode_access_token


async def get_current_user(request):
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise Exception("Missing or invalid authorization header")

    token = auth_header.split()[1]

    payload = decode_access_token(token)
    if payload is None:
        raise Exception("Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise Exception("Invalid token payload")

    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

    if user is None:
        raise Exception("User not found")

    return user

async def require_admin(current_user):
    if not current_user or not current_user.is_admin:
        raise Exception("Admin access required")
    return current_user


    