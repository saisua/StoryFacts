from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Fact, Character, Verb


def update_table(db_uri, table_name, record_id, updates):
    engine = create_engine(db_uri)
    with Session(engine) as session:
        # Map table names to model classes
        table_map = {
            "Facts": Fact,
            "Characters": Character,
            "Verbs": Verb,
        }

        # Validate table name
        if table_name not in table_map:
            raise ValueError(f"Invalid table name: {table_name}")

        Model = table_map[table_name]

        # Fetch the record
        record = session.query(Model).filter(Model.id == record_id).first()
        if not record:
            raise ValueError(
                f"Record with ID {record_id} not found in {table_name}"
            )

        # Apply updates
        for key, value in updates.items():
            if hasattr(record, key):
                # Handle binary fields (subject, target, prev_facts, facts)
                if (
                    key in {"subject", "target", "prev_facts", "facts"}
                    and isinstance(value, list)
                ):
                    setattr(record, key, bytes(value))
                else:
                    setattr(record, key, value)
            else:
                raise AttributeError(
                    f"Invalid field '{key}' for table {table_name}"
                )

        session.commit()
