from sqlalchemy import Column, Integer, String, Text, LargeBinary

from .base import Base


class OOVWords(Base):
	__tablename__ = 'OOVWords'

	spacy_id = Column(Integer, primary_key=True)
	word = Column(String, unique=True)
