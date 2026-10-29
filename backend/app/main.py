"""
Smart Krishi Advisor FastAPI Application.
Problem ID: HACK-P302 (Category: Agriculture)
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .config import settings
from .routes import health, crops, recommend, compare, profiles

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=(
        "Explainable rule-based decision support system for crop recommendation and "
        "agricultural suitability analysis across Indian agro-climatic zones."
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom validation exception handler for user-friendly error messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        errors.append({"field": loc, "message": msg})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Input validation error",
            "errors": errors,
            "safety_note": "Please review specified field constraints (e.g., pH 0-14, Humidity 0-100%)."
        }
    )

# Include API routes under /api
app.include_router(health.router, prefix="/api")
app.include_router(crops.router, prefix="/api")
app.include_router(recommend.router, prefix="/api")
app.include_router(compare.router, prefix="/api")
app.include_router(profiles.router, prefix="/api")


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "version": settings.version,
        "status": "ONLINE",
        "docs": "/docs",
        "health": "/api/health"
    }
