import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sql_models import User
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# User Email
user_email = "hayashakil@gmail.com"

try:
    user = db.query(User).filter(User.email == user_email).first()
    if user:
        print(f"Updating role for {user.email}...")
        user.role = "user"
        db.commit()
        print("Role updated to 'user'")
    else:
        print(f"User with email {user_email} not found")
finally:
    db.close()
