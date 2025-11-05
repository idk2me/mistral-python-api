from fastapi import APIRouter
from utils.db import get_user_settings, update_user_settings
from schemas.paper import UserSettings

router = APIRouter()


@router.get("/userSettings")
async def get_user_settings_endpoint():
    settings = await get_user_settings()
    return settings


@router.post("/updateUser")
async def update_user_settings_endpoint(user_settings: UserSettings):
    await update_user_settings(
        user_settings.niche_interests, user_settings.additional_params
    )
    return {"status": 200, "message": "User settings updated successfully"}
