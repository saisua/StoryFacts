from typing import Final

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dsak.load import load

from db.add_fact import add_fact


GLOBAL_STR: Final[str] = "@"


def from_dsak(db_uri, file_path):
	engine = create_engine(db_uri)
	with Session(engine) as session:
		global_args = []
		global_kwargs = {}
		id_map = dict()
		for args, kwargs in load(file_path):
			rel_id = kwargs.pop("id", None)
			if rel_id is not None:
				rel_id = int(rel_id.strip())

			new_global_args = [
				arg[len(GLOBAL_STR):]
				for arg in args
				if arg.startswith(GLOBAL_STR)
			]
			new_global_kwargs = {
				key[len(GLOBAL_STR):]: value
				for key, value in kwargs.items()
				if key.startswith(GLOBAL_STR)
			}

			if new_global_args:
				global_args.extend(new_global_args)

				args = [
					arg
					for arg in args
					if not arg.startswith(GLOBAL_STR)
				]

			if new_global_kwargs:
				global_kwargs.update(new_global_kwargs)

				kwargs = {
					key: value
					for key, value in kwargs.items()
					if not key.startswith(GLOBAL_STR)
				}

			if "prev_facts" in kwargs:
				kwargs["prev_facts"] = [
					id_map[id]
					for id in map(
						int,
						map(
							str.strip,
							filter(None, kwargs["prev_facts"].split(",")),
						),
					)
				]

			db_id = add_fact(session, *global_args, *args, **(global_kwargs | kwargs))

			if rel_id is not None:
				id_map[rel_id] = db_id

		session.commit()
