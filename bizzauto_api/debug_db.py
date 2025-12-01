import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {db_url.split('@')[1] if db_url and '@' in db_url else 'Not Set or Invalid Format'}")

try:
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Check row count
    result = session.execute(text("SELECT count(*) FROM scheduled_whatsapp_messages"))
    count = result.scalar()
    print(f"Total rows in scheduled_whatsapp_messages: {count}")

    # Check rows
    result = session.execute(text("SELECT id, phone, scheduled_at, status, company_id FROM scheduled_whatsapp_messages"))
    rows = result.fetchall()
    for row in rows:
        print(f" - {row}")

    # Check RLS settings (Postgres specific)
    try:
        result = session.execute(text("SELECT relname, relrowsecurity FROM pg_class WHERE relname = 'scheduled_whatsapp_messages'"))
        rls = result.fetchone()
        if rls:
            print(f"RLS Enabled on table: {rls[1]}")
    except Exception as e:
        print(f"Could not check RLS: {e}")

    session.close()

    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {'Found' if service_key else 'Not Found'}")
except Exception as e:
    print(f"Error connecting to DB: {e}")
