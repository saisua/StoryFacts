import networkx as nx

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Fact, Character, Verb


def generate_graph(db_uri):
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
            fact_label = f"F-{fact.id}"
            verb_label = f"V-{fact.verb_id}"

            facts.add(fact_label)
            verbs.add(verb_label)

            # Add subject references (characters → verb)
            if fact.subject:
                for char_id in list(fact.subject):
                    char_label = f"C-{char_id}"
                    G.add_edge(char_label, verb_label)
                    characters.add(char_label)

            # Add fact → verb edge
            G.add_edge(fact_label, verb_label)

            # Add object references (verb → object)
            if fact.object:
                obj_label = f"O-{fact.object}"
                G.add_edge(verb_label, obj_label)
                objs.add(obj_label)

            # Add target references (verb → target characters)
            if fact.target:
                for char_id in list(fact.target):
                    char_label = f"C-{char_id}"
                    G.add_edge(verb_label, char_label)
                    targets.add(char_label)

            # Add previous fact references (child → parent)
            if fact.prev_facts:
                for prev_fact_id in list(fact.prev_facts):
                    pfact_label = f"F-{prev_fact_id}"
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
        G.add_node(verb, color="#00FF00", label=verb)

    for obj in objs:
        G.add_node(obj, color="#FFA500", label=obj)

    return G
