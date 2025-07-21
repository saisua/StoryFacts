from sqlalchemy import (
	Column, Integer, Text, LargeBinary, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship

from .base import Base


class Fact(Base):
	__tablename__ = 'Facts'

	id = Column(Integer, primary_key=True, autoincrement=True)
	type = Column(Integer, ForeignKey('FactTypes.id'))
	subject = Column(LargeBinary, nullable=True)
	verb_id = Column(Integer, ForeignKey('Verbs.id'))
	object = Column(LargeBinary, nullable=True)
	target = Column(LargeBinary, nullable=True)
	description = Column(LargeBinary, nullable=True)
	text = Column(LargeBinary, nullable=True)
	prev_facts = Column(LargeBinary, nullable=True)
	date = Column(DateTime, nullable=True)
	chapter = Column(Integer, nullable=True)
	locked = Column(Boolean, nullable=True)

	verb = relationship("Verb", back_populates="facts")
