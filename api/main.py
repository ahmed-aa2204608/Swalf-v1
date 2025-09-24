from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn
import os

from database import create_tables
from routes import router as podcast_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 [DEBUG] Starting up API...")
    try:
        print("🚀 [DEBUG] Creating database tables...")
        create_tables()
        print("🚀 [DEBUG] Database tables created successfully")
        print("🤖 AI Podcast Maker API is ready!")
        yield
    except Exception as e:
        print(f"❌ [DEBUG] Startup error: {str(e)}")
        import traceback
        print(f"❌ [DEBUG] Startup traceback: {traceback.format_exc()}")
        raise
    # Shutdown
    print("👋 API shutting down...")

app = FastAPI(
    title="AI Podcast Maker API",
    description="Generate Arabic podcasts with AI - from topic to audio",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(podcast_router)

# Debug endpoint to test database
from database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

@app.get("/debug/db-test")
async def test_database(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        print("🧪 [DEBUG] Testing database connection...")
        # Simple query to test connection
        result = db.execute("SELECT 1 as test")
        row = result.fetchone()
        print(f"🧪 [DEBUG] Database test result: {row}")
        return {"status": "database_ok", "test_result": row[0] if row else None}
    except Exception as e:
        print(f"❌ [DEBUG] Database test failed: {str(e)}")
        return {"status": "database_error", "error": str(e)}

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the frontend at root
@app.get("/frontend")
async def serve_frontend():
    return FileResponse("static/index.html")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "AI Podcast Maker API is running",
        "version": "1.0.0"
    }

# Root endpoint with API info
@app.get("/")
async def root():
    return {
        "message": "🎙️ AI Podcast Maker API",
        "description": "Generate Arabic podcasts from topic to audio",
        "frontend": "/frontend",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "submit_topic": "POST /api/podcast/submit-topic",
            "submit_with_file": "POST /api/podcast/submit-topic-with-file", 
            "generate_personas": "POST /api/podcast/generate-personas/{podcast_id}",
            "confirm_personas": "POST /api/podcast/confirm-personas",
            "generate_content": "POST /api/podcast/generate-content/{podcast_id}",
            "generate_script": "POST /api/podcast/generate-script/{podcast_id}",
            "generate_audio": "POST /api/podcast/generate-audio/{podcast_id}",
            "complete_pipeline": "POST /api/podcast/complete-pipeline/{podcast_id}",
            "get_status": "GET /api/podcast/status/{podcast_id}",
            "download_audio": "GET /api/podcast/download-audio/{podcast_id}"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
