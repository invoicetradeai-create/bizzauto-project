import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path to import database modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables FIRST
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
# Ensure SUPABASE_KEY is set for database.py (it uses this name for the anon key usually, but here we might need to mock it or set it if missing)
# Ensure SUPABASE_KEY is set for database.py (it uses this name for the anon key usually, but here we might need to mock it or set it if missing)
if not os.getenv("SUPABASE_KEY"):
    # If SUPABASE_KEY is missing, database.py might fail. 
    # Let's try to set it to something or ensure it's loaded.
    os.environ["SUPABASE_KEY"] = "dummy_key_to_bypass_database_py_check"

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
    sys.exit(1)

# Add parent directory to path to import database modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from sql_models import User

# Initialize Supabase Admin Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def backfill_metadata():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Found {len(users)} users in database.")

        for user in users:
            if not user.email:
                print(f"Skipping user {user.id}: No email")
                continue
            
            if not user.company_id:
                print(f"Skipping user {user.email}: No company_id")
                continue

            print(f"Updating user {user.email} with company_id: {user.company_id}")
            
            try:
                # We need the Auth User ID (which matches our DB ID because we sync them)
                # Assuming user.id in our DB is the same as Supabase Auth ID
                auth_user_id = str(user.id)
                
                # Update user_metadata
                response = supabase.auth.admin.update_user_by_id(
                    auth_user_id,
                    {"user_metadata": {"company_id": str(user.company_id)}}
                )
                print(f"✅ Successfully updated {user.email}")
                
            except Exception as e:
                print(f"❌ Failed to update {user.email}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    backfill_metadata()
