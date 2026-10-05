from app.main import app

# Vercel looks for the ASGI application object `app` in api/index.py or app/main.py
__all__ = ["app"]
