import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from supabase import create_client, Client
from typing import Optional

# --- SQLAlchemy Configuration (Optional) ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = None
SessionLocal = None

if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, poolclass=NullPool)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print("[OK] PostgreSQL database connected")
    except Exception as e:
        print(f"[WARN] PostgreSQL connection failed: {e}")
        engine = None
        SessionLocal = None
else:
    print("[WARN] DATABASE_URL not set - SQLAlchemy database features will be disabled.")

Base = declarative_base()

def get_db():
    """Dependency to get a DB session. Raises an error if DB is not configured."""
    if not SessionLocal:
        raise RuntimeError("Database not configured. Please set the DATABASE_URL environment variable.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Testing Database (SQLite) ---
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def get_test_db():
    """Dependency for testing database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Supabase Configuration (Optional) ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Optional[Client] = None

if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("[OK] Supabase client connected")
    except Exception as e:
        print(f"[WARN] Supabase connection failed: {e}")
        supabase = None
else:
    print("[WARN] SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set - Supabase features will be disabled.")

def get_supabase() -> Client:
    """
    Dependency to get the Supabase client.
    Raises a RuntimeError if Supabase is not configured.
    """
    if supabase is None:
        raise RuntimeError("Supabase not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables.")
    return supabase
