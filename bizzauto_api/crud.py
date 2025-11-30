from sqlalchemy.orm import Session
from sql_models import (
    Company, Product, Client, User, Supplier, Invoice, InvoiceItem, Purchase, PurchaseItem, Expense, Lead, WhatsappLog, UploadedDoc, Setting, ScheduledWhatsappMessage
)
from models import (
    Company as PydanticCompany, 
    Product as PydanticProduct, 
    Client as PydanticClient, 
    User as PydanticUser, 
    Supplier as PydanticSupplier,
    Invoice as PydanticInvoice,
    InvoiceItem as PydanticInvoiceItem,
    Purchase as PydanticPurchase,
    PurchaseItem as PydanticPurchaseItem,
    Expense as PydanticExpense,
    Lead as PydanticLead,
    WhatsappLog as PydanticWhatsappLog,
    UploadedDoc as PydanticUploadedDoc,
    Setting as PydanticSetting,
    ScheduledWhatsappMessage as PydanticScheduledWhatsappMessage
)
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import func

def get_company(db: Session, company_id: UUID):
    return db.query(Company).filter(Company.id == company_id).first()

def get_companies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Company).offset(skip).limit(limit).all()

def create_company(db: Session, company: PydanticCompany):
    db_company = Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def update_company(db: Session, company_id: UUID, company: PydanticCompany):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company:
        for key, value in company.model_dump(exclude_unset=True).items():
            setattr(db_company, key, value)
        db.commit()
        db.refresh(db_company)
    return db_company

def delete_company(db: Session, company_id: UUID):
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company:
        db.delete(db_company)
        db.commit()
    return db_company

def get_product(db: Session, product_id: UUID):
    return db.query(Product).filter(Product.id == product_id).first()

def get_product_by_name(db: Session, name: str):
    return db.query(Product).filter(Product.name.ilike(f"%{name}%")).first()

def get_products(db: Session, skip: int = 0, limit: int = 100, company_id: UUID = None):
    query = db.query(Product)
    if company_id:
        query = query.filter(Product.company_id == company_id)
    return query.offset(skip).limit(limit).all()

def create_product(db: Session, product: PydanticProduct, user_id: UUID):
    db_product = Product(**product.model_dump(exclude_none=True), user_id=user_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: UUID, product: PydanticProduct):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        for key, value in product.model_dump(exclude_unset=True).items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: UUID):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product

def get_stock_summary(db: Session):
    return db.query(Product.name, Product.stock_quantity).all()

def get_alert_products(db: Session, company_id: UUID, days_to_expiry: int = 30):
    """
    Retrieves products that are low in stock or have an approaching expiration date.
    """
    current_date = datetime.utcnow()
    expiry_threshold = current_date + timedelta(days=days_to_expiry)

    return db.query(Product).filter(
        Product.company_id == company_id,
        ((Product.stock_quantity <= Product.low_stock_alert) |
         (Product.expiration_date <= expiry_threshold))
    ).all()

def get_client(db: Session, client_id: UUID):
    return db.query(Client).filter(Client.id == client_id).first()

def get_client_by_name(db: Session, name: str):
    return db.query(Client).filter(Client.name == name).first()


def get_clients(db: Session, skip: int = 0, limit: int = 100, company_id: UUID = None):
    query = db.query(Client)
    if company_id:
        query = query.filter(Client.company_id == company_id)
    return query.offset(skip).limit(limit).all()

def create_client(db: Session, client: PydanticClient, user_id: UUID):
    db_client = Client(**client.model_dump(exclude_none=True), user_id=user_id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def update_client(db: Session, client_id: UUID, client: PydanticClient):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if db_client:
        for key, value in client.model_dump(exclude_unset=True).items():
            setattr(db_client, key, value)
        db.commit()
        db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: UUID):
    db_client = db.query(Client).filter(Client.id == client_id).first()
    if db_client:
        db.delete(db_client)
        db.commit()
    return db_client

def get_user(db: Session, user_id: UUID):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: PydanticUser):
    db_user = User(**user.model_dump(exclude_none=True))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: UUID, user: PydanticUser):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        for key, value in user.model_dump(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: UUID):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def get_supplier(db: Session, supplier_id: UUID):
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()

def get_suppliers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Supplier).offset(skip).limit(limit).all()

def create_supplier(db: Session, supplier: PydanticSupplier, user_id: UUID):
    db_supplier = Supplier(**supplier.model_dump(exclude_none=True), user_id=user_id)
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

def update_supplier(db: Session, supplier_id: UUID, supplier: PydanticSupplier):
    db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if db_supplier:
        for key, value in supplier.model_dump(exclude_unset=True).items():
            setattr(db_supplier, key, value)
        db.commit()
        db.refresh(db_supplier)
    return db_supplier

def delete_supplier(db: Session, supplier_id: UUID):
    db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if db_supplier:
        db.delete(db_supplier)
        db.commit()
    return db_supplier

def get_invoice(db: Session, invoice_id: UUID):
    return db.query(Invoice).filter(Invoice.id == invoice_id).first()

def get_invoices(db: Session, skip: int = 0, limit: int = 100, company_id: UUID = None):
    query = db.query(Invoice)
    if company_id:
        query = query.filter(Invoice.company_id == company_id)
    return query.offset(skip).limit(limit).all()

def create_invoice(db: Session, invoice: PydanticInvoice, company_id: UUID, user_id: UUID):
    # Extract items and create the main invoice object
    invoice_data = invoice.model_dump(exclude={'items', 'company_id'})
    db_invoice = Invoice(**invoice_data, company_id=company_id, user_id=user_id)
    db.add(db_invoice)
    db.commit() # Commit to get the db_invoice.id
    db.refresh(db_invoice)
    print(f"Created invoice with ID: {db_invoice.id}")

    # Now create the invoice items
    if invoice.items:
        for item_data in invoice.items:
            db_item = InvoiceItem(**item_data.model_dump(), invoice_id=db_invoice.id, user_id=user_id)
            db.add(db_item)
            print(f"Creating invoice item for product ID: {db_item.product_id}")
    
    db.commit() # Commit the new items
    db.refresh(db_invoice) # Refresh to load the items relationship
    return db_invoice

def update_invoice(db: Session, invoice_id: UUID, invoice_data: PydanticInvoice):
    print(f"Attempting to update invoice with ID: {invoice_id}")
    print(f"Received update data: {invoice_data.model_dump()}")

    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    if not db_invoice:
        print(f"Invoice with ID: {invoice_id} not found for update.")
        return None

    try:
        # Update top-level invoice fields from the new data
        update_data = invoice_data.model_dump(exclude_unset=True, exclude={'items'})
        for key, value in update_data.items():
            setattr(db_invoice, key, value)
        
        # --- Handle Invoice Items (Delete and Recreate) ---
        new_items_data = invoice_data.items

        # 1. Delete old items
        for item in db_invoice.items:
            db.delete(item)
        print(f"Deleted old items for invoice {invoice_id}")

        # 2. Add new items
        for item_data in new_items_data:
            if item_data.product_id:
                new_item = InvoiceItem(
                    invoice_id=db_invoice.id,
                    product_id=item_data.product_id,
                    user_id=db_invoice.user_id, # Inherit user_id from invoice
                    quantity=item_data.quantity,
                    price=item_data.price,
                    total=item_data.total
                )
                db.add(new_item)
                print(f"Adding new item for product ID: {item_data.product_id}")
        
        db.commit()
        db.refresh(db_invoice)
        print(f"Invoice {invoice_id} updated successfully.")
        return db_invoice

    except Exception as e:
        db.rollback()
        print(f"Error updating invoice {invoice_id}: {e}")
        raise

def delete_invoice(db: Session, invoice_id: UUID):
    print(f"Attempting to delete invoice with ID: {invoice_id}")
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if db_invoice:
        try:
            db.delete(db_invoice)
            db.commit()
            print(f"Invoice {invoice_id} and associated items deleted successfully.")
            return db_invoice
        except Exception as e:
            db.rollback()
            print(f"Error deleting invoice {invoice_id}: {e}")
            raise # Re-raise to let the router handle the HTTP exception
    print(f"Invoice with ID: {invoice_id} not found for deletion.")
    return None

def get_invoice_item(db: Session, invoice_item_id: UUID):
    return db.query(InvoiceItem).filter(InvoiceItem.id == invoice_item_id).first()

def get_invoice_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(InvoiceItem).offset(skip).limit(limit).all()

def create_invoice_item(db: Session, invoice_item: PydanticInvoiceItem):
    db_invoice_item = InvoiceItem(**invoice_item.model_dump(exclude_none=True))
    db.add(db_invoice_item)
    db.commit()
    db.refresh(db_invoice_item)
    return db_invoice_item

def update_invoice_item(db: Session, invoice_item_id: UUID, invoice_item: PydanticInvoiceItem):
    db_invoice_item = db.query(InvoiceItem).filter(InvoiceItem.id == invoice_item_id).first()
    if db_invoice_item:
        for key, value in invoice_item.model_dump(exclude_unset=True).items():
            setattr(db_invoice_item, key, value)
        db.commit()
        db.refresh(db_invoice_item)
    return db_invoice_item

def delete_invoice_item(db: Session, invoice_item_id: UUID):
    db_invoice_item = db.query(InvoiceItem).filter(InvoiceItem.id == invoice_item_id).first()
    if db_invoice_item:
        db.delete(db_invoice_item)
        db.commit()
    return db_invoice_item

def get_purchase(db: Session, purchase_id: UUID):
    return db.query(Purchase).filter(Purchase.id == purchase_id).first()

def get_purchases(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Purchase).offset(skip).limit(limit).all()

def create_purchase(db: Session, purchase: PydanticPurchase, user_id: UUID):
    db_purchase = Purchase(**purchase.model_dump(exclude_none=True), user_id=user_id)
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    return db_purchase

def update_purchase(db: Session, purchase_id: UUID, purchase: PydanticPurchase):
    db_purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if db_purchase:
        for key, value in purchase.model_dump(exclude_unset=True).items():
            setattr(db_purchase, key, value)
        db.commit()
        db.refresh(db_purchase)
    return db_purchase

def delete_purchase(db: Session, purchase_id: UUID):
    db_purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if db_purchase:
        db.delete(db_purchase)
        db.commit()
    return db_purchase

def get_purchase_item(db: Session, purchase_item_id: UUID):
    return db.query(PurchaseItem).filter(PurchaseItem.id == purchase_item_id).first()

def get_purchase_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PurchaseItem).offset(skip).limit(limit).all()

def create_purchase_item(db: Session, purchase_item: PydanticPurchaseItem):
    db_purchase_item = PurchaseItem(**purchase_item.model_dump(exclude_none=True))
    db.add(db_purchase_item)
    db.commit()
    db.refresh(db_purchase_item)
    return db_purchase_item

def update_purchase_item(db: Session, purchase_item_id: UUID, purchase_item: PydanticPurchaseItem):
    db_purchase_item = db.query(PurchaseItem).filter(PurchaseItem.id == purchase_item_id).first()
    if db_purchase_item:
        for key, value in purchase_item.model_dump(exclude_unset=True).items():
            setattr(db_purchase_item, key, value)
        db.commit()
        db.refresh(db_purchase_item)
    return db_purchase_item

def delete_purchase_item(db: Session, purchase_item_id: UUID):
    db_purchase_item = db.query(PurchaseItem).filter(PurchaseItem.id == purchase_item_id).first()
    if db_purchase_item:
        db.delete(db_purchase_item)
        db.commit()
    return db_purchase_item

def get_expense(db: Session, expense_id: UUID):
    return db.query(Expense).filter(Expense.id == expense_id).first()

def get_expenses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Expense).offset(skip).limit(limit).all()

def create_expense(db: Session, expense: PydanticExpense, user_id: UUID):
    db_expense = Expense(**expense.model_dump(exclude_none=True), user_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def update_expense(db: Session, expense_id: UUID, expense: PydanticExpense):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if db_expense:
        for key, value in expense.model_dump(exclude_unset=True).items():
            setattr(db_expense, key, value)
        db.commit()
        db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: UUID):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if db_expense:
        db.delete(db_expense)
        db.commit()
    return db_expense

def get_lead(db: Session, lead_id: UUID):
    return db.query(Lead).filter(Lead.id == lead_id).first()

def get_leads(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Lead).offset(skip).limit(limit).all()

def create_lead(db: Session, lead: PydanticLead, user_id: UUID):
    db_lead = Lead(**lead.model_dump(exclude_none=True), user_id=user_id)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def update_lead(db: Session, lead_id: UUID, lead: PydanticLead):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead:
        for key, value in lead.model_dump(exclude_unset=True).items():
            setattr(db_lead, key, value)
        db.commit()
        db.refresh(db_lead)
    return db_lead

def delete_lead(db: Session, lead_id: UUID):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead:
        db.delete(db_lead)
        db.commit()
    return db_lead

def get_whatsapp_log(db: Session, whatsapp_log_id: UUID):
    return db.query(WhatsappLog).filter(WhatsappLog.id == whatsapp_log_id).first()

def get_whatsapp_logs(db: Session, skip: int = 0, limit: int = 100, company_id: UUID = None):
    query = db.query(WhatsappLog)
    if company_id:
        query = query.filter(WhatsappLog.company_id == company_id)
    return query.offset(skip).limit(limit).all()

def create_whatsapp_log(db: Session, whatsapp_log: PydanticWhatsappLog, user_id: UUID):
    db_whatsapp_log = WhatsappLog(**whatsapp_log.model_dump(exclude_none=True), user_id=user_id)
    db.add(db_whatsapp_log)
    db.commit()
    db.refresh(db_whatsapp_log)
    return db_whatsapp_log

def get_whatsapp_log_by_whatsapp_message_id(db: Session, whatsapp_message_id: str):
    return db.query(WhatsappLog).filter(WhatsappLog.whatsapp_message_id == whatsapp_message_id).first()

def update_whatsapp_log(db: Session, whatsapp_message_id: str, whatsapp_log: PydanticWhatsappLog):
    db_whatsapp_log = db.query(WhatsappLog).filter(WhatsappLog.whatsapp_message_id == whatsapp_message_id).first()
    if db_whatsapp_log:
        for key, value in whatsapp_log.model_dump(exclude_unset=True).items():
            setattr(db_whatsapp_log, key, value)
        db.commit()
        db.refresh(db_whatsapp_log)
    return db_whatsapp_log

def delete_whatsapp_log(db: Session, whatsapp_log_id: UUID):
    db_whatsapp_log = db.query(WhatsappLog).filter(WhatsappLog.id == whatsapp_log_id).first()
    if db_whatsapp_log:
        db.delete(db_whatsapp_log)
        db.commit()
    return db_whatsapp_log

def get_whatsapp_log_by_whatsapp_message_id(db: Session, whatsapp_message_id: str):
    return db.query(WhatsappLog).filter(WhatsappLog.whatsapp_message_id == whatsapp_message_id).first()

def delete_whatsapp_log(db: Session, whatsapp_log_id: UUID):
    db_whatsapp_log = db.query(WhatsappLog).filter(WhatsappLog.id == whatsapp_log_id).first()
    if db_whatsapp_log:
        db.delete(db_whatsapp_log)
        db.commit()
    return db_whatsapp_log

# --- CRUD for ScheduledWhatsappMessage ---

def get_scheduled_whatsapp_message(db: Session, message_id: UUID):
    return db.query(ScheduledWhatsappMessage).filter(ScheduledWhatsappMessage.id == message_id).first()

def get_scheduled_whatsapp_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ScheduledWhatsappMessage).order_by(ScheduledWhatsappMessage.scheduled_at.desc()).offset(skip).limit(limit).all()

def get_pending_scheduled_whatsapp_messages(db: Session):
    return db.query(ScheduledWhatsappMessage).filter(ScheduledWhatsappMessage.status == 'pending', ScheduledWhatsappMessage.scheduled_at <= datetime.utcnow()).all()

def create_scheduled_whatsapp_message(db: Session, scheduled_message: PydanticScheduledWhatsappMessage, user_id: UUID):
    db_message = ScheduledWhatsappMessage(**scheduled_message.model_dump(), user_id=user_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_scheduled_whatsapp_message(db: Session, message_id: UUID, scheduled_message: PydanticScheduledWhatsappMessage):
    db_message = db.query(ScheduledWhatsappMessage).filter(ScheduledWhatsappMessage.id == message_id).first()
    if db_message:
        for key, value in scheduled_message.model_dump(exclude_unset=True).items():
            setattr(db_message, key, value)
        db.commit()
        db.refresh(db_message)
    return db_message

# --- End of CRUD for ScheduledWhatsappMessage ---

def get_uploaded_doc(db: Session, uploaded_doc_id: UUID):
    return db.query(UploadedDoc).filter(UploadedDoc.id == uploaded_doc_id).first()

def get_uploaded_docs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UploadedDoc).offset(skip).limit(limit).all()

def create_uploaded_doc(db: Session, uploaded_doc: PydanticUploadedDoc, user_id: UUID):
    db_uploaded_doc = UploadedDoc(**uploaded_doc.model_dump(exclude_none=True), user_id=user_id)
    db.add(db_uploaded_doc)
    db.commit()
    db.refresh(db_uploaded_doc)
    return db_uploaded_doc

def update_uploaded_doc(db: Session, uploaded_doc_id: UUID, uploaded_doc: PydanticUploadedDoc):
    db_uploaded_doc = db.query(UploadedDoc).filter(UploadedDoc.id == uploaded_doc_id).first()
    if db_uploaded_doc:
        for key, value in uploaded_doc.model_dump(exclude_unset=True).items():
            setattr(db_uploaded_doc, key, value)
        db.commit()
        db.refresh(db_uploaded_doc)
    return db_uploaded_doc

def delete_uploaded_doc(db: Session, uploaded_doc_id: UUID):
    db_uploaded_doc = db.query(UploadedDoc).filter(UploadedDoc.id == uploaded_doc_id).first()
    if db_uploaded_doc:
        db.delete(db_uploaded_doc)
        db.commit()
    return db_uploaded_doc

def get_setting(db: Session, setting_id: UUID):
    return db.query(Setting).filter(Setting.id == setting_id).first()

def get_settings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Setting).offset(skip).limit(limit).all()

def create_setting(db: Session, setting: PydanticSetting):
    setting_data = setting.model_dump(exclude_none=True)
    if 'value' in setting_data and not isinstance(setting_data['value'], str):
        setting_data['value'] = json.dumps(setting_data['value'])
    db_setting = Setting(**setting_data)
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting

def update_setting(db: Session, setting_id: UUID, setting: PydanticSetting):
    db_setting = db.query(Setting).filter(Setting.id == setting_id).first()
    if db_setting:
        update_data = setting.model_dump(exclude_unset=True)
        if 'value' in update_data and not isinstance(update_data['value'], str):
            update_data['value'] = json.dumps(update_data['value'])
            
        for key, value in update_data.items():
            setattr(db_setting, key, value)
        db.commit()
        db.refresh(db_setting)
    return db_setting

def delete_setting(db: Session, setting_id: UUID):
    db_setting = db.query(Setting).filter(Setting.id == setting_id).first()
    if db_setting:
        db.delete(db_setting)
        db.commit()
    return db_setting


