from sqlalchemy import Integer,String,Column, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer,primary_key = True)
    action = Column(String(50), nullable = False)
    entity = Column(String(50), nullable = False)
    entity_id = Column(Integer, nullable = False)
    
    performed_by = Column(Integer, ForeignKey("users.id"), nullable = True)
    
    message = Column(String(255), nullable = True)
    created_at = Column(TIMESTAMP, default=func.now())