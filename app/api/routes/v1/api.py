from fastapi import APIRouter

from app.api.routes.v1 import user

router = APIRouter()

# Include subrouters
router.include_router(prefix="/user", router=user.router, tags=["user"])
