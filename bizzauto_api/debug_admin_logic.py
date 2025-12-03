import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql_models import User
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# User ID from the logs
user_id = "cb946aeb-1aae-4c27-9567-17a6dba33bde"

try:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Role: '{user.role}'") # Quotes to see whitespace
        
        if user.role == "admin":
            print("Logic Check: user.role == 'admin' is TRUE")
        else:
            print("Logic Check: user.role == 'admin' is FALSE")
            
    else:
        print("User not found")
finally:
    db.close()
