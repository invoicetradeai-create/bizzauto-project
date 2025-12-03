import sys
import os
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DATABASE_URL
from sql_models import User, Product, Company

load_dotenv()

def test_rls():
    if not DATABASE_URL:
        print("DATABASE_URL not set")
        return

    # 1. Connect as Superuser to setup test user
    admin_engine = create_engine(DATABASE_URL)
    
    test_user = "test_rls_user"
    test_pass = "test_rls_pass"
    
    print("Setting up test user...")
    with admin_engine.connect() as conn:
        conn.execute(text("COMMIT")) # Cannot run CREATE ROLE inside transaction block
        try:
            conn.execute(text(f"DROP ROLE IF EXISTS {test_user}"))
            conn.execute(text(f"CREATE ROLE {test_user} WITH LOGIN PASSWORD '{test_pass}' NOBYPASSRLS"))
            conn.execute(text(f"GRANT CONNECT ON DATABASE postgres TO {test_user}")) # Assuming db name is postgres or from URL
            conn.execute(text(f"GRANT USAGE ON SCHEMA public TO {test_user}"))
            conn.execute(text(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {test_user}"))
            conn.execute(text(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {test_user}"))
            print(f"Created role {test_user}")
        except Exception as e:
            print(f"Error creating role: {e}")
            # Proceeding, maybe it exists

    # 3. Create a Company using Admin connection (to bypass RLS)
    print("Creating company as admin...")
    company_id = uuid.uuid4()
    with admin_engine.connect() as conn:
        conn.execute(text("INSERT INTO companies (id, name, email) VALUES (:id, 'Test Company RLS', 'testrls_user@example.com')"), {"id": company_id})
        conn.commit()
        print(f"Created Company: {company_id}")

    # 4. Create User 1 and User 2 using Admin connection
    print("Creating users as admin...")
    user1_id = uuid.uuid4()
    user2_id = uuid.uuid4()
    
    with admin_engine.connect() as conn:
        conn.execute(text("INSERT INTO users (id, full_name, email, role, company_id) VALUES (:id, 'User One', 'user1_rls@example.com', 'user', :company_id)"), {"id": user1_id, "company_id": company_id})
        conn.execute(text("INSERT INTO users (id, full_name, email, role, company_id) VALUES (:id, 'User Two', 'user2_rls@example.com', 'user', :company_id)"), {"id": user2_id, "company_id": company_id})
        conn.commit()
        print(f"Created User1: {user1_id}")
        print(f"Created User2: {user2_id}")

    # 2. Construct new connection URL
    url = make_url(DATABASE_URL)
    test_db_url = url.set(username=test_user, password=test_pass)
    
    print(f"Connecting as {test_user}...")
    engine = create_engine(test_db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 5. Create Product for User 1
        # Products table HAS RLS.
        # We need to set context.
        
        import json
        
        print("Setting context for User 1...")
        claims1 = json.dumps({"sub": str(user1_id)})
        session.execute(text("SET request.jwt.claims = :claims"), {"claims": claims1})
        session.execute(text("SET ROLE authenticated"))
        
        # Use ORM but with the IDs we created
        product1 = Product(name="User1 Product", company_id=company_id, user_id=user1_id)
        session.add(product1)
        session.commit()
        print(f"Created Product for User 1: {product1.id}")

        # 6. Verify User 1 can see it
        products_u1 = session.query(Product).all()
        print(f"User 1 sees {len(products_u1)} products")
        assert len(products_u1) == 1
        assert products_u1[0].id == product1.id

        # 7. Switch to User 2
        print("Switching context to User 2...")
        claims2 = json.dumps({"sub": str(user2_id)})
        session.execute(text("SET request.jwt.claims = :claims"), {"claims": claims2})
        session.execute(text("SET ROLE authenticated"))
        
        # 8. Verify User 2 sees NOTHING
        products_u2 = session.query(Product).all()
        print(f"User 2 sees {len(products_u2)} products")
        assert len(products_u2) == 0
        
        print("RLS Verification Successful with non-superuser!")

    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()
        # Cleanup user
        with admin_engine.connect() as conn:
             conn.execute(text("COMMIT"))
             # conn.execute(text(f"DROP ROLE IF EXISTS {test_user}")) # Keep it for debugging or manual cleanup if needed
             pass

if __name__ == "__main__":
    test_rls()
