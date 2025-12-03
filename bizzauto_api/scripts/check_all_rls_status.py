import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DATABASE_URL

load_dotenv()

def check_all_rls_status():
    if not DATABASE_URL:
        print("DATABASE_URL not set")
        return

    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        sql = """
        SELECT relname, relrowsecurity 
        FROM pg_class 
        JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
        WHERE pg_namespace.nspname = 'public' AND relkind = 'r';
        """
        result = connection.execute(text(sql))
        
        print(f"{'Table Name':<30} | {'RLS Enabled':<10}")
        print("-" * 45)
        for row in result:
            print(f"{row.relname:<30} | {str(row.relrowsecurity):<10}")

if __name__ == "__main__":
    check_all_rls_status()
