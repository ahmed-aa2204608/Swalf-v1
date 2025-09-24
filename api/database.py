from sqlalchemy import create_engine, Column, String, Text, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Podcast(Base):
    __tablename__ = "podcasts"
    
    id = Column(String, primary_key=True)
    status = Column(String, nullable=False, default="topic_submitted")
    
    # Input data
    topic = Column(Text, nullable=False)
    info = Column(Text)
    file_content = Column(Text)
    
    # Processing results
    classification = Column(JSON)
    host_persona = Column(JSON)
    guest_persona = Column(JSON)
    outline = Column(JSON)
    persona_outline = Column(JSON)
    culture_outline = Column(JSON)
    script = Column(JSON)
    
    # Audio file info
    audio_file_path = Column(String)
    audio_duration_seconds = Column(Float)
    file_size_mb = Column(Float)
    
    # Metadata
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    print("🔗 [DEBUG] Creating database session...")
    db = SessionLocal()
    try:
        print("🔗 [DEBUG] Database session created successfully")
        yield db
    except Exception as e:
        print(f"❌ [DEBUG] Error with database session: {str(e)}")
        raise
    finally:
        print("🔗 [DEBUG] Closing database session...")
        db.close()
