from dotenv import load_dotenv
import sys
import os

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

from database import engine
import sql_models
import logging

app = FastAPI()

# ✅ Frontend URLs allowed during development
origins = [
    "http://localhost:3000",  # for Next.js frontend
    "http://localhost:5173",  # for Vite React frontend
]

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],            # allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],            # allow all headers (esp. Authorization)
)

# ✅ Create database tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        sql_models.Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Database initialization failed: {str(e)}")

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