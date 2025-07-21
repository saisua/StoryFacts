from sqlalchemy import Column, Integer, String, Text, LargeBinary, ForeignKey

from .base import Base


class Character(Base):
	__tablename__ = 'Characters'

	id = Column(Integer, primary_key=True, autoincrement=True)
	type = Column(Integer, ForeignKey('CharacterTypes.id'))
	name = Column(String, unique=True)
	aliases = Column(Text, nullable=True)
	description = Column(Text, nullable=True)
	facts = Column(LargeBinary, nullable=True)
