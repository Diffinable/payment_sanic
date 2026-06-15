from sanic import Blueprint, Request, json

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.services.payment import process_payment, verify_signature

webhook_bp = Blueprint("webhook", url_prefix="/webhook")
settings = get_settings()

@webhook_bp.post("/payment")
async def payment_webhook(request: Request):
    data = request.json
    if not data:
        return json({"error": "Empty body"}, status=400)

    if not verify_signature(data, settings.SECRET_KEY):
        return json({"error": "Invalid signature"}, status=400)

    try:
        async with AsyncSessionLocal() as db:
            result = await process_payment(db, data)
            return json(result, status=200)
    except ValueError as e:
        return json({"error": str(e)}, status=404)
    except Exception as e:
        return json({"Webhook error": "Internal server error"}, status=500)


