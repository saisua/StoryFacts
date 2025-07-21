from datetime import datetime
import pickle as pkl

import spacy

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Fact, Verb, Character, CharacterTypes, FactTypes


NLP_MODEL = "en_core_web_sm"
try:
    nlp = spacy.load(NLP_MODEL)
except OSError:
    spacy.cli.download(NLP_MODEL)
    nlp = spacy.load(NLP_MODEL)


def get_or_create_character_type(session, char_type_name):
    char_type_name = char_type_name.lower()
    char_type = session.query(CharacterTypes)\
        .filter(CharacterTypes.name == char_type_name)\
        .first()
    if not char_type:
        char_type = CharacterTypes(name=char_type_name)
        session.add(char_type)
        session.commit()
    return char_type.id


def get_or_create_fact_type(session, fact_type_name):
    fact_type_name = fact_type_name.lower()
    fact_type = session.query(FactTypes)\
        .filter(FactTypes.name == fact_type_name)\
        .first()
    if not fact_type:
        fact_type = FactTypes(name=fact_type_name)
        session.add(fact_type)
        session.commit()
    return fact_type.id


def get_or_create_verb(session, verb_name):
    verb_name = verb_name.lower()
    verb = session.query(Verb).filter(Verb.name == verb_name).first()
    if not verb:
        verb = Verb(name=verb_name)
        session.add(verb)
        session.commit()
    return verb.id


def get_or_create_character(session, char_name, char_type=None):
    char_name = char_name.lower().replace(" ", "_")
    char = session.query(Character).filter(Character.name == char_name).first()
    if not char:
        char = Character(
            name=char_name,
            description="",
            facts=None,
            type=char_type,
        )
        session.add(char)
        session.commit()
    return char.id


def text_to_spacy_ids(session, text: str) -> list[int]:
    if not text:
        return []

    doc = nlp(text)

    tokens = []
    for token in doc:
        if token.is_oov:  # Check if token is out-of-vocabulary
            # Try to find matching character
            char = session.query(Character)\
                .filter(Character.name == token.text.lower().replace(" ", "_"))\
                .first()
            if char:
                tokens.append(ord('('))  # Use ASCII code instead of token
                tokens.append(ord('c'))  # Use ASCII code for 'character'
                tokens.append(char.id)
                tokens.append(ord(')'))  # Use ASCII code instead of token
            else:
                tokens.append(token.lower)
        else:
            tokens.append(token.i)

    return tokens


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
        verb_id = get_or_create_verb(session, verb)
    else:
        verb_id = verb

    # Handle character type (convert to ID if string)
    if isinstance(character_type, str):
        character_type_id = get_or_create_character_type(
            session,
            character_type
        )
    else:
        character_type_id = character_type

    # Handle subject (convert to list of IDs if string/int)
    if isinstance(subject, (str, int)):
        subject = [subject]
    subject_ids = [
        get_or_create_character(session, char, character_type_id)
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
        get_or_create_character(session, char, character_type_id)
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

    # Handle fact type (convert to ID if string)
    if isinstance(fact_type, str):
        fact_type_id = get_or_create_fact_type(session, fact_type)
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
    return new_fact.id
