from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api import setup_routers
from app.core.config import get_settings
from app.core.database import init_db

settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = setup_routers(app)


@app.on_event("startup")
def on_startup():
    init_db()
