from dsak.load import load

from db.add_fact import add_fact


def from_dsak(db_uri, file_path):
	id_map = dict()
	for args, kwargs in load(file_path):
		rel_id = int(kwargs.pop("id", None).strip())

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

		db_id = add_fact(db_uri, *args, **kwargs)

		if rel_id is not None:
			id_map[rel_id] = db_id
