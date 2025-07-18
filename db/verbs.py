from enum import Enum
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models.verb import Verb


def get_verb_names(db_uri):
	engine = create_engine(db_uri)
	with Session(engine) as session:
		names = session.scalars(select(Verb.name).distinct()).all()
	return names


def create_verb_enum(db_uri, enum_name="VerbName"):
	names = get_verb_names(db_uri)
	return Enum(enum_name, {name.upper(): name for name in names})
