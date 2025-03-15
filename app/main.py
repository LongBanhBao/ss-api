from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import create_db_and_tables
from app.routers import ai, assignments, auth, savedcode, submissions, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    print("Startup")
    yield
    # Shutdown
    print("Shutdown")


settings = get_settings()

app = FastAPI(lifespan=lifespan)

origins = [settings.FRONTEND_ORIGIN if settings.ENVIRONMENT != "development" else "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

routers = [users, auth, ai, assignments, submissions, savedcode]
for router in [r.router for r in routers]:
    app.include_router(router)
