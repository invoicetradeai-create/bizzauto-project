from sqlalchemy import Column, String, Float, Integer, ForeignKey, Date, DateTime
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from sqlalchemy.types import JSON

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone_number_id = Column(String, unique=True, nullable=True) # Added for WhatsApp multi-tenancy

    products = relationship("Product", back_populates="company")
    clients = relationship("Client", back_populates="company")
    users = relationship("User", back_populates="company")
    suppliers = relationship("Supplier", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")
    purchases = relationship("Purchase", back_populates="company")
    expenses = relationship("Expense", back_populates="company")
    leads = relationship("Lead", back_populates="company")
    whatsapp_logs = relationship("WhatsappLog", back_populates="company")
    uploaded_docs = relationship("UploadedDoc", back_populates="company")
    scheduled_whatsapp_messages = relationship("ScheduledWhatsappMessage", back_populates="company")
    accounts = relationship("Account", back_populates="company")
    journal_entries = relationship("JournalEntry", back_populates="company")

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String, index=True)
    sku = Column(String, nullable=True)
    category = Column(String, nullable=True)
    purchase_price = Column(Float, default=0)
    sale_price = Column(Float, default=0)
    stock_quantity = Column(Integer, default=0)
    low_stock_alert = Column(Integer, default=5)
    unit = Column(String, nullable=True)
    expiration_date = Column(DateTime(timezone=True), nullable=True)

    company = relationship("Company", back_populates="products")
    invoice_items = relationship("InvoiceItem", back_populates="product", cascade="all, delete-orphan")
    purchase_items = relationship("PurchaseItem", back_populates="product", cascade="all, delete-orphan")

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)

    company = relationship("Company", back_populates="clients")
    invoices = relationship("Invoice", back_populates="client")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=True)
    role = Column(String)
    business_name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    status = Column(String, default='active')
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="users")
    settings = relationship("Setting", back_populates="user")

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)

    company = relationship("Company", back_populates="suppliers")
    purchases = relationship("Purchase", back_populates="supplier")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True)
    invoice_date = Column(Date)
    total_amount = Column(Float, default=0)
    payment_status = Column(String, default='unpaid')
    notes = Column(String, nullable=True)

    

    company = relationship("Company", back_populates="invoices")

    client = relationship("Client", back_populates="invoices")

    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

    journal_entries = relationship("JournalEntry", back_populates="invoice")
class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    quantity = Column(Integer, default=1)
    price = Column(Float, default=0)
    total = Column(Float, default=0)

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoice_items")

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    purchase_date = Column(Date)
    total_amount = Column(Float, default=0)
    notes = Column(String, nullable=True)

    

    company = relationship("Company", back_populates="purchases")

    supplier = relationship("Supplier", back_populates="purchases")

    items = relationship("PurchaseItem", back_populates="purchase")

    journal_entries = relationship("JournalEntry", back_populates="purchase")
class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    quantity = Column(Integer, default=1)
    price = Column(Float, default=0)
    total = Column(Float, default=0)

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(String, index=True)
    category = Column(String, nullable=True)
    amount = Column(Float, default=0)
    expense_date = Column(Date)
    notes = Column(String, nullable=True)

    

    company = relationship("Company", back_populates="expenses")

    journal_entries = relationship("JournalEntry", back_populates="expense")
class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    status = Column(String, default='new')

    company = relationship("Company", back_populates="leads")

class WhatsappLog(Base):
    __tablename__ = "whatsapp_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    message_type = Column(String, nullable=True)
    whatsapp_message_id = Column(String, nullable=True, unique=True) # Added this line
    phone = Column(String, nullable=True)
    message = Column(String, nullable=True)
    status = Column(String, default='sent')

    company = relationship("Company", back_populates="whatsapp_logs")

class ScheduledWhatsappMessage(Base):
    __tablename__ = "scheduled_whatsapp_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    phone = Column(String, nullable=False)
    message = Column(String, nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    status = Column(String, default='pending', index=True) # pending, sent, failed

    company = relationship("Company", back_populates="scheduled_whatsapp_messages")

class UploadedDoc(Base):
    __tablename__ = "uploaded_docs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    file_name = Column(String)
    file_url = Column(String)

    company = relationship("Company", back_populates="uploaded_docs")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String, index=True)
    type = Column(String, index=True)  # e.g., Asset, Liability, Equity, Revenue, Expense
    balance = Column(Float, default=0)

    company = relationship("Company", back_populates="accounts")
    journal_entries = relationship("JournalEntry", back_populates="account")

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"))
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=True)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id"), nullable=True)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id"), nullable=True)
    date = Column(Date)
    debit = Column(Float, default=0)
    credit = Column(Float, default=0)
    
    company = relationship("Company", back_populates="journal_entries")
    account = relationship("Account", back_populates="journal_entries")
    invoice = relationship("Invoice", back_populates="journal_entries")
    purchase = relationship("Purchase", back_populates="journal_entries")
    expense = relationship("Expense", back_populates="journal_entries")

class Setting(Base):
    __tablename__ = "settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    key = Column(String, index=True)
    value = Column(JSON().with_variant(JSONB, "postgresql"))

    user = relationship("User", back_populates="settings")

class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    subject = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
