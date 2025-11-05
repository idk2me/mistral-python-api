from fastapi import APIRouter
from routes.papers import router as papers_router
from routes.user import router as user_router

api_router = APIRouter()

api_router.include_router(papers_router, tags=["papers"])
api_router.include_router(user_router, tags=["user"])
