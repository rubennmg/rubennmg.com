from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.routes.admin_matches import router as admin_matches_router
from app.api.routes.admin_players import router as admin_players_router
from app.api.routes.auth import router as auth_router
from app.api.routes.public_games import router as public_games_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(admin_players_router)
api_router.include_router(admin_matches_router)
api_router.include_router(public_games_router)
