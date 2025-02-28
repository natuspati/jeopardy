from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Context manager to manage the lifecycle of a FastAPI application.

    Upon entering the context, it runs the startup events, and upon exiting,
    it runs the shutdown events.

    :param app: FastAPI application instance to manage
    :yield:
    """
    await run_startup_events(app)
    yield
    await run_shutdown_events(app)


async def run_startup_events(app: FastAPI) -> None:
    """
    Perform startup events.

    :param app: application
    :return:
    """
    pass


async def run_shutdown_events(app: FastAPI) -> None:
    """
    Perform shutdown events.

    :param app: application
    :return:
    """
    pass
