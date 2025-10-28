import uvicorn

from configs import override_external_loggers, settings
from migrations.scripts import run_migrations

if __name__ == "__main__":
    override_external_loggers()

    if settings.db_apply_migrations:
        run_migrations()

    uvicorn.run(
        app="application:fastapi_app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_config=None,
    )
