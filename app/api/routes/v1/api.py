from fastapi import APIRouter

from app.api.routes.v1 import auth, invite, user

router = APIRouter()

# Include subrouters
router.include_router(prefix="/user", router=user.router, tags=["user"])
router.include_router(prefix="/auth", router=auth.router, tags=["auth"])
router.include_router(prefix="/invite", router=invite.router, tags=["invite"])
