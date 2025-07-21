from sqlalchemy import Column, Integer, String, Text, LargeBinary

from .base import Base


class FactTypes(Base):
	__tablename__ = 'FactTypes'

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String, unique=True)
	description = Column(Text, nullable=True)
