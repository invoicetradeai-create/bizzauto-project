from fastapi import Header, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from sql_models import User
from uuid import UUID
import os
from jose import jwt, JWTError

# Load JWT Secret
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
ALGORITHM = "HS256"

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    
    try:
    # Verify JWT
        # print(f"DEBUG: Verifying token: {token[:10]}...")
        # print(f"DEBUG: Secret: {SUPABASE_JWT_SECRET[:5]}...")
        
        if not SUPABASE_JWT_SECRET:
            print("CRITICAL: SUPABASE_JWT_SECRET is not set in environment variables.")
            raise HTTPException(status_code=500, detail="Server misconfiguration: Missing JWT Secret")

        payload = jwt.decode(token, str(SUPABASE_JWT_SECRET), algorithms=[ALGORITHM], options={"verify_aud": False})
        print(f"DEBUG: JWT Payload: {payload}")
        
        # Extract user_id and company_id
        user_id = payload.get("sub")
        user_metadata = payload.get("user_metadata", {})
        company_id = user_metadata.get("company_id")
        
        if not user_id:
            print("DEBUG: Missing user_id in payload")
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
            
        # Optional: Verify user exists in DB (adds latency but ensures consistency)
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        if not user:
            print(f"DEBUG: User {user_id} not found in DB")
            raise HTTPException(status_code=404, detail="User not found")
            
        # Ensure company_id matches (Optional double check)
        if company_id and str(user.company_id) != company_id:
             print(f"DEBUG: Company ID mismatch. Token: {company_id}, DB: {user.company_id}")
             # In a strict scenario, we might raise an error, but for now let's trust the DB or the Token.
             # Ideally, we trust the token for RLS, but here we return the DB user object.
             pass

        return user

    except JWTError as e:
        print(f"DEBUG: JWT Error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Could not validate credentials: {str(e)}")
    except Exception as e:
        print(f"DEBUG: General Auth Error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

def get_current_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return user

def set_rls_context(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Set the RLS context using Supabase's standard request.jwt.claims
    # This allows auth.uid() to work in RLS policies
    import json
    from sqlalchemy import text
    
    # Construct claims object with 'sub' (subject) only
    # We remove 'company_id' to disable the permissive 'Tenant isolation' policy
    # and enforce strict 'User isolation' via user_isolation_policy.
    claims = json.dumps({
        "sub": str(user.id)
    })
    
    # Set the claims for auth.uid() and auth.jwt()
    db.execute(text("SET request.jwt.claims = :claims"), {"claims": claims})
    
    # Set app.current_user_id for legacy policy support (since we couldn't update policies)
    db.execute(text("SET app.current_user_id = :user_id"), {"user_id": str(user.id)})
    
    return db
