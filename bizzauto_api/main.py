from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import dashboard, tables
from routers.api import (
    companies, clients, users, suppliers, products, invoices,
    invoice_items, purchases, purchase_items, expenses, leads,
    whatsapp_logs, uploaded_docs, settings, meta_whatsapp
)
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
app.include_router(meta_whatsapp.router, prefix="/api", tags=["meta_whatsapp"])

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
