import os
import sys
import uuid
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DATABASE_URL

load_dotenv()

def verify_rls_insert():
    if not DATABASE_URL:
        print("DATABASE_URL not set")
        return

    engine = create_engine(DATABASE_URL)
    
    # Generate IDs
    user_id = uuid.uuid4()
    company_id = uuid.uuid4()
    
    print(f"Testing with User ID: {user_id}")
    
    with engine.connect() as connection:
        # Start transaction
        with connection.begin():
            try:
                # 1. Set Context
                claims = json.dumps({"sub": str(user_id)})
                print(f"Setting claims: {claims}")
                connection.execute(text("SET request.jwt.claims = :claims"), {"claims": claims})
                
                # Debug: Check auth.uid()
                uid_check = connection.execute(text("SELECT auth.uid()")).scalar()
                uid_type = connection.execute(text("SELECT pg_typeof(auth.uid())")).scalar()
                print(f"DEBUG: auth.uid() inside transaction is: {uid_check}")
                print(f"DEBUG: auth.uid() type is: {uid_type}")
                print(f"DEBUG: Expected user_id is: {user_id}")
                
                # 2. Try Insert
                print("Attempting INSERT...")
                sql = """
                INSERT INTO scheduled_whatsapp_messages 
                (id, company_id, user_id, phone, message, scheduled_at, status)
                VALUES (:id, :company_id, :user_id, :phone, :message, :scheduled_at, :status)
                """
                
                params = {
                    "id": uuid.uuid4(),
                    "company_id": company_id,
                    "user_id": user_id,
                    "phone": "1234567890",
                    "message": "Test RLS",
                    "scheduled_at": datetime.now(),
                    "status": "pending"
                }
                
                connection.execute(text(sql), params)
                print("SUCCESS: Inserted row with RLS context.")
                
            except Exception as e:
                print(f"FAILURE: {e}")

if __name__ == "__main__":
    verify_rls_insert()
