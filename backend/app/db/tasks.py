import os

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import DATABASE_URL, DATABASE_NAME

import logging

logger = logging.getLogger("dev")


async def connect_to_db(app: FastAPI) -> None:
    database_name = f"{DATABASE_NAME}_test" if os.environ.get("TESTING") else DATABASE_NAME
    
    try:
        mongo_client = AsyncIOMotorClient(DATABASE_URL, uuidRepresentation='standard')
        app.mongo_client = mongo_client
        app.database = mongo_client[database_name]
        logger.debug("--- DB CONNECTED SUCCESSFULLY ---")
    except Exception as e:
        logger.warning("--- DB CONNECTION ERROR ---")
        logger.warning(e)
        logger.warning("--- DB CONNECTION ERROR ---")


async def close_db_connection(app: FastAPI) -> None:
    try:
        app.mongo_client.close()
        logger.debug("--- DB DISCONNECTED SUCCESSFULLY ---")
    except Exception as e:
        logger.warning("--- DB DISCONNECT ERROR ---")
        logger.warning(e)
        logger.warning("--- DB DISCONNECT ERROR ---")