from sanic import Sanic
from sanic_ext import Extend
from sanic.response import json
from app.config import get_settings
from app.routes.auth import auth_bp
from app.routes.webhook import webhook_bp
from app.routes.users import users_bp
from app.routes.admin import admin_bp



app = Sanic("PaymentService")
Extend(app)

settings = get_settings()
app.config.update(settings.model_dump())


@app.get("/health")
async def health_check(request):
    return json({"status": "ok"})

app.blueprint(auth_bp)
app.blueprint(webhook_bp)
app.blueprint(users_bp)
app.blueprint(admin_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

    