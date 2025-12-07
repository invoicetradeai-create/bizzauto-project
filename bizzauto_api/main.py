from dotenv import load_dotenv
import sys
import os
import json
import time

# ✅ Load environment variables from .env file FIRST
load_dotenv()

from google.oauth2 import service_account
from google.cloud import vision
from fastapi import FastAPI , Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
import google.generativeai as genai
from pydantic import BaseModel
import threading


# Add the directory containing main.py to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Routers
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
import routers.api.contact as contact
import routers.admin as admin
import routers.api.invoice_processing as invoice_processing

from database import engine, get_db, TestingSessionLocal, test_engine
import sql_models

app = FastAPI()

# ✅ Frontend URLs allowed during development
origins = [
    "http://localhost:3000",
    "https://bizzauto-project.onrender.com",
    "https://www.bizzauto.com",
]

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ✅ Include invoice processing router
app.include_router(
    invoice_processing.router,
    prefix="/api/invoice-processing",
    tags=["Invoice Processing"]
)
# ✅ Create database tables on startup
@app.on_event("startup")
async def startup_event():
    # Check if running in test environment
    if os.getenv("TESTING") == "True":
        sql_models.Base.metadata.drop_all(bind=test_engine)
        sql_models.Base.metadata.create_all(bind=test_engine)
        logging.info("✅ Test database tables created successfully")
    else:
        # Gracefully handle database table creation
        try:
            if engine is not None:
                sql_models.Base.metadata.create_all(bind=engine)
                logging.info("✅ Database tables created successfully")
            else:
                logging.warning("⚠️ Database engine not available - skipping table creation")
        except Exception as e:
            logging.error(f"❌ Database initialization failed: {str(e)}")

    # Google Cloud Vision API Credentials Initialization
    try:
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            logging.info("✅ Using GOOGLE_APPLICATION_CREDENTIALS from environment.")
        else:
            creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
            if not creds_json:
                logging.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS_JSON not set. OCR features will not work.")
            else:
                creds_dict = json.loads(creds_json)
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
                # Use a temporary file path that works in most environments
                with open("/tmp/gcp_creds.json", "w") as f:
                    json.dump(creds_dict, f)
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/gcp_creds.json"
                logging.info("✅ Google Cloud Vision API credentials configured")
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error configuring Google Cloud Vision API: {e}")

    # Gemini API Key Configuration
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            logging.info("✅ Gemini API key configured.")
        else:
            logging.warning("⚠️ GEMINI_API_KEY environment variable not set.")
    except KeyError:
        # This case is unlikely with .get(), but good practice
        logging.error("❌ Error configuring Gemini: GEMINI_API_KEY not found.")


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
# app.include_router(invoices.router, prefix="/api/invoices", tags=["invoices"]) # Replaced by invoice_processing
app.include_router(invoice_items.router, prefix="/api/invoice_items", tags=["invoice_items"])
app.include_router(purchases.router, prefix="/api/purchases", tags=["purchases"])
app.include_router(purchase_items.router, prefix="/api/purchase_items", tags=["purchase_items"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["expenses"])
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(whatsapp_logs.router, prefix="/api/whatsapp_logs", tags=["whatsapp_logs"])
app.include_router(uploaded_docs.router, prefix="/api/uploaded_docs", tags=["uploaded_docs"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(meta_whatsapp.router, prefix="/api/meta_whatsapp", tags=["whatsapp"])
# app.include_router(ocr.router, prefix="/api/ocr", tags=["ocr"]) # Removed: Functionality replaced by invoice_processing
app.include_router(scheduled_messages.router, prefix="/api", tags=["scheduled_messages"])
app.include_router(inventory.router, prefix="/api", tags=["inventory"])
app.include_router(accounting.router, prefix="/api/accounting", tags=["accounting"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(contact.router, prefix="/api/contact", tags=["contact"])
app.include_router(invoice_processing.router, prefix="/api/invoice-processing", tags=["invoice-processing"])

# ✅ Root endpoint
@app.get("/")
def read_root():
    return {"message": "BizzAuto API", "version": "1.0.0", "status": "running"}

# ✅ Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is healthy", "version": "1.0.0"}

# Pydantic model for Gemini
class GeminiPrompt(BaseModel):
    prompt: str

gemini_model = genai.GenerativeModel('gemini-2.0-flash')

@app.post("/gemini-generate")
async def generate_with_gemini(prompt: GeminiPrompt):
    try:
        response = gemini_model.generate_content(prompt.prompt)
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Default to port 8000 as requested
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port, reload=False, log_level="debug")
