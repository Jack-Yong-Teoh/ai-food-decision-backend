from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.databases.orm.base import Base, AuditModel


class Wallet(Base, AuditModel):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)
    balance = Column(Numeric, nullable=False, default=0.0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship(
        "Transaction",
        back_populates="wallet",
        cascade="all, delete-orphan",
    )
