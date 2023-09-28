from fastapi import APIRouter

from app.api.routes.v1 import user
from app.api.routes.v1 import device

router = APIRouter()

# Include subrouters
router.include_router(prefix="/user", router=user.router, tags=["user"])
router.include_router(prefix="/device", router=device.router, tags=["device"])


