from sqlalchemy import inspect
from database import engine

inspector = inspect(engine)
if "whatsapp_logs" in inspector.get_table_names():
    print("Table 'whatsapp_logs' exists.")
else:
    print("Table 'whatsapp_logs' does NOT exist.")
