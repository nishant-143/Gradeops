"""
GradeOps FastAPI Application.

Main entry point for the backend API.
"""

# Trigger uvicorn reload with updated env

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.api.routes import auth, exams, rubrics, submissions, answer_regions, grades, export, pipeline
from app.core.supabase import SessionLocal, health_check
from app.services import PipelineService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan event handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    
    Startup:
        - Check database connection
        - Verify storage buckets
        
    Shutdown:
        - Close connections cleanly
    """
    # Startup
    logger.info("GradeOps API starting...")
    try:
        health = await health_check()
        if health["database"] and health["storage"]:
            logger.info("[SUCCESS] All services healthy")
        else:
            logger.warning(f"[WARNING] Health check issues: {health}")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
    
    worker_running = True

    async def pipeline_worker_loop():
        while worker_running:
            db = SessionLocal()
            try:
                has_job = await PipelineService.process_next_job(db)
                if not has_job:
                    await asyncio.sleep(1.5)
            except Exception as worker_exc:
                logger.exception("Pipeline worker error: %s", worker_exc)
                await asyncio.sleep(2.5)
            finally:
                db.close()

    worker_task = asyncio.create_task(pipeline_worker_loop())

    yield
    
    # Shutdown
    worker_running = False
    worker_task.cancel()
    try:
        await worker_task
    except Exception:
        pass
    logger.info("[STOP] GradeOps API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="GradeOps API",
    description="AI-powered exam grading system with TA review dashboard",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server
        "https://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request timing and logging
@app.middleware("http")
async def add_request_timing(request: Request, call_next):
    """Log request duration."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} "
        f"({duration:.2f}s)"
    )
    return response


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if str(exc) else "Unknown error"
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health():
    """Check API health and database connection."""
    try:
        from app.core.config import settings
        import httpx
        
        status = await health_check()
        
        # Check LLM configuration
        status["llm"] = bool(settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY or settings.XAI_API_KEY)
        
        # Check OCR service
        status["ocr"] = False
        if settings.OCR_API_URL:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    res = await client.get(f"{settings.OCR_API_URL.rstrip('/')}/health")
                    status["ocr"] = (res.status_code == 200)
            except Exception:
                pass
                
        all_healthy = all(status.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "services": status,
            "version": "0.1.0",
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
        }


# Root endpoint
@app.get("/", tags=["root"])
def root():
    """API root endpoint."""
    return {
        "message": "GradeOps API",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(auth.router)
app.include_router(exams.router)
app.include_router(rubrics.router)
app.include_router(submissions.router)
app.include_router(answer_regions.router)
app.include_router(grades.router)
app.include_router(export.router)
app.include_router(pipeline.router)

logger.info("[SUCCESS] All routes registered")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
