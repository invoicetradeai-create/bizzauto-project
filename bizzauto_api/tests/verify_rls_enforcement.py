import os
import sys
import uuid
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DATABASE_URL

load_dotenv()

def verify_rls_enforcement():
    if not DATABASE_URL:
        print("DATABASE_URL not set")
        return

    engine = create_engine(DATABASE_URL)
    
    # User 1 Setup
    user1_id = uuid.uuid4()
    company1_id = uuid.uuid4()
    
    # User 2 Setup
    user2_id = uuid.uuid4()
    company2_id = company1_id # SAME company to test user isolation within tenant
    
    print(f"User 1: {user1_id} (Company: {company1_id})")
    print(f"User 2: {user2_id} (Company: {company2_id})")
    
    table = "scheduled_whatsapp_messages"
    
    # Setup Companies (Need to exist for FK)
    # We use a separate connection/transaction for setup to avoid RLS issues if possible, 
    # or we just insert them. Companies table might have RLS disabled now (we tried earlier).
    print("--- Setting up Companies ---")
    with engine.connect() as conn:
        with conn.begin():
            try:
                conn.execute(text("INSERT INTO companies (id, name) VALUES (:id, 'Comp 1')"), {"id": company1_id})
                if company1_id != company2_id:
                    conn.execute(text("INSERT INTO companies (id, name) VALUES (:id, 'Comp 2')"), {"id": company2_id})
                print("Created companies.")
                
                conn.execute(text("INSERT INTO users (id, company_id, full_name, email, role) VALUES (:id, :cid, 'User 1', 'u1@ex.com', 'user')"), {"id": user1_id, "cid": company1_id})
                conn.execute(text("INSERT INTO users (id, company_id, full_name, email, role) VALUES (:id, :cid, 'User 2', 'u2@ex.com', 'user')"), {"id": user2_id, "cid": company2_id})
                print("Created users.")
            except Exception as e:
                print(f"Error creating setup data (maybe exist?): {e}")

    with engine.connect() as connection:
        # 1. Insert Data for User 1
        print("\n--- Inserting Data for User 1 ---")
        with connection.begin():
            # Set Context for User 1
            claims1 = json.dumps({"sub": str(user1_id), "company_id": str(company1_id)})
            connection.execute(text("SET request.jwt.claims = :claims"), {"claims": claims1})
            connection.execute(text("SET app.current_user_id = :user_id"), {"user_id": str(user1_id)})
            
            # Insert
            sql = f"""
            INSERT INTO {table} (id, company_id, user_id, phone, message, scheduled_at, status)
            VALUES (:id, :company_id, :user_id, '1111111111', 'User 1 Message', NOW(), 'pending')
            """
            connection.execute(text(sql), {
                "id": uuid.uuid4(),
                "company_id": company1_id,
                "user_id": user1_id
            })
            print("Inserted row for User 1")

        # 2. Switch to User 2 and Try to Read
        print("\n--- Switching to User 2 ---")
        with connection.begin():
            # Set Context for User 2
            claims2 = json.dumps({"sub": str(user2_id), "company_id": str(company2_id)})
            connection.execute(text("SET request.jwt.claims = :claims"), {"claims": claims2})
            connection.execute(text("SET app.current_user_id = :user_id"), {"user_id": str(user2_id)})
            
            # Query
            print("Querying table...")
            result = connection.execute(text(f"SELECT user_id, message FROM {table}")).fetchall()
            
            print(f"User 2 sees {len(result)} rows:")
            for row in result:
                print(f" - {row.message} (Owner: {row.user_id})")
                
            if len(result) == 0:
                print("\nSUCCESS: User 2 sees NO data (RLS is working).")
            else:
                # Check if User 2 sees User 1's data
                leakage = any(str(row.user_id) == str(user1_id) for row in result)
                if leakage:
                    print("\nFAILURE: User 2 sees User 1's data! RLS LEAKAGE DETECTED.")
                else:
                    print("\nSUCCESS: User 2 only sees their own data (if any).")

if __name__ == "__main__":
    verify_rls_enforcement()
