from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes import auth, health, files, ai, billing

settings = get_settings()

app = FastAPI(
    title="VitalSync API",
    version="1.0.0",
    description="AI-powered health optimization platform — MVP",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow Flutter web and mobile dev tools to reach the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(files.router)
app.include_router(ai.router)
app.include_router(billing.router)


@app.get("/", tags=["meta"])
def root():
    return {"service": "VitalSync API", "status": "healthy", "docs": "/docs"}


@app.get("/health-check", tags=["meta"])
def health_check():
    return {"status": "ok"}
