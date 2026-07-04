"""App factory. The engine singleton lives here."""

import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware


from banking.api.routes import router
from banking.api.views import views
from banking.engine import BankingEngine

engine = BankingEngine()


def get_engine() -> BankingEngine:
    return engine


def create_app() -> FastAPI:
    app = FastAPI(
        title="Banking Simulator",
        description="Simulated banking system with lazy cashback settlement",
        version="0.1.0",
    )
    allowed = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in allowed.split(",")],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/operations")
    app.include_router(views, prefix="/views")

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse("/docs")
    
    return app


app = create_app()