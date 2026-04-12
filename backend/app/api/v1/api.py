from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.exams import router as exams_router
from app.api.v1.endpoints.machines import router as machines_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(machines_router)
api_router.include_router(exams_router)
