# app/system/urls.py

from fastapi import APIRouter

from app.system.views.permissions import permission_router
from app.system.views.roles import role_router
from app.system.views.users import user_router

router = APIRouter()

router.include_router(user_router, prefix="/users", tags=["users"])
router.include_router(role_router, prefix="/roles", tags=["roles"])
router.include_router(permission_router, prefix="/permissions", tags=["permissions"])
