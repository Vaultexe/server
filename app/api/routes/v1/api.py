from fastapi import APIRouter

from app.api.routes.v1 import auth, collection, invite, secrets, sync, user

router = APIRouter()

# Include subrouters
router.include_router(prefix="/user", router=user.router, tags=["user"])
router.include_router(prefix="/auth", router=auth.router, tags=["auth"])
router.include_router(prefix="/sync", router=sync.router, tags=["sync"])
router.include_router(prefix="/invite", router=invite.router, tags=["invite"])
router.include_router(prefix="/secrets", router=secrets.router, tags=["secrets"])
router.include_router(prefix="/collection", router=collection.router, tags=["collection"])
