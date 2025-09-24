import sys
import os
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Tuple, List
from sqlalchemy.orm import Session

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.persona_db import personas
from api_init import get_deployment
from topic_classify import classify_topic
from outline_gen import generate_outline
from outline_enhance_persona import enhance_outline_with_personas
from outline_enhance_culture import enhance_outline_with_culture
from script_generator import script_generator
from persona_selector import select_personas
from test2 import getTTS
from database import Podcast
from schemas import PodcastStatus

class PodcastService:
    def __init__(self):
        self.deployment = get_deployment()
    
    def create_podcast(self, db: Session, topic: str, info: str = "", file_content: str = None) -> str:
        """Create a new podcast entry and return its ID"""
        print(f"🔧 [DEBUG] create_podcast called with topic: '{topic}', info: '{info}'")
        
        try:
            podcast_id = str(uuid.uuid4())
            print(f"🔧 [DEBUG] Generated podcast_id: {podcast_id}")
            
            # Combine info and file_content
            combined_info = f"{info}\n\n{file_content}" if file_content else info
            print(f"🔧 [DEBUG] Combined info length: {len(combined_info)} chars")
            
            print(f"🔧 [DEBUG] Creating Podcast object...")
            podcast = Podcast(
                id=podcast_id,
                status=PodcastStatus.TOPIC_SUBMITTED,
                topic=topic,
                info=combined_info,
                file_content=file_content
            )
            
            print(f"🔧 [DEBUG] Adding to database session...")
            db.add(podcast)
            
            print(f"🔧 [DEBUG] Committing to database...")
            db.commit()
            
            print(f"🔧 [DEBUG] Podcast created successfully: {podcast_id}")
            return podcast_id
            
        except Exception as e:
            print(f"❌ [DEBUG] Error in create_podcast: {str(e)}")
            print(f"❌ [DEBUG] Exception type: {type(e)}")
            import traceback
            print(f"❌ [DEBUG] Traceback: {traceback.format_exc()}")
            raise
    
    def classify_and_suggest_personas(self, db: Session, podcast_id: str) -> Tuple[Dict, Dict, Dict]:
        """Step 1: Classify topic and suggest personas"""
        podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
        if not podcast:
            raise ValueError("Podcast not found")
        
        try:
            # Classify topic
            classification = classify_topic(podcast.topic, podcast.info or "", self.deployment)
            
            # Select personas
            host, guest, selected_indices = select_personas(
                podcast.topic, 
                podcast.info or "", 
                personas, 
                classification=classification.get('domain', ''), 
                k=2
            )
            
            # Update database
            podcast.classification = classification
            podcast.host_persona = host
            podcast.guest_persona = guest
            podcast.status = PodcastStatus.PERSONAS_SUGGESTED
            
            db.commit()
            
            return host, guest, classification
            
        except Exception as e:
            podcast.status = PodcastStatus.FAILED
            podcast.error_message = f"Persona selection failed: {str(e)}"
            db.commit()
            raise
    
    def update_personas(self, db: Session, podcast_id: str, host_persona: Dict, guest_persona: Dict):
        """Step 2: Allow user to modify personas"""
        podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
        if not podcast:
            raise ValueError("Podcast not found")
        
        podcast.host_persona = host_persona
        podcast.guest_persona = guest_persona
        podcast.status = PodcastStatus.PERSONAS_CONFIRMED
        
        db.commit()
    
    def generate_content(self, db: Session, podcast_id: str):
        """Step 3: Generate outline, enhance with personas and culture"""
        podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
        if not podcast:
            raise ValueError("Podcast not found")
        
        if podcast.status != PodcastStatus.PERSONAS_CONFIRMED:
            raise ValueError("Personas must be confirmed before generating content")
        
        try:
            # Generate outline
            outline = generate_outline(
                podcast.topic, 
                podcast.info or "", 
                podcast.classification, 
                self.deployment
            )
            
            # Enhance with personas
            persona_outline = enhance_outline_with_personas(
                outline, 
                podcast.host_persona, 
                podcast.guest_persona, 
                self.deployment
            )
            
            # Enhance with culture
            culture_outline = enhance_outline_with_culture(
                persona_outline, 
                podcast.classification, 
                self.deployment
            )
            
            # Update database
            podcast.outline = outline
            podcast.persona_outline = persona_outline
            podcast.culture_outline = culture_outline
            podcast.status = PodcastStatus.OUTLINE_GENERATED
            
            db.commit()
            
            return outline, persona_outline, culture_outline
            
        except Exception as e:
            podcast.status = PodcastStatus.FAILED
            podcast.error_message = f"Content generation failed: {str(e)}"
            db.commit()
            raise
    
    def generate_script(self, db: Session, podcast_id: str):
        """Step 4: Generate final script"""
        podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
        if not podcast:
            raise ValueError("Podcast not found")
        
        if podcast.status != PodcastStatus.OUTLINE_GENERATED:
            raise ValueError("Outline must be generated before creating script")
        
        try:
            # Generate script
            arabic_persona = {
                "host": podcast.host_persona, 
                "guest": podcast.guest_persona, 
                "chemistry_note": "متكاملان دوراً وأسلوباً"
            }
            
            script = script_generator(
                podcast.culture_outline, 
                arabic_persona, 
                podcast.classification, 
                self.deployment
            )
            
            # Update database
            podcast.script = script
            podcast.status = PodcastStatus.SCRIPT_GENERATED
            
            db.commit()
            
            return script
            
        except Exception as e:
            podcast.status = PodcastStatus.FAILED
            podcast.error_message = f"Script generation failed: {str(e)}"
            db.commit()
            raise
    
    async def generate_audio(self, db: Session, podcast_id: str):
        """Step 5: Generate TTS audio"""
        podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
        if not podcast:
            raise ValueError("Podcast not found")
        
        if podcast.status != PodcastStatus.SCRIPT_GENERATED:
            raise ValueError("Script must be generated before creating audio")
        
        try:
            # Generate audio
            audio_file_path = await getTTS(podcast.script)
            
            # Get file info
            if os.path.exists(audio_file_path):
                file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)  # Convert to MB
            else:
                file_size_mb = None
            
            # Update database
            podcast.audio_file_path = audio_file_path
            podcast.file_size_mb = file_size_mb
            podcast.status = PodcastStatus.AUDIO_GENERATED
            
            db.commit()
            
            return audio_file_path
            
        except Exception as e:
            podcast.status = PodcastStatus.FAILED
            podcast.error_message = f"Audio generation failed: {str(e)}"
            db.commit()
            raise
    
    async def complete_full_pipeline(self, db: Session, podcast_id: str):
        """Run the complete pipeline automatically (for testing)"""
        try:
            # Step 1: Classify and suggest personas
            host, guest, classification = self.classify_and_suggest_personas(db, podcast_id)
            
            # Step 2: Auto-confirm personas (in real app, user would review)
            self.update_personas(db, podcast_id, host, guest)
            
            # Step 3: Generate content
            self.generate_content(db, podcast_id)
            
            # Step 4: Generate script
            self.generate_script(db, podcast_id)
            
            # Step 5: Generate audio
            await self.generate_audio(db, podcast_id)
            
            # Mark as completed
            podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
            podcast.status = PodcastStatus.COMPLETED
            db.commit()
            
            return True
            
        except Exception as e:
            podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
            if podcast:
                podcast.status = PodcastStatus.FAILED
                podcast.error_message = f"Pipeline failed: {str(e)}"
                db.commit()
            raise
    
    def get_podcast_status(self, db: Session, podcast_id: str) -> Podcast:
        """Get current podcast status and data"""
        podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
        if not podcast:
            raise ValueError("Podcast not found")
        return podcast

    def get_podcast_history(self, db: Session) -> List[Podcast]:
        """Get all podcast entries ordered by creation date"""
        return db.query(Podcast).order_by(Podcast.created_at.desc()).all()
