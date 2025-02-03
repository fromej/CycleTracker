from fastapi import FastAPI

from app.core.config import get_settings


def setup_routers(app: FastAPI):
    from .auth import router as auth_router
    from .user import router as user_router
    from .period import period_router
    # Include routers
    settings = get_settings()
    app.include_router(auth_router, prefix=f"{settings.api_v1_str}/auth", tags=["Auth"])
    app.include_router(user_router, prefix=f"{settings.api_v1_str}", tags=["User"])
    app.include_router(period_router, prefix=f"{settings.api_v1_str}", tags=["Periods"])

    return app
