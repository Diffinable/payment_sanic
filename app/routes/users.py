from sanic import Blueprint, Request, json
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.dependencies.auth import get_current_user
from app.models import Account, Payment


users_bp = Blueprint("users", url_prefix="/users")

@users_bp.get("/me")
async def get_my_profile(request: Request):
    try:
        current_user = await get_current_user(request)
    except Exception as e:
        return json({"error": str(e)}, status=401)

    return json({
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name
    })

@users_bp.get("/me/accounts")
async def get_my_accounts(request: Request):
    try:
        current_user = await get_current_user(request)
    except Exception as e:
        return json({"error": str(e)}, status=401)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Account).where(Account.user_id == current_user.id)
        )
        accounts = result.scalars().all()

    return json([
        {"id": acc.id, "balance": str(acc.balance)}
        for acc in accounts
    ])

@users_bp.get("/me/payments")
async def get_my_payments(request: Request):
    try:
        current_user = await get_current_user(request)
    except Exception as e:
        return json({"error": str(e)}, status=401)
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Payment)
            .join(Account, Payment.account_id == Account.id)
            .where(Account.user_id == current_user.id)
            .order_by(Payment.created_at.desc())
        )
        payments = result.scalars().all()

    return json([
        {
            "transaction_id": p.transaction_id,
            "account_id": p.account_id,
            "amount": str(p.amount),
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in payments
    ])
