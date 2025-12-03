import os
import sys
import asyncio
from uuid import UUID
from dotenv import load_dotenv
from supabase import create_client, Client
from sqlalchemy.orm import Session

# Add parent directory to path to import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from sql_models import User, Company
from crud import create_user, create_company
from models import User as PydanticUser, Company as PydanticCompany

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials not found in .env")
    print("Please ensure NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY are set.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def create_admin_user():
    print("\n--- Create Super Admin User ---\n")
    email = input("Enter Email: ").strip()
    password = input("Enter Password (min 6 chars): ").strip()
    full_name = input("Enter Full Name: ").strip()
    
    if len(password) < 6:
        print("Error: Password must be at least 6 characters.")
        return

    print("\n1. Creating user in Supabase Auth...")
    try:
        # Sign up in Supabase
        res = supabase.auth.sign_up({
            "email": email, 
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "role": "admin"
                }
            }
        })
        
        if not res.user:
            print("Error: Failed to create user in Supabase (User object is None).")
            if res.session is None: 
                # Sometimes sign_up returns None session if email confirmation is required
                # But usually user object is present. 
                # If user already exists, it might not throw but return existing? 
                # Actually supabase-py throws GotrueError usually.
                pass
            return

        user_id = res.user.id
        print(f"✅ Supabase User Created! ID: {user_id}")
        
    except Exception as e:
        print(f"Error creating Supabase user: {e}")
        print("If the user already exists, please copy their ID from Supabase dashboard and enter it below.")
        user_id_input = input("Enter existing Supabase User ID (or press Enter to abort): ").strip()
        if not user_id_input:
            return
        user_id = user_id_input

    print("\n2. Creating user in Local Database...")
    db = SessionLocal()
    try:
        # Check if company exists, if not create a default one
        company = db.query(Company).first()
        if not company:
            print("No company found. Creating default 'Admin Company'...")
            company_data = PydanticCompany(name="Admin Company", email=email)
            company = create_company(db, company_data)
            print(f"✅ Created Company: {company.id}")

        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User {email} already exists in local DB. Updating role to 'admin'...")
            existing_user.role = "admin"
            existing_user.id = UUID(user_id) # Ensure ID matches Supabase
            db.commit()
            print("✅ User updated successfully.")
        else:
            new_user = PydanticUser(
                id=UUID(user_id),
                company_id=company.id,
                full_name=full_name,
                email=email,
                role="admin",
                status="active"
            )
            create_user(db, new_user)
            print("✅ Admin User created successfully in local DB.")

    except Exception as e:
        print(f"Error updating local DB: {e}")
    finally:
        db.close()

    print("\n-----------------------------------")
    print("Done! You can now log in at http://localhost:3000/signin")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
