from sqlalchemy import Integer,Column,Boolean,String,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id"), nullable=False)
    token = Column(String,nullable=False)
    expires_at = Column(DateTime, nullable = False)
    is_revoked = Column(Boolean, default = False)
    created_at = Column(DateTime, default = datetime.now)
    
    user = relationship("User")
    