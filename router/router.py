from fastapi import APIRouter
from .cors import add_cors_middleware
from mediator.user.api.routes import router as user_router
from mediator.upload.api.routes import router as upload_router
from mediator.persona.api.routes import router as persona_router
from mediator.session.api.routes import router as session_router


def create_main_router() -> APIRouter:
    main_router = APIRouter()
    main_router.include_router(user_router)
    main_router.include_router(upload_router)
    main_router.include_router(persona_router)
    main_router.include_router(session_router)
    return main_router


def configure_app_cors(app) -> None:
    """
    Configure CORS for the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    add_cors_middleware(app)


# Export the main router creation function and CORS configuration
__all__ = ["configure_app_cors", "create_main_router"]
