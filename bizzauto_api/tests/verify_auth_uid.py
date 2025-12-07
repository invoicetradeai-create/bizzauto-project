import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DATABASE_URL

load_dotenv()

def verify_auth_uid():
    if not DATABASE_URL:
        print("DATABASE_URL not set")
        return

    engine = create_engine(DATABASE_URL)
    
    # Test UUID
    test_uuid = "00000000-0000-0000-0000-000000000000"
    
    with engine.connect() as connection:
        try:
            # 1. Try to select auth.uid() without setting anything
            print("1. Testing auth.uid() without context...")
            result = connection.execute(text("SELECT auth.uid()")).scalar()
            print(f"   Result: {result}")
            
            # 2. Set request.jwt.claims and try again
            print("\n2. Setting request.jwt.claims and testing auth.uid()...")
            claims = json.dumps({"sub": test_uuid})
            connection.execute(text(f"SET request.jwt.claims = '{claims}'"))
            
            result = connection.execute(text("SELECT auth.uid()")).scalar()
            print(f"   Result: {result}")
            
            if str(result) == test_uuid:
                print("\nSUCCESS: auth.uid() correctly resolved from request.jwt.claims")
            else:
                print("\nFAILURE: auth.uid() did not resolve correctly")
                
        except Exception as e:
            print(f"\nError: {e}")
            print("It is possible that auth.uid() function does not exist or has a different definition.")

if __name__ == "__main__":
    verify_auth_uid()
