from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import PyPDF2
import io
import os

from database import get_db
from services import PodcastService
from schemas import (
    TopicSubmissionRequest, 
    PersonaModificationRequest,
    PodcastCreationResponse,
    PodcastStatusResponse,
    PersonaSelectionResponse,
    AudioGenerationResponse,
    PodcastStatus,
    PodcastHistorySummary
)

router = APIRouter(prefix="/api/podcast", tags=["podcast"])
podcast_service = PodcastService()

@router.post("/submit-topic", response_model=PodcastCreationResponse)
async def submit_topic(
    request: TopicSubmissionRequest,
    db: Session = Depends(get_db)
):
    """Step 1: Submit topic and get persona suggestions"""
    print("🎯 [DEBUG] /submit-topic endpoint called")
    print(f"🎯 [DEBUG] Request data: topic='{request.topic}', info='{request.info}'")
    
    try:
        print("🎯 [DEBUG] Starting podcast creation...")
        # Create podcast entry
        podcast_id = podcast_service.create_podcast(
            db, 
            request.topic, 
            request.info,
            request.file_content
        )
        
        print(f"🎯 [DEBUG] Podcast created successfully with ID: {podcast_id}")
        
        response = PodcastCreationResponse(
            podcast_id=podcast_id,
            status=PodcastStatus.TOPIC_SUBMITTED,
            message="Topic submitted successfully. Generating persona suggestions..."
        )
        
        print(f"🎯 [DEBUG] Returning response: {response}")
        return response
        
    except Exception as e:
        print(f"❌ [DEBUG] Error in submit_topic: {str(e)}")
        print(f"❌ [DEBUG] Exception type: {type(e)}")
        import traceback
        print(f"❌ [DEBUG] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit-topic-with-file", response_model=PodcastCreationResponse)
async def submit_topic_with_file(
    topic: str,
    info: str = "",
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Submit topic with optional PDF file upload"""
    file_content = None
    
    if file:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        try:
            # Read PDF content
            pdf_content = await file.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            
            text_content = []
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
            
            file_content = "\n".join(text_content)
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process PDF: {str(e)}")
    
    try:
        podcast_id = podcast_service.create_podcast(db, topic, info, file_content)
        
        return PodcastCreationResponse(
            podcast_id=podcast_id,
            status=PodcastStatus.TOPIC_SUBMITTED,
            message="Topic and file submitted successfully."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-personas/{podcast_id}", response_model=PersonaSelectionResponse)
async def generate_personas(
    podcast_id: str,
    db: Session = Depends(get_db)
):
    """Step 2: Generate and return persona suggestions"""
    try:
        host, guest, classification = podcast_service.classify_and_suggest_personas(db, podcast_id)
        
        return PersonaSelectionResponse(
            podcast_id=podcast_id,
            suggested_host=host,
            suggested_guest=guest,
            classification=classification
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm-personas", response_model=dict)
async def confirm_personas(
    request: PersonaModificationRequest,
    db: Session = Depends(get_db)
):
    """Step 3: Confirm or modify persona selection"""
    try:
        podcast_service.update_personas(
            db, 
            request.podcast_id, 
            request.host_persona, 
            request.guest_persona
        )
        
        return {"message": "Personas confirmed successfully", "podcast_id": request.podcast_id}
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-content/{podcast_id}")
async def generate_content(
    podcast_id: str,
    db: Session = Depends(get_db)
):
    """Step 4: Generate outline, persona outline, and culture outline"""
    try:
        outline, persona_outline, culture_outline = podcast_service.generate_content(db, podcast_id)
        
        return {
            "message": "Content generated successfully",
            "podcast_id": podcast_id,
            "outline": outline,
            "persona_outline": persona_outline,
            "culture_outline": culture_outline
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-script/{podcast_id}")
async def generate_script(
    podcast_id: str,
    db: Session = Depends(get_db)
):
    """Step 5: Generate final script"""
    try:
        script = podcast_service.generate_script(db, podcast_id)
        
        return {
            "message": "Script generated successfully",
            "podcast_id": podcast_id,
            "script": script
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-audio/{podcast_id}", response_model=AudioGenerationResponse)
async def generate_audio(
    podcast_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Step 6: Generate TTS audio (background task)"""
    try:
        audio_file_path = await podcast_service.generate_audio(db, podcast_id)
        
        return AudioGenerationResponse(
            podcast_id=podcast_id,
            audio_file_path=audio_file_path,
            file_size_mb=None  # Will be calculated in service
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete-pipeline/{podcast_id}")
async def complete_full_pipeline(
    podcast_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Complete the entire pipeline automatically (for testing)"""
    try:
        background_tasks.add_task(podcast_service.complete_full_pipeline, db, podcast_id)
        
        return {
            "message": "Full pipeline started in background",
            "podcast_id": podcast_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{podcast_id}", response_model=PodcastStatusResponse)
async def get_podcast_status(
    podcast_id: str,
    db: Session = Depends(get_db)
):
    """Get current podcast status and all generated content"""
    try:
        podcast = podcast_service.get_podcast_status(db, podcast_id)
        
        return PodcastStatusResponse(
            podcast_id=podcast.id,
            status=podcast.status,
            created_at=podcast.created_at,
            updated_at=podcast.updated_at,
            topic=podcast.topic,
            info=podcast.info,
            classification=podcast.classification,
            host_persona=podcast.host_persona,
            guest_persona=podcast.guest_persona,
            outline=podcast.outline,
            persona_outline=podcast.persona_outline,
            culture_outline=podcast.culture_outline,
            script=podcast.script,
            audio_file_path=podcast.audio_file_path,
            error_message=podcast.error_message
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download-audio/{podcast_id}")
async def download_audio(
    podcast_id: str,
    db: Session = Depends(get_db)
):
    """Download generated audio file"""
    try:
        podcast = podcast_service.get_podcast_status(db, podcast_id)
        
        if not podcast.audio_file_path or not os.path.exists(podcast.audio_file_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            podcast.audio_file_path,
            media_type="audio/mpeg",
            filename=f"podcast_{podcast_id}.mp3"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[PodcastHistorySummary])
async def get_history(
    db: Session = Depends(get_db)
):
    """Get history of all podcast generations"""
    try:
        podcasts = podcast_service.get_podcast_history(db)
        
        return [
            PodcastHistorySummary(
                podcast_id=podcast.id,
                topic=podcast.topic,
                status=podcast.status,
                created_at=podcast.created_at,
                audio_available=bool(podcast.audio_file_path and os.path.exists(podcast.audio_file_path)),
                error_message=podcast.error_message,
                classification=podcast.classification
            )
            for podcast in podcasts
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
