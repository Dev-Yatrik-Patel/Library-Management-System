from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, nullable = False)
    email = Column(String, unique = True, nullable = False)
    password_hash = Column(String, nullable = False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable = False)
    created_at = Column(TIMESTAMP, server_default= func.now() )
    is_active = Column(Boolean, default=True)
    updated_at = Column(TIMESTAMP, nullable = True)
    
    
    role = relationship("Role")
    