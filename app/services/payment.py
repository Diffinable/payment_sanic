

from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib

from app.models import Account, Payment, User


def verify_signature(data, secret_key):
    payload = {
        "transaction_id": data.get("transaction_id"),
        "account_id": data.get("account_id"),
        "user_id": data.get("user_id"),
        "amount": data.get("amount")
    }

    sorted_keys = sorted(payload.keys())

    concat_str = "".join(str(payload[k]) for k in sorted_keys) + secret_key

    expected_sig = hashlib.sha256(concat_str.encode("utf-8")).hexdigest()

    return expected_sig == data.get("signature")

async def process_payment(db: AsyncSession, data: dict):
    transaction_id = str(data["transaction_id"])
    user_id = int(data["user_id"])
    account_id = int(data["account_id"])
    amount = Decimal(str(data["amount"]))

    result = await db.execute(select(Payment).where(Payment.transaction_id == transaction_id))
    if result.scalar_one_or_none():
        return {"status": "already processed"}
    
    result = await db.execute(select(Account).where(Account.id == account_id, Account.user_id == user_id))
    account = result.scalar_one_or_none()

    if not account:
        user_res = await db.execute(select(User).where(User.id == user_id))
        if not user_res.scalar_one_or_none():
            ValueError("User not found")

        account = Account(id=account_id,user_id=user_id,balance=Decimal("0.00"))
        db.add(account)
        await db.flush()

    account.balance += amount

    payment = Payment(
        transaction_id=transaction_id,
        account_id=account.id,
        amount=amount
    )

    db.add(payment)
    await db.commit()
    return {"status": "success", "new_balance": str(account.balance)}
    