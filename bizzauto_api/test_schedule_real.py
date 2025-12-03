import requests
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt

load_dotenv()

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
ALGORITHM = "HS256"

# Mock User Data (must match a real user or at least have valid structure)
# I need a valid user ID and company ID.
# I'll use the ones from the debug_db.py output if available, or just random UUIDs 
# and hope the DB check in get_current_user doesn't fail (it does check DB).
# So I need a real user ID.
# I'll query the DB first to get a valid user.

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

try:
    result = session.execute(text("SELECT id, company_id, email FROM users LIMIT 1"))
    user = result.fetchone()
    if not user:
        print("No users found in DB. Cannot test.")
        exit(1)
    
    user_id = str(user[0])
    company_id = str(user[1])
    email = user[2]
    print(f"Using User: {user_id}, Company: {company_id}")

    # Generate Token
    payload = {
        "sub": user_id,
        "user_metadata": {"company_id": company_id},
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm=ALGORITHM)
    print(f"Generated Token: {token[:10]}...")

    # Send Request
    url = "http://127.0.0.1:8000/api/scheduled-whatsapp-messages"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "phone": "923001234567",
        "message": "Test message from script",
        "scheduled_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat() + "Z"
    }
    
    print(f"Sending POST to {url} with data: {data}")
    response = requests.post(url, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

except Exception as e:
    print(f"Error: {e}")
finally:
    session.close()
