from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.databases.orm.base import Base, AuditModel


class Food(Base, AuditModel):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_name = Column(String, nullable=False)
    food_type = Column(String, nullable=False)
    calories = Column(String, nullable=False)
    description = Column(String, nullable=True)
    ingredients = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    # Relationships
    user = relationship(
        "User",
        back_populates="food",
    )
