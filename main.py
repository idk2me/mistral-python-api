from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.db import init_db
from utils.logging_config import setup_logging, get_logger
from utils.settings import settings
from routes.router import api_router
import requests

headers = {"Authorization": f"Bearer {settings.mistral_api_key}"}
url = "https://api.mistral.ai/v1/models"
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # initializing db
    await init_db()

    # testing connection
    logger.info(f"Current headers set: {headers}")
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        logger.info(f"response: {res}")
        logger.info("Mistral API seems to be working, starting app...")
    else:
        logger.info(f"Response from mistral api: {res}")
        logger.error("Issues querying Mistral's API, shutting down...")
        raise ConnectionError("Issues querying Mistral's API...")

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
