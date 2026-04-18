from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.settings import get_settings
from config.logging import setup_logging
from router.router import configure_app_cors, create_main_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    print("🚀 Ghost Mode API starting")

    yield

    print("🛑 Ghost Mode API shutting down")

app = FastAPI(
    title="Ghost Mode API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS using the router module
configure_app_cors(app)

# Create and include the main router with all sub-routers
main_router = create_main_router()
app.include_router(main_router)
