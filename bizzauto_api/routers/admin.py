from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from uuid import UUID

from database import get_db
from dependencies import get_current_admin
from models import User as PydanticUser, Company as PydanticCompany
from sql_models import User, Company, Invoice, WhatsappLog, ScheduledWhatsappMessage, Purchase

router = APIRouter()

# --- Tenant Management ---
@router.get("/tenants", response_model=List[PydanticCompany])
def get_all_tenants(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    admin: PydanticUser = Depends(get_current_admin)
):
    return db.query(Company).offset(skip).limit(limit).all()

@router.get("/users", response_model=List[PydanticUser])
def get_all_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    admin: PydanticUser = Depends(get_current_admin)
):
    return db.query(User).offset(skip).limit(limit).all()

@router.post("/users/{user_id}/suspend")
def suspend_user(
    user_id: UUID, 
    db: Session = Depends(get_db),
    admin: PydanticUser = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = "suspended"
    db.commit()
    return {"message": f"User {user.email} suspended"}

@router.post("/users/{user_id}/activate")
def activate_user(
    user_id: UUID, 
    db: Session = Depends(get_db),
    admin: PydanticUser = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = "active"
    db.commit()
    return {"message": f"User {user.email} activated"}

# --- Analytics & Usage ---
@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
    admin: PydanticUser = Depends(get_current_admin)
):
    total_users = db.query(User).count()
    total_companies = db.query(Company).count()
    total_revenue = db.query(func.sum(Invoice.total_amount)).scalar() or 0
    active_users = db.query(User).filter(User.status == 'active').count()
    
    # Revenue Trend (Last 6 months)
    # Generate last 6 months keys in order
    from datetime import datetime, timedelta
    revenue_trend = {}
    current_date = datetime.now()
    
    # Initialize with 0 for the last 6 months
    months_order = []
    for i in range(5, -1, -1):
        month_date = current_date - timedelta(days=i*30)
        month_key = month_date.strftime("%b") # e.g., Jul, Aug
        revenue_trend[month_key] = 0
        months_order.append(month_key)

    # Fetch invoices and aggregate
    # Ideally filter by date in SQL: .filter(Invoice.invoice_date >= six_months_ago)
    invoices = db.query(Invoice).all()
    for invoice in invoices:
        if invoice.invoice_date:
            month = invoice.invoice_date.strftime("%b")
            # Only add if it's in our target window (simple check)
            if month in revenue_trend:
                revenue_trend[month] += invoice.total_amount
    
    # Create list in chronological order
    revenue_trend_list = [{"name": m, "value": revenue_trend[m]} for m in months_order]

    # User Growth (Last 6 months)
    users = db.query(User).all()
    user_growth = {}
    
    # Initialize last 6 months with 0
    from datetime import datetime, timedelta
    current_date = datetime.now()
    for i in range(5, -1, -1):
        month_date = current_date - timedelta(days=i*30)
        month_name = month_date.strftime("%b")
        user_growth[month_name] = 0

    for user in users:
        if user.created_at:
            month = user.created_at.strftime("%b")
            if month in user_growth:
                user_growth[month] += 1
            
    user_growth_list = [{"name": m, "value": v} for m, v in user_growth.items()] 

    return {
        "total_users": total_users,
        "total_companies": total_companies,
        "total_revenue": total_revenue,
        "active_users": active_users,
        "revenue_trend": revenue_trend_list,
        "user_growth": user_growth_list
    }

@router.get("/whatsapp-stats")
def get_whatsapp_stats(
    db: Session = Depends(get_db),
    admin: PydanticUser = Depends(get_current_admin)
):
    total_sent = db.query(WhatsappLog).filter(WhatsappLog.status.in_(['sent', 'delivered', 'read'])).count()
    total_failed = db.query(WhatsappLog).filter(WhatsappLog.status == 'failed').count()
    scheduled_pending = db.query(ScheduledWhatsappMessage).filter(ScheduledWhatsappMessage.status == 'pending').count()
    
    return {
        "total_sent": total_sent,
        "total_failed": total_failed,
        "scheduled_pending": scheduled_pending
    }

# --- Billing (Mock for now as Transaction model not fully defined in prompt, using Invoices as proxy) ---
@router.get("/billing")
def get_billing_history(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    admin: PydanticUser = Depends(get_current_admin)
):
    # Assuming Invoices represent billing for now, or we can add a Transaction model later
    # Returning recent invoices across all companies
    return db.query(Invoice).order_by(Invoice.invoice_date.desc()).offset(skip).limit(limit).all()
