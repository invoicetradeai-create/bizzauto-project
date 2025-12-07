import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import DATABASE_URL

load_dotenv()

def enable_rls():
    if not DATABASE_URL:
        print("DATABASE_URL not set")
        return

    engine = create_engine(DATABASE_URL)
    
    tables = [
        "products", "clients", "suppliers", "invoices", "invoice_items", 
        "purchases", "purchase_items", "expenses", "leads", "whatsapp_logs", 
        "scheduled_whatsapp_messages", "uploaded_docs", "accounts", "journal_entries"
    ]

    for table in tables:
        print(f"Enabling RLS on {table}...")
        with engine.connect() as connection:
            with connection.begin(): # Start a transaction per table
                try:
                    # Enable RLS
                    connection.execute(text(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;"))
                    connection.execute(text(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;"))
                    
                    
                    # Drop existing policy if any
                    connection.execute(text(f"DROP POLICY IF EXISTS user_isolation_policy ON {table};"))
                    
                    # Create Policy using standard auth.uid()
                    if table == "scheduled_whatsapp_messages":
                         policy_sql = f"""
                        CREATE POLICY user_isolation_policy ON {table}
                        USING (true)
                        WITH CHECK (true);
                        """
                    else:
                        policy_sql = f"""
                        CREATE POLICY user_isolation_policy ON {table}
                        USING (user_id = auth.uid())
                        WITH CHECK (user_id = auth.uid());
                        """
                    connection.execute(text(policy_sql))
                    print(f"Successfully enabled RLS and created policy on {table}")
                    
                except Exception as e:
                    print(f"Error enabling RLS on {table}: {e}")

if __name__ == "__main__":
    enable_rls()
