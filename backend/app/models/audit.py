from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    entity_type = Column(String(100))  # user, product, sale, etc.
    entity_id = Column(Integer)
    changes = Column(JSON)  # Before/after values for updates
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    status = Column(String(50), default="success")  # success, failed
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, entity_type={self.entity_type}, user_id={self.user_id})>"
