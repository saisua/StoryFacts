from sqlalchemy import (
	Column, Integer, Text, LargeBinary, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship

from .base import Base


class Fact(Base):
	__tablename__ = 'Facts'

	id = Column(Integer, primary_key=True, autoincrement=True)
	subject = Column(LargeBinary)
	verb_id = Column(Integer, ForeignKey('Verbs.id'))
	object = Column(Text)
	target = Column(LargeBinary)
	description = Column(Text)
	narration = Column(Text)
	prev_facts = Column(LargeBinary)
	date = Column(DateTime)
	chapter = Column(Integer)
	locked = Column(Boolean)

	verb = relationship("Verb", back_populates="facts")
