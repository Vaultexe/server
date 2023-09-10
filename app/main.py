from fastapi import FastAPI
from fastapi.middleware import cors

from app.api.routes import api
from app.core.config import settings


def add_routers(app: FastAPI) -> None:
    app.include_router(api.router)


def add_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        cors.CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_app() -> FastAPI:
    """App factory"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="A production grade server example of a password manager",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    add_routers(app)
    add_middlewares(app)
    return app


app = create_app()
