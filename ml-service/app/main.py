from fastapi import FastAPI
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import detection
from app.core.config import settings
from app.core import security

app = FastAPI(title="Object Detection API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(
    detection.router,
    prefix="/api/v1",
    tags=["detection"],
    dependencies=[Depends(security.security)]
)

@app.on_event("startup")
async def startup():
    from app.utils.helpers import ensure_directory
    ensure_directory(settings.upload_dir)
    ensure_directory(settings.results_dir)