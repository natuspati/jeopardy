import os

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import DATABASE_URL, DATABASE_NAME

from app.db.repositories import COLLECTION_CONFIGS

import logging

logger = logging.getLogger("dev")


async def connect_to_db(app: FastAPI) -> None:
    database_name = f"{DATABASE_NAME}_test" if os.environ.get("TESTING") else DATABASE_NAME
    
    try:
        mongo_client = AsyncIOMotorClient(DATABASE_URL, uuidRepresentation='standard')
        app.mongo_client = mongo_client
        app.database = mongo_client[database_name]
        logger.debug("--- DB CONNECTED SUCCESSFULLY ---")
        # look for index fields and create them when necessary
        await check_and_create_collection_indices(app.database)
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


async def check_and_create_collection_indices(db: AsyncIOMotorDatabase) -> None:
    """
    Check if any collection should have indexed fields.
    """
    for collection_config in COLLECTION_CONFIGS:
        index_fields = collection_config.get("index_fields")
        unique_constraint = collection_config.get("unique", True)
        background = collection_config.get("background", True)
        
        if index_fields:
            collection = db.get_collection(collection_config["name"])
            existing_indices = tuple(await collection.index_information())
            absent_index_fields = []
            
            if isinstance(index_fields, str):
                # one indexed field without indexing direction is given
                if index_fields not in existing_indices:
                    absent_index_fields = index_fields
            else:
                # one or more indexed fields and directions are given
                
                for i in range(index_fields):
                    if index_fields[i][0] not in existing_indices:
                        absent_index_fields.append(index_fields[i])
                
            if absent_index_fields:
                await collection.create_index(
                    keys=absent_index_fields, unique=unique_constraint, background=background
                )
