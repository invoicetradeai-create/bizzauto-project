import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DATABASE_URL

load_dotenv()

def check_policies():
    if not DATABASE_URL:
        print("DATABASE_URL not set")
        return

    engine = create_engine(DATABASE_URL)
    
    table_name = "invoices"
    
    with engine.connect() as connection:
        sql = text(f"SELECT policyname, cmd, qual, with_check FROM pg_policies WHERE tablename = '{table_name}'")
        result = connection.execute(sql)
        
        print(f"Policies for {table_name}:")
        for row in result:
            print(f"Name: {row.policyname}")
            print(f"Command: {row.cmd}")
            print(f"Using (qual): {row.qual}")
            print(f"With Check: {row.with_check}")
            print("-" * 20)

if __name__ == "__main__":
    check_policies()
