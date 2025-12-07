import os
from supabase import create_client, Client
from typing import Optional

url: Optional[str] = os.environ.get("SUPABASE_URL")
key: Optional[str] = os.environ.get("SUPABASE_KEY")
supabase: Optional[Client] = None

if url and key:
    try:
        supabase = create_client(url, key)
        print("✅ Supabase (db.py) connected")
    except Exception as e:
        print(f"⚠️ Supabase (db.py) connection failed: {e}")
        supabase = None
else:
    print("⚠️ SUPABASE_URL or SUPABASE_KEY not set in db.py")

def get_supabase_client() -> Client:
    """Get Supabase client or raise error"""
    if not supabase:
        raise RuntimeError("Supabase not configured")
    return supabase
