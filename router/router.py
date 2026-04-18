from fastapi import APIRouter
from .cors import add_cors_middleware
from mediator.user.api.routes import router as user_router


def create_main_router() -> APIRouter:
    main_router = APIRouter()
    main_router.include_router(user_router)
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