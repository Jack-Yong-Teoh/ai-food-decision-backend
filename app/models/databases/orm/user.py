from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.databases.orm.base import Base, AuditModel


class User(Base, AuditModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean)
    last_access = Column(DateTime)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Relationships
    wallet = relationship(
        "Wallet",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def wallet_id(self) -> int | None:
        """Get wallet_id from the wallet relationship"""
        return self.wallet.id if self.wallet else None
