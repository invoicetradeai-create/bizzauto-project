from database import SessionLocal
from sql_models import WhatsappLog, ScheduledWhatsappMessage
from sqlalchemy import func

db = SessionLocal()

try:
    # Check distinct statuses in WhatsappLog
    statuses = db.query(WhatsappLog.status, func.count(WhatsappLog.status)).group_by(WhatsappLog.status).all()
    print("WhatsappLog Statuses:", statuses)

    # Check distinct statuses in ScheduledWhatsappMessage
    scheduled_statuses = db.query(ScheduledWhatsappMessage.status, func.count(ScheduledWhatsappMessage.status)).group_by(ScheduledWhatsappMessage.status).all()
    print("ScheduledWhatsappMessage Statuses:", scheduled_statuses)

except Exception as e:
    print(e)
finally:
    db.close()
