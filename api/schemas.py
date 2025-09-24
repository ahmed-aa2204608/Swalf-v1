from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

class PodcastStatus(str, Enum):
    TOPIC_SUBMITTED = "topic_submitted"
    PERSONAS_SUGGESTED = "personas_suggested"
    PERSONAS_CONFIRMED = "personas_confirmed"
    OUTLINE_GENERATED = "outline_generated"
    SCRIPT_GENERATED = "script_generated"
    AUDIO_GENERATED = "audio_generated"
    COMPLETED = "completed"
    FAILED = "failed"

# Request Models
class TopicSubmissionRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500, description="Main topic for the podcast")
    info: str = Field(default="", max_length=5000, description="Additional information or description")
    file_content: Optional[str] = Field(default=None, description="Extracted text from uploaded PDF")

class PersonaModificationRequest(BaseModel):
    podcast_id: str
    host_persona: Dict[str, Any]
    guest_persona: Dict[str, Any]

class PersonaSelectionResponse(BaseModel):
    podcast_id: str
    suggested_host: Dict[str, Any]
    suggested_guest: Dict[str, Any]
    classification: Dict[str, str]

# Response Models
class PodcastCreationResponse(BaseModel):
    podcast_id: str
    status: PodcastStatus
    message: str

class PodcastHistorySummary(BaseModel):
    podcast_id: str
    topic: str
    status: PodcastStatus
    created_at: datetime
    audio_available: bool
    error_message: Optional[str] = None
    classification: Optional[Dict[str, str]] = None

class PodcastStatusResponse(BaseModel):
    podcast_id: str
    status: PodcastStatus
    created_at: datetime
    updated_at: datetime
    topic: str
    info: Optional[str]
    classification: Optional[Dict[str, Any]]
    host_persona: Optional[Dict[str, Any]]
    guest_persona: Optional[Dict[str, Any]]
    outline: Optional[Dict[str, Any]]
    persona_outline: Optional[Dict[str, Any]]
    culture_outline: Optional[Dict[str, Any]]
    script: Optional[Dict[str, Any]]
    audio_file_path: Optional[str]
    error_message: Optional[str]

class PersonaBase(BaseModel):
    age: str
    gender: str
    JobDescription: str
    SpeakingStyle: str
    OCEAN_Persona: Dict[str, str]

class ClassificationResponse(BaseModel):
    domain: str
    style: str
    sensitivity: str
    raw_output: Optional[str]

class OutlineResponse(BaseModel):
    Intro1: Dict[str, Any]
    Intro2: Dict[str, Any]
    Points: Dict[str, Any]
    Con: Dict[str, Any]
    topic: Optional[str]
    domain: Optional[str]

class AudioGenerationResponse(BaseModel):
    podcast_id: str
    audio_file_path: str
    audio_duration_seconds: Optional[float]
    file_size_mb: Optional[float]
