from sqlalchemy import Column, Integer, String, Text, LargeBinary

from .base import Base


class CharacterTypes(Base):
	__tablename__ = 'CharacterTypes'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String, unique=True)
	description = Column(Text, nullable=True)
