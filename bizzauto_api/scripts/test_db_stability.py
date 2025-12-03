import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from sqlalchemy import text
import time

def test_connection():
    print("Testing database connection stability...")
    db = SessionLocal()
    try:
        # 1. Simple query
        result = db.execute(text("SELECT 1")).scalar()
        print(f"✅ Initial query successful: {result}")
        
        # 2. Simulate idle time (short)
        print("Sleeping for 2 seconds to simulate idle time...")
        time.sleep(2)
        
        # 3. Query again to test pool_pre_ping
        result = db.execute(text("SELECT 1")).scalar()
        print(f"✅ Post-idle query successful: {result}")
        
        print("🎉 Database connection is stable!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()
