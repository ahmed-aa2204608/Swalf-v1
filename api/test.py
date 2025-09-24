import os
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Testing Neon connection...")
print(f"URL: {DATABASE_URL[:50]}...")

try:
    # Test SQLAlchemy connection with proper text() wrapper
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()
        print(f"✅ SQLAlchemy connection successful!")
        print(f"📊 PostgreSQL version: {version[0]}")
    
    print("✅ Neon database is ready!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("🔄 Trying direct psycopg2 connection...")
    
    try:
        # Fallback to direct psycopg2 test
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Direct psycopg2 connection successful!")
        print(f"📊 PostgreSQL version: {version[0]}")
        cursor.close()
        conn.close()
    except Exception as e2:
        print(f"❌ Direct connection also failed: {e2}")