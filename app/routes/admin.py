from pydantic import BaseModel, EmailStr
from sanic import Blueprint, Request, json
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.dependencies.auth import get_current_user, require_admin
from app.models import User
from app.services.security import hash_password


admin_bp = Blueprint("admin", url_prefix="/admin")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    full_name: str | None = None

@admin_bp.get("/users")
async def list_users(request: Request):
    try:
        current_user = await get_current_user(request)
        await require_admin(current_user)
    except Exception as e:
        status = 403 if "Admin" in str(e) else 401
        return json({"error": str(e)}, status=status)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).options(selectinload(User.accounts))
        )
        users = result.scalars().unique().all()


    return json([
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "is_admin": u.is_admin,
            "accounts": [
                {"id": a.id, "balance": str(a.balance)}
                for a in u.accounts
            ]
        }
        for u in users
    ])

@admin_bp.post("/users")
async def create_user(request: Request):
    try:
        current_user = await get_current_user(request)
        await require_admin(current_user)
    except Exception as e:
        status = 403 if "Admin" in str(e) else 401
        return json({"error": f"{str(e)}"}, status=status)

    try:
        data = UserCreate(**request.json)
    except Exception as e:
        return json({"error": f"Validation error: {str(e)}"}, status=400)


    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            return json({"error": "Email already exists"}, status=409)

        new_user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            is_admin=False,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

    return json({
        "id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name
    }, status=201)

@admin_bp.put("/users/<user_id:int>")
async def update_user(request: Request, user_id: int):
    try:
        current_user = await get_current_user(request)
        await require_admin(current_user)
    except Exception as e:
        status = 403 if "Admin" in str(e) else 401
        return json({"error": f"{str(e)}"}, status=status)

    try:
        data = UserUpdate(**request.json)
    except Exception as e:
        return json({"error": f"Validation error: {str(e)}"}, status=400)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return json({"error": "User not found"}, status=404)
        
        if data.email is not None:
            user.email = data.email
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.password is not None:
            user.hashed_password = hash_password(data.password)
        
        await db.commit()
        await db.refresh(user)

    return json({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_admin": user.is_admin
    })

@admin_bp.delete("/users/<user_id:int>")
async def delete_user(request: Request, user_id: int):
    try:
        current_user = await get_current_user(request)
        await require_admin(current_user)
    except Exception as e:
        status = 403 if "Admin" in str(e) else 401
        return json({"error": str(e)}, status=status)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return json({"error": "User not found"}, status=404)

        await db.delete(user)
        await db.commit()


    return json({"message": "User deleted"})
