import yaml

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Fact, Character, Verb


def load_from_yaml(db_uri, file_path):
	engine = create_engine(db_uri)
	with Session(engine) as session:
		# Read YAML
		with open(file_path, "r") as f:
			data = yaml.safe_load(f)

		# Load verbs (simple inserts)
		for verb_data in data.get("Verbs", []):
			verb = session.query(Verb)\
				.filter(Verb.id == verb_data["id"])\
				.first()
			if not verb:
				verb = Verb(id=verb_data["id"], name=verb_data["name"])
				session.add(verb)

		# Load characters
		for char_data in data.get("Characters", []):
			char = session.query(Character)\
				.filter(Character.id == char_data["id"])\
				.first()
			if not char:
				char = Character(
					id=char_data["id"],
					name=char_data["name"],
					description=char_data["description"],
					facts=(
						bytes(char_data["facts"])
						if char_data["facts"]
						else None
					),
				)
				session.add(char)

		# Load facts
		for fact_data in data.get("Facts", []):
			fact = session.query(Fact)\
				.filter(Fact.id == fact_data["id"])\
				.first()
			if not fact:
				fact = Fact(
					id=fact_data["id"],
					subject=bytes(fact_data["subject"]),
					verb_id=fact_data["verb"],
					object=fact_data["object"],
					target=bytes(fact_data["target"]),
					description=fact_data["description"],
					prev_facts=bytes(fact_data["prev_facts"]),
					date=fact_data["date"],
					chapter=fact_data["chapter"],
					locked=fact_data["locked"],
				)
				session.add(fact)

		session.commit()
