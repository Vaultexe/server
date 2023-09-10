from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse, Response

router = APIRouter()

@router.get("/health")
async def health():
    return Response(status_code=status.HTTP_200_OK)