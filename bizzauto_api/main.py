from dotenv import load_dotenv
import sys
import os
import json # Added for JSON parsing
from google.oauth2 import service_account # Added for service account credentials
from google.cloud import vision # Added for Vision API client initialization

# Add the directory containing main.py (which is bizzauto_api) to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv() # Load environment variables from .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import routers.dashboard as dashboard
import routers.tables as tables
import routers.api.companies as companies
import routers.api.clients as clients
import routers.api.users as users
import routers.api.suppliers as suppliers
import routers.api.products as products
import routers.api.invoices as invoices
import routers.api.invoice_items as invoice_items
import routers.api.purchases as purchases
import routers.api.purchase_items as purchase_items
import routers.api.expenses as expenses
import routers.api.leads as leads
import routers.api.whatsapp_logs as whatsapp_logs
import routers.api.uploaded_docs as uploaded_docs
import routers.api.settings as settings
import routers.api.meta_whatsapp as meta_whatsapp
import routers.api.ocr as ocr
import routers.api.scheduled_messages as scheduled_messages
import routers.api.inventory as inventory
import routers.api.accounting as accounting

from database import engine, get_db, TestingSessionLocal, test_engine
import sql_models
import logging
from redis import Redis
import google.generativeai as genai
from pydantic import BaseModel


app = FastAPI()

# ✅ Frontend URLs allowed during development
origins = [
    "*",
]

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],            # allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],            # allow all headers (esp. Authorization)
)

# ✅ Create database tables on startup
@app.on_event("startup")
async def startup_event():
    # Check if running in test environment
    if os.getenv("TESTING") == "True":
        sql_models.Base.metadata.drop_all(bind=test_engine) # Need to import test_engine from database
        sql_models.Base.metadata.create_all(bind=test_engine) # Need to import test_engine from database
        logging.info("Test database tables created successfully")
    else:
        try:
            sql_models.Base.metadata.create_all(bind=engine)
            logging.info("Database tables created successfully")
        except Exception as e:
            logging.error(f"Database initialization failed: {str(e)}")

    # Google Cloud Vision API Credentials Initialization
    try:
        creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if not creds_json:
            raise ValueError("Env var GOOGLE_APPLICATION_CREDENTIALS_JSON is not set")

        # Convert JSON string to Python dict
        creds_dict = json.loads(creds_json)

        # Fix private_key line breaks
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

        # Write to temp file
        with open("/tmp/sa.json", "w") as f:
            json.dump(creds_dict, f)

        # Set GOOGLE_APPLICATION_CREDENTIALS
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/sa.json"
        logging.info("Google Cloud Vision API credentials configured from environment variable.")
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        logging.error(f"Error configuring Google Cloud Vision API credentials: {e}")

    REDIS_URL = os.getenv("REDIS_URL")
    if REDIS_URL:
        app.state.redis = Redis.from_url(REDIS_URL) # Initialize Redis client
        logging.info("Redis client initialized.")
    else:
        logging.warning("REDIS_URL not set. Redis client not initialized.")

    # Gemini API Key Configuration
    # Make sure to set the GEMINI_API_KEY environment variable in your .env file
    # or directly in your environment.
    try:
        api_key = os.environ["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        logging.info("Gemini API key configured.")
    except KeyError:
        logging.error("GEMINI_API_KEY environment variable not set.")

# Dependency override for testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Include all routers
app.include_router(dashboard.router, prefix="/dashboard")
app.include_router(tables.router, prefix="/tables")
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["suppliers"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(invoices.router, prefix="/api/invoices", tags=["invoices"])
app.include_router(invoice_items.router, prefix="/api/invoice_items", tags=["invoice_items"])
app.include_router(purchases.router, prefix="/api/purchases", tags=["purchases"])
app.include_router(purchase_items.router, prefix="/api/purchase_items", tags=["purchase_items"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(whatsapp_logs.router, prefix="/api/whatsapp_logs", tags=["whatsapp_logs"])
app.include_router(uploaded_docs.router, prefix="/api/uploaded_docs", tags=["uploaded_docs"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(
    meta_whatsapp.router,
    prefix="/api/meta_whatsapp",
    tags=["whatsapp"]
)
app.include_router(ocr.router, prefix="/api/ocr", tags=["ocr"])
app.include_router(scheduled_messages.router, prefix="/api", tags=["scheduled_messages"])
app.include_router(inventory.router, prefix="/api", tags=["inventory"])
app.include_router(accounting.router, prefix="/api/accounting", tags=["accounting"])

# ✅ Root endpoint (for testing)
@app.get("/")
def read_root():
    return {
        "message": "BizzAuto API",
        "version": "1.0.0",
        "status": "running"
    }

# ✅ Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "API is healthy",
        "version": "1.0.0"
    }

# Pydantic model for the request body
class GeminiPrompt(BaseModel):
    prompt: str

# Gemini model initialization
# You can choose other models like 'gemini-pro-vision', 'gemini-1.0-pro', etc.
gemini_model = genai.GenerativeModel('gemini-pro')

@app.post("/gemini-generate")
async def generate_with_gemini(prompt: GeminiPrompt):
    """
    Receives a prompt and returns a response generated by Gemini.
    """
    try:
        response = gemini_model.generate_content(prompt.prompt)
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # app is already defined globally
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False, log_level="debug")