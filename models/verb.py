from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Verb(Base):
	__tablename__ = 'Verbs'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String, unique=True)

	facts = relationship("Fact", back_populates="verb")
