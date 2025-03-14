import uvicorn

from settings import settings

if __name__ == "__main__":
    uvicorn.run(
        app="application:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
