import sys
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DATABASE_URL
from sql_models import User, Product, Company
from crud import create_product
from models import Product as PydanticProduct

load_dotenv()

def verify_population():
    if not DATABASE_URL:
        print("DATABASE_URL not set")
        return

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create dummy data
        company = Company(name="Test Pop Company", email=f"testpop_{uuid.uuid4()}@example.com")
        session.add(company)
        session.commit()
        
        user = User(full_name="Test Pop User", email=f"testpop_{uuid.uuid4()}@example.com", role="user", company_id=company.id)
        session.add(user)
        session.commit()
        
        # Test create_product
        p_data = PydanticProduct(name="Test Pop Product", company_id=company.id)
        # We call create_product passing user_id
        db_product = create_product(db=session, product=p_data, user_id=user.id)
        
        print(f"Created product: {db_product.id}")
        print(f"Product user_id: {db_product.user_id}")
        
        if db_product.user_id == user.id:
            print("SUCCESS: user_id is correctly populated.")
        else:
            print(f"FAILURE: user_id mismatch. Expected {user.id}, got {db_product.user_id}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_population()
