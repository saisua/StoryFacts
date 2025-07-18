from enum import Enum
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models.character import Character


def get_character_names(db_uri):
	engine = create_engine(db_uri)
	with Session(engine) as session:
		names = session.scalars(select(Character.name).distinct()).all()
	return names


def create_character_enum(db_uri, enum_name="CharacterName"):
	names = get_character_names(db_uri)
	return Enum(enum_name, {name.upper(): name for name in names})
