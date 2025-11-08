from pydantic import BaseModel, Json
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date

class Company(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class Client(BaseModel):
    company_id: UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class User(BaseModel):
    company_id: UUID
    full_name: str
    email: str
    password_hash: str
    role: str
    status: Optional[str] = 'active'

class Supplier(BaseModel):
    company_id: UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class Product(BaseModel):
    company_id: UUID
    name: str
    sku: Optional[str] = None
    category: Optional[str] = None
    purchase_price: float = 0
    sale_price: float = 0
    stock_quantity: int = 0
    low_stock_alert: Optional[int] = 5
    unit: Optional[str] = None

class Invoice(BaseModel):
    company_id: UUID
    client_id: Optional[UUID] = None
    invoice_date: date = date.today()
    total_amount: float = 0
    payment_status: Optional[str] = 'unpaid'
    notes: Optional[str] = None

class InvoiceItem(BaseModel):
    invoice_id: UUID
    product_id: UUID
    quantity: int = 1
    price: float = 0
    total: float = 0

class Purchase(BaseModel):
    company_id: UUID
    supplier_id: Optional[UUID] = None
    purchase_date: date = date.today()
    total_amount: float = 0
    notes: Optional[str] = None

class PurchaseItem(BaseModel):
    purchase_id: UUID
    product_id: UUID
    quantity: int = 1
    price: float = 0
    total: float = 0

class Expense(BaseModel):
    company_id: UUID
    title: str
    category: Optional[str] = None
    amount: float = 0
    expense_date: date = date.today()
    notes: Optional[str] = None

class Lead(BaseModel):
    company_id: UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = 'new'

class WhatsappLog(BaseModel):
    company_id: UUID
    message_type: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[str] = None
    status: Optional[str] = 'sent'

class UploadedDoc(BaseModel):
    company_id: UUID
    file_name: str
    file_url: str

class Setting(BaseModel):
    user_id: UUID
    key: str
    value: Json
