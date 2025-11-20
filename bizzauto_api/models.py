from pydantic import BaseModel, Json, ConfigDict, field_serializer
from typing import Optional, List
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

class Invoice(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    client_id: Optional[UUID] = None
    invoice_date: date = date.today()
    total_amount: float = 0
    payment_status: Optional[str] = 'unpaid'
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class InvoiceItem(BaseModel):
    id: Optional[UUID] = None
    invoice_id: UUID
    product_id: UUID
    quantity: int = 1
    price: float = 0
    total: float = 0

    model_config = ConfigDict(from_attributes=True)

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
    message_type: Optional[str] = None
    whatsapp_message_id: Optional[str] = None # Added this line
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
    scheduled_at: datetime

class UploadedDoc(BaseModel):
    id: Optional[UUID] = None
    company_id: UUID
    file_name: str
    file_url: str

    model_config = ConfigDict(from_attributes=True)

class Setting(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    key: str
    value: Json

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('value')
    def serialize_value(self, value: any, _info):
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return value
