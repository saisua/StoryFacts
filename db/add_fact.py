from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Fact, Verb, Character
from db.characters import create_character_enum
from db.verbs import create_verb_enum


def get_or_create_verb(session, verb_name):
    verb_name = verb_name.lower()
    verb = session.query(Verb).filter(Verb.name == verb_name).first()
    if not verb:
        verb = Verb(name=verb_name)
        session.add(verb)
        session.commit()
    return verb.id


def get_or_create_character(session, char_name):
    char_name = char_name.lower()
    char = session.query(Character).filter(Character.name == char_name).first()
    if not char:
        char = Character(name=char_name, description="", facts=None)
        session.add(char)
        session.commit()
    return char.id


def add_fact(
    db_uri,
    subject,
    verb,
    obj="",
    target=None,
    description="",
    prev_facts=None,
    date=None,
    chapter=-1,
    locked=False,
):
    engine = create_engine(db_uri)
    with Session(engine) as session:
        # Handle verb (convert to ID if string)
        if isinstance(verb, str):
            verb_id = get_or_create_verb(session, verb)
        else:
            verb_id = verb

        # Handle subject (convert to list of IDs if string/int)
        if isinstance(subject, (str, int)):
            subject = [subject]
        subject_ids = [
            get_or_create_character(session, char)
            if isinstance(char, str)
            else char
            for char in subject
        ]

        # Handle target (convert to list of IDs if string/int)
        if target is None:
            target_ids = []
        elif isinstance(target, (str, int)):
            target_ids = [target]
        else:
            target_ids = target
        target_ids = [
            get_or_create_character(session, char)
            if isinstance(char, str)
            else char
            for char in target_ids
        ]

        # Handle prev_facts (convert to list of IDs if int)
        if prev_facts is None:
            prev_facts_ids = []
        elif isinstance(prev_facts, int):
            prev_facts_ids = [prev_facts]
        else:
            prev_facts_ids = prev_facts

        # Set default date if not provided
        if date is None:
            date = datetime.now()

        # Create the fact
        new_fact = Fact(
            subject=bytes(subject_ids),
            verb_id=verb_id,
            object=obj,
            target=bytes(target_ids),
            description=description,
            prev_facts=bytes(prev_facts_ids),
            date=date,
            chapter=chapter,
            locked=locked,
        )
        session.add(new_fact)
        session.commit()
        return new_fact.id
