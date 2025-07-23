from datetime import datetime
import pickle as pkl

import spacy

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Fact, Verb, Character, CharacterTypes, FactTypes
from utils.get_or_create_by_name import get_or_create_by_name
from utils.text_to_spacy_ids import text_to_spacy_ids


def add_fact(
    session,
    subject,
    verb,
    obj="",
    target=None,
    fact_type="narration",
    description="",
    text="",
    prev_facts=None,
    date=None,
    chapter=-1,
    locked=False,
    *,
    character_type="character",
) -> int:
    if isinstance(session, str):
        engine = create_engine(session)
        session = Session(engine).__enter__()
        exit_session = True
    else:
        exit_session = False

    # Handle verb (convert to ID if string)
    if isinstance(verb, str):
        verb_id = get_or_create_by_name(session, Verb, verb.lower())
    else:
        verb_id = verb

    # Handle character type (convert to ID if string)
    if isinstance(character_type, str):
        character_type_id = get_or_create_by_name(
            session,
            CharacterTypes,
            character_type.lower().replace(" ", "_")
        )
    else:
        character_type_id = character_type

    # Handle subject (convert to list of IDs if string/int)
    if isinstance(subject, (str, int)):
        subject = [subject]
    subject_ids = [
        get_or_create_by_name(
            session,
            Character,
            char.lower().replace(" ", "_"),
            type=character_type_id,
        )
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
        get_or_create_by_name(
            session,
            Character,
            char.lower().replace(" ", "_"),
            type=character_type_id,
        )
        if isinstance(char, str)
        else char
        for char in target_ids
    ]

    # Handle prev_facts (convert to list of IDs if int)
    if prev_facts is None:
        prev_facts_ids = None
    elif isinstance(prev_facts, int):
        prev_facts_ids = [prev_facts]
    else:
        prev_facts_ids = prev_facts

    # Set default date if not provided
    if date is None:
        date = datetime.now()

    # Handle fact type (convert to ID if string)
    if isinstance(fact_type, str):
        fact_type_id = get_or_create_by_name(
            session,
            FactTypes,
            fact_type.lower(),
        )
    else:
        fact_type_id = fact_type

    # Convert to bytes
    if subject_ids:
        subject_ids = pkl.dumps(subject_ids)
    else:
        subject_ids = None

    if target_ids:
        target_ids = pkl.dumps(target_ids)
    else:
        target_ids = None

    if obj:
        obj = pkl.dumps(text_to_spacy_ids(session, obj))
    else:
        obj = None

    if description:
        description = pkl.dumps(text_to_spacy_ids(session, description))
    else:
        description = None

    if text:
        text = pkl.dumps(text_to_spacy_ids(session, text))
    else:
        text = None

    if prev_facts_ids:
        prev_facts_ids = pkl.dumps(prev_facts_ids)
    else:
        prev_facts_ids = None

    # Create the fact
    new_fact = Fact(
        subject=subject_ids,
        verb_id=verb_id,
        object=obj,
        target=target_ids,
        type=fact_type_id,
        description=description,
        text=text,
        prev_facts=prev_facts_ids,
        date=date,
        chapter=chapter,
        locked=locked,
    )
    session.add(new_fact)

    if exit_session:
        session.commit()
        session.__exit__()
        return new_fact.id
    else:
        session.flush()
        return new_fact.id
