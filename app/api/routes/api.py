from fastapi import APIRouter, status
from fastapi.responses import Response

from app.api.routes import v1

router = APIRouter()


@router.get("/health")
async def health():
    return Response(status_code=status.HTTP_200_OK)


# Include subrouters
router.include_router(prefix="/v1", router=v1.router, tags=["v1"])
