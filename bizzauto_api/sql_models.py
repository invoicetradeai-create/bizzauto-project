from sqlalchemy import Column, String, Float, Integer, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)

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

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    name = Column(String, index=True)
    sku = Column(String, nullable=True)
    category = Column(String, nullable=True)
    purchase_price = Column(Float, default=0)
    sale_price = Column(Float, default=0)
    stock_quantity = Column(Integer, default=0)
    low_stock_alert = Column(Integer, default=5)
    unit = Column(String, nullable=True)

    company = relationship("Company", back_populates="products")
    invoice_items = relationship("InvoiceItem", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
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
    password_hash = Column(String)
    role = Column(String)
    status = Column(String, default='active')

    company = relationship("Company", back_populates="users")
    settings = relationship("Setting", back_populates="user")

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
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
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True)
    invoice_date = Column(Date)
    total_amount = Column(Float, default=0)
    payment_status = Column(String, default='unpaid')
    notes = Column(String, nullable=True)

    company = relationship("Company", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    price = Column(Float, default=0)
    total = Column(Float, default=0)

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoice_items")

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    purchase_date = Column(Date)
    total_amount = Column(Float, default=0)
    notes = Column(String, nullable=True)

    company = relationship("Company", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase")

class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    price = Column(Float, default=0)
    total = Column(Float, default=0)

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    title = Column(String, index=True)
    category = Column(String, nullable=True)
    amount = Column(Float, default=0)
    expense_date = Column(Date)
    notes = Column(String, nullable=True)

    company = relationship("Company", back_populates="expenses")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    name = Column(String, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    status = Column(String, default='new')

    company = relationship("Company", back_populates="leads")

class WhatsappLog(Base):
    __tablename__ = "whatsapp_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    message_type = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    message = Column(String, nullable=True)
    status = Column(String, default='sent')

    company = relationship("Company", back_populates="whatsapp_logs")

class UploadedDoc(Base):
    __tablename__ = "uploaded_docs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    file_name = Column(String)
    file_url = Column(String)

    company = relationship("Company", back_populates="uploaded_docs")

class Setting(Base):
    __tablename__ = "settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    key = Column(String, index=True)
    value = Column(JSONB)

    user = relationship("User", back_populates="settings")
