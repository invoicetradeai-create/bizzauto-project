from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud import get_invoices, get_clients, get_products, get_whatsapp_logs
from datetime import datetime

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    invoices = get_invoices(db, skip=0, limit=1000)
    clients = get_clients(db, skip=0, limit=1000)
    products = get_products(db, skip=0, limit=1000)
    whatsapp_logs = get_whatsapp_logs(db, skip=0, limit=1000)

    total_revenue = sum(i.total_amount for i in invoices if i.payment_status == 'paid')
    pending_payments = sum(i.total_amount for i in invoices if i.payment_status != 'paid')
    active_clients = len(clients)
    low_stock_items = sum(1 for p in products if p.stock_quantity < p.low_stock_alert)
    messages_sent = len(whatsapp_logs)

    revenue_trend = {}
    for invoice in invoices:
        month = invoice.invoice_date.strftime("%b")
        if month not in revenue_trend:
            revenue_trend[month] = 0
        revenue_trend[month] += invoice.total_amount

    revenue_trend_list = [{"month": m, "value": v} for m, v in revenue_trend.items()]

    payment_status = {}
    for invoice in invoices:
        status = invoice.payment_status
        if status not in payment_status:
            payment_status[status] = 0
        payment_status[status] += 1
        
    payment_status_list = [{"name": s, "value": v} for s, v in payment_status.items()]

    return {
        "stats": {
            "total_revenue": total_revenue,
            "pending_payments": pending_payments,
            "active_clients": active_clients,
            "low_stock_items": low_stock_items,
            "messages_sent": messages_sent,
        },
        "revenue_trend": revenue_trend_list,
        "payment_status": payment_status_list,
    }
