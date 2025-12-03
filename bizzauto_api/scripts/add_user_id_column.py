import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Add parent directory to path to import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DATABASE_URL

load_dotenv()

def add_user_id_columns():
    if not DATABASE_URL:
        print("DATABASE_URL not set")
        return

    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    tables_to_update = [
        "products", "clients", "suppliers", "invoices", "invoice_items", 
        "purchases", "purchase_items", "expenses", "leads", "whatsapp_logs", 
        "scheduled_whatsapp_messages", "uploaded_docs", "accounts", "journal_entries"
    ]

    with engine.connect() as connection:
        for table in tables_to_update:
            columns = [col['name'] for col in inspector.get_columns(table)]
            if "user_id" not in columns:
                print(f"Adding user_id to {table}...")
                try:
                    # We use text() for raw SQL execution
                    # Note: We are adding a nullable column first. 
                    # If existing data needs to be backfilled, that's a separate step.
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN user_id UUID REFERENCES users(id);"))
                    print(f"Successfully added user_id to {table}")
                except Exception as e:
                    print(f"Error adding user_id to {table}: {e}")
            else:
                print(f"user_id already exists in {table}")
        
        connection.commit()

if __name__ == "__main__":
    add_user_id_columns()
