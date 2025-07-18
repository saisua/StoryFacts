from sqlalchemy import create_engine

from models import Base


def init_db(db_uri):
	engine = create_engine(db_uri)
	Base.metadata.create_all(engine)


if __name__ == "__main__":
	DB_URI = "sqlite:///storyfacts.db"
	init_db(DB_URI)
