import uvicorn

from jlib.enums import AppEnvironmentEnum
from jlib.redis import start_redis_server
from settings import settings

if __name__ == "__main__":
    if settings.environment == AppEnvironmentEnum.LOCAL:
        start_redis_server()

    uvicorn.run(
        app="application:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
