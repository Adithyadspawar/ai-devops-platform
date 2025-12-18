# app/sentry_integration.py
import os

try:
    import sentry_sdk
    from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
    SENTRY_AVAILABLE = True
except Exception:
    sentry_sdk = None
    SentryAsgiMiddleware = None
    SENTRY_AVAILABLE = False

SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
SENTRY_ENV = os.environ.get("SENTRY_ENV", "development")

def init_sentry():
    if not SENTRY_AVAILABLE or not SENTRY_DSN:
        # Sentry not configured or package missing — safe no-op
        return None
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENV,
        traces_sample_rate=0.1,
    )
    return sentry_sdk

def wrap_app_with_sentry(app):
    if SENTRY_AVAILABLE and SENTRY_DSN and SentryAsgiMiddleware is not None:
        return SentryAsgiMiddleware(app)
    return app

