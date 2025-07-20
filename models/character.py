from sqlalchemy import Column, Integer, String, Text, LargeBinary

from .base import Base


class Character(Base):
	__tablename__ = 'Characters'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String, unique=True)
	aliases = Column(Text)
	description = Column(Text)
	facts = Column(LargeBinary)
