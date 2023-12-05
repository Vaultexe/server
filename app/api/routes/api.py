from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse, Response

from app.api.routes import v1

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def root():
    return """
        <h1>Welcome to Vaultexe docs 👋</h1>
        <p>Here are some links to get you started:</p>
        <ul>
            <li><a href="/openapi.json">/openapi.json</a> - OpenAPI (previously known as Swagger) JSON file</li>
            <li><a href="/docs">/docs</a> - automatic interactive API documentation (provided by <a href="">Swagger UI</a>)</li>
            <li><a href="/redoc">/redoc</a> - alternative automatic interactive API documentation (provided by <a href="">ReDoc</a>)</li>
        </ul>
    """


@router.get("/health")
async def health():
    return Response(status_code=status.HTTP_200_OK)


# Include subrouters
router.include_router(prefix="/v1", router=v1.router, tags=["v1"])
