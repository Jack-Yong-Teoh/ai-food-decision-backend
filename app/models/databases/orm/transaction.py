from sqlalchemy import Column, Integer, Numeric, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.databases.orm.base import Base, AuditModel
from app.models.enums.transaction import TransactionType
from app.utilities.orm import EnumValue


class Transaction(Base, AuditModel):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    amount = Column(Numeric, nullable=False)
    transaction_type = Column(EnumValue(TransactionType), nullable=False)
    reference_id = Column(String, nullable=True)

    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
