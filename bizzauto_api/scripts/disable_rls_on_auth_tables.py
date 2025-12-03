import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DATABASE_URL

load_dotenv()

def disable_rls_auth_tables():
    if not DATABASE_URL:
        print("DATABASE_URL not set")
        return

    engine = create_engine(DATABASE_URL)
    
    tables = ["companies", "users"]

    for table in tables:
        print(f"Disabling RLS on {table}...")
        with engine.connect() as connection:
            with connection.begin():
                try:
                    connection.execute(text(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;"))
                    print(f"Successfully disabled RLS on {table}")
                except Exception as e:
                    print(f"Error disabling RLS on {table}: {e}")

if __name__ == "__main__":
    disable_rls_auth_tables()
