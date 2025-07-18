import yaml

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Fact, Character, Verb


def dump_to_yaml(db_uri, file_path):
    engine = create_engine(db_uri)
    with Session(engine) as session:
        # Fetch all facts
        facts = []
        for fact in session.query(Fact).all():
            facts.append({
                "id": fact.id,
                "subject": list(fact.subject),
                "verb": fact.verb_id,
                "object": fact.object,
                "target": list(fact.target),
                "description": fact.description,
                "prev_facts": list(fact.prev_facts),
                "date": fact.date.isoformat() if fact.date else None,
                "chapter": fact.chapter,
                "locked": fact.locked,
            })

        # Fetch all characters
        characters = []
        for char in session.query(Character).all():
            characters.append({
                "id": char.id,
                "name": char.name,
                "description": char.description,
                "facts": list(char.facts) if char.facts else [],
            })

        # Fetch all verbs
        verbs = []
        for verb in session.query(Verb).all():
            verbs.append({
                "id": verb.id,
                "name": verb.name,
            })

        # Structure data
        data = {
            "Facts": facts,
            "Characters": characters,
            "Verbs": verbs,
        }

        # Write to YAML
        with open(file_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

# Example usage:
# dump_to_yaml("sqlite:///storyfacts.db", "storyfacts_dump.yaml")
