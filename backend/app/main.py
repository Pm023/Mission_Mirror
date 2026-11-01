from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.api import missions, science, mentor, exploration

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Explainable space mission simulator with counterfactual replay for junior astronauts.",
    lifespan=lifespan
)

# Enable CORS for local development and integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_enabled": bool(settings.LLM_PROVIDER and settings.LLM_API_KEY),
        "llm_provider": settings.LLM_PROVIDER
    }

# Register API routers
app.include_router(missions.router)
app.include_router(science.router)
app.include_router(mentor.router)
app.include_router(exploration.router)

# Mount frontend directory for seamless local running
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("  [>] MISSION MIRROR -- Junior Astronaut Mission Trainer")
    print("  Web App running at: http://localhost:8000")
    print("  API Documentation:  http://localhost:8000/docs")
    print("="*60 + "\n")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
