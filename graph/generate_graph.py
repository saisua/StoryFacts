import networkx as nx
import pickle as pkl

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import spacy

from models import Fact, Character, Verb


NLP_MODEL = "en_core_web_sm"
try:
    nlp = spacy.load(NLP_MODEL)
except OSError:
    spacy.cli.download(NLP_MODEL)
    nlp = spacy.load(NLP_MODEL)


def spacy_id_to_text(session, spacy_ids: bytes) -> str:
    if not spacy_ids:
        return ""
    spacy_ids: list[int] = pkl.loads(spacy_ids)
    result = []
    i = 0
    while i < len(spacy_ids):
        # Check for character reference pattern: (c<id>)
        if (
            i + 2 < len(spacy_ids) and
            spacy_ids[i] == ord('(') and
            spacy_ids[i+1] == ord('c')
        ):
            # Extract character ID
            i += 2
            char = session.get(Character, int(spacy_ids[i]))
            result.append(char.name if char else "?")
            i += 2
        else:
            # Try to decode as vocabulary token
            try:
                result.append(nlp.vocab.strings[spacy_ids[i]])
            except KeyError:
                raise
            i += 1
    return ' '.join(result)


def generate_graph(db_uri, id_labels: bool = False):
    engine = create_engine(db_uri)
    G = nx.DiGraph()

    characters = set()
    targets = set()
    verbs = set()
    objs = set()
    facts = set()
    child_facts = set()

    with Session(engine) as session:
        # Fetch all facts and their relationships
        for fact in session.query(Fact).all():
            if fact.text is not None:
                if id_labels:
                    fact_label = f"F-{fact.id}"
                else:
                    fact_text = spacy_id_to_text(session, fact.text)
                    if len(fact_text) > 10:
                        fact_text = f"{fact_text[:10]}..."
                    fact_label = f"F-{fact_text}"
                facts.add(fact_label)
            else:
                fact_label = None

            if id_labels:
                verb_label = f"V-{fact.verb_id}"
            else:
                verb_label = f"V-{session.get(Verb, fact.verb_id).name}"

            verbs.add(verb_label)

            # Add subject references (characters → verb)
            if fact.subject:
                for char_id in pkl.loads(fact.subject):
                    if id_labels:
                        char_label = f"C-{char_id}"
                    else:
                        char_label = f"C-{session.get(Character, char_id).name}"

                    G.add_edge(char_label, verb_label)
                    characters.add(char_label)

            # Add fact → verb edge
            if fact_label is not None:
                G.add_edge(fact_label, verb_label)

            # Add object references (verb → object)
            if fact.object:
                if id_labels:
                    obj_label = f"O-{fact.object}"
                else:
                    obj_text = spacy_id_to_text(session, fact.object)
                    if len(obj_text) > 10:
                        obj_text = f"{obj_text[:10]}..."
                    obj_label = f"O-{obj_text}"

                G.add_edge(verb_label, obj_label)
                objs.add(obj_label)

            # Add target references (verb → target characters)
            if fact.target:
                for char_id in pkl.loads(fact.target):
                    if id_labels:
                        char_label = f"C-{char_id}"
                    else:
                        char_label = f"C-{session.get(Character, char_id).name}"

                    G.add_edge(verb_label, char_label)
                    targets.add(char_label)

            # Add previous fact references (child → parent)
            if fact.prev_facts and fact_label is not None:
                for prev_fact_id in pkl.loads(fact.prev_facts):
                    if prev_fact_id is None:
                        continue

                    if id_labels:
                        pfact_label = f"F-{prev_fact_id}"
                    else:
                        prev_fact = session.get(Fact, prev_fact_id)
                        if prev_fact is None:
                            continue
                        if prev_fact.text is None:
                            continue
                        pfact_text = spacy_id_to_text(session, prev_fact.text)
                        if len(pfact_text) > 10:
                            pfact_text = f"{pfact_text[:10]}..."
                        pfact_label = f"F-{pfact_text}"

                    G.add_edge(pfact_label, fact_label)
                    child_facts.add(pfact_label)

    # Color-code nodes
    for fact in facts:
        color = "#00008B" if fact in child_facts else "#0000FF"
        G.add_node(fact, color=color, label=fact)

    for char in characters:
        color = "#FF0000" if char in targets else "#FF7F7F"
        G.add_node(char, color=color, label=char)

    for tar in targets - characters:
        G.add_node(tar, color="#8B0000", label=tar)

    for verb in verbs:
        G.add_node(verb, color="#00AA00", label=verb)

    for obj in objs:
        G.add_node(obj, color="#FFA500", label=obj)

    return G
