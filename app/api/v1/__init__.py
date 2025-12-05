from fastapi import APIRouter

from app.api.v1 import auth, users, dvi, mitra, opportunities

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(dvi.router, prefix="/dvi", tags=["dvi"])
api_router.include_router(mitra.router, prefix="/mitra", tags=["mitra"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
