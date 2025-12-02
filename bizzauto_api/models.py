from pydantic import BaseModel, Json, ConfigDict, field_serializer, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime, date
import json

class Company(BaseModel):
    id: Optional[UUID] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class Client(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    full_name: str
    email: str
    password_hash: Optional[str] = None
    role: str
    business_name: Optional[str] = None
    location: Optional[str] = None
    contact_number: Optional[str] = None
    status: Optional[str] = 'active'

    model_config = ConfigDict(from_attributes=True)

class Supplier(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class Product(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    name: str
    sku: Optional[str] = None
    category: Optional[str] = None
    purchase_price: float = 0
    sale_price: float = 0
    stock_quantity: int = 0
    low_stock_alert: Optional[int] = 5
    unit: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class InvoiceItem(BaseModel):
    id: Optional[UUID] = None
    invoice_id: Optional[UUID] = None # Optional for creation
    product_id: UUID
    quantity: int = 1
    price: float = 0
    total: float = 0

    model_config = ConfigDict(from_attributes=True)

class InvoiceItemCreate(BaseModel):
    product_id: UUID
    quantity: int = 1
    price: float = 0
    total: float = 0

class Invoice(BaseModel):
    id: Optional[UUID] = None
    company_id: Optional[UUID] = None # Optional for creation
    client_id: Optional[UUID] = None
    invoice_date: date = date.today()
    total_amount: float = 0
    payment_status: Optional[str] = 'unpaid'
    notes: Optional[str] = None
    items: List[InvoiceItem] = [] # For response

    model_config = ConfigDict(from_attributes=True)

class InvoiceCreate(BaseModel):
    client_id: UUID
    invoice_date: date
    total_amount: float
    payment_status: Optional[str] = 'unpaid'
    notes: Optional[str] = None
    items: List[InvoiceItemCreate] = []


class Purchase(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    supplier_id: Optional[UUID] = None
    purchase_date: date = date.today()
    total_amount: float = 0
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PurchaseItem(BaseModel):
    id: Optional[UUID] = None
    purchase_id: UUID
    product_id: UUID
    quantity: int = 1
    price: float = 0
    total: float = 0

    model_config = ConfigDict(from_attributes=True)

class Expense(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    title: str
    category: Optional[str] = None
    amount: float = 0
    expense_date: date = date.today()
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class Lead(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = 'new'

    model_config = ConfigDict(from_attributes=True)

class WhatsappLog(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    user_id: UUID  # Added this line
    message_type: Optional[str] = None
    whatsapp_message_id: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[str] = None
    status: Optional[str] = 'sent'

    model_config = ConfigDict(from_attributes=True)

class ScheduledWhatsappMessage(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    phone: str
    message: str
    scheduled_at: datetime
    status: Optional[str] = 'pending'

    model_config = ConfigDict(from_attributes=True)

class ScheduledWhatsappMessageCreate(BaseModel):
    phone: str
    message: str
    scheduled_at: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True)

class UploadedDoc(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    file_name: str
    file_url: str

    model_config = ConfigDict(from_attributes=True)

class Account(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    name: str
    type: str
    balance: float = 0

    model_config = ConfigDict(from_attributes=True)

class JournalEntry(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    account_id: UUID
    invoice_id: Optional[UUID] = None
    purchase_id: Optional[UUID] = None
    expense_id: Optional[UUID] = None
    date: date
    debit: float = 0
    credit: float = 0

    model_config = ConfigDict(from_attributes=True)

class ExpenseReport(BaseModel):
    category: str
    sum: float

class Setting(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    key: str
    value: Any

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('value')
    def serialize_value(self, value: any, _info):
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return value
