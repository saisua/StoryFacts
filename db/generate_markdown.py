from collections import defaultdict
import pickle as pkl

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Fact
from models.character import Character
from models.fact_types import FactTypes

from utils.spacy_ids_to_text import spacy_ids_to_text


def get0(t): return t[0]


def dialogue_format(session, text: str, fact) -> str:
	subjects = fact.subject
	targets = fact.target

	subjects = pkl.loads(subjects)

	if len(subjects) == 1:
		subj_str = session.get(Character, subjects[0]).name
	else:
		subj_str = ", ".join(map(
			lambda x: session.get(Character, x).name.replace("_", " "),
			subjects[:-1]
		))
		subj_str += " and " + session.get(
			Character,
			subjects[-1]
		).name.replace("_", " ")

	text_parts = list()
	if targets is not None:
		targets = pkl.loads(targets)
		if len(targets) == 1:
			target_str = session.get(Character, targets[0]).name
		else:
			target_str = ", ".join(map(
				lambda x: session.get(Character, x).name.replace("_", " "),
				targets[:-1]
			))
			target_str += " and " + session.get(
				Character,
				targets[-1]
			).name.replace("_", " ")

		text_parts.append(f"\n\n_{subj_str} said to {target_str}_:\n")
	else:
		text_parts.append(f"\n\n_{subj_str} said_:\n")

	text_parts.append('> ')
	text_parts.append(text)
	text_parts.append("\n\n")
	return "".join(text_parts)


def generate_markdown(
	db_uri,
	out_file: str = "story.md",
	start_fact_id: int | None = None,
) -> None:
	engine = create_engine(db_uri)
	with Session(engine) as session:
		dialogue_id = session\
			.query(FactTypes)\
			.filter(FactTypes.name == "dialogue")\
			.first()\
			.id

		if start_fact_id is None:
			# Get all fact IDs in order if no start ID provided
			facts = session.query(Fact.id).order_by(Fact.id).all()
			if not facts:
				return ""
		else:
			facts = [start_fact_id]

		if not facts:
			return ""

		visited = set()

		facts_remaining = len(facts) - 1
		facts = map(get0, facts)
		stack = [next(facts)]
		chapter_texts = defaultdict(list)
		while True:
			if len(stack):
				fact_id = stack.pop()
			elif facts_remaining:
				fact_id = next(facts)
				facts_remaining -= 1
			else:
				break

			if fact_id in visited:
				continue
			visited.add(fact_id)

			fact = session.query(Fact).get(fact_id)
			if not fact:
				continue

			if fact.text:
				text = spacy_ids_to_text(session, fact.text)

				if fact.type == dialogue_id:
					text = dialogue_format(session, text, fact)
				elif (
					len(chapter_texts[fact.chapter]) == 0
					or chapter_texts[fact.chapter][-1][-1] == '.'
				):
					text = f"\n{text.capitalize()}"

				chapter_texts[fact.chapter].append(text)

			if fact.prev_facts:
				# Group prev_facts by chapter to maintain chapter contiguity
				for prev_fact_id in pkl.loads(fact.prev_facts):
					if prev_fact_id is None:
						continue
					stack.insert(0, prev_fact_id)

		text_parts = []
		for chapter, texts in sorted(chapter_texts.items(), key=lambda x: x[0]):
			if len(text_parts) != 0:
				missing_nl = text_parts[-1][-2:].count('\n')
				if missing_nl != 2:
					text_parts.append('\n' * (2 - missing_nl))

			text_parts.append(f"**Chapter {chapter}**\n")
			text_parts.extend(texts)

	# Join text parts in reverse order since we traversed backwards
	text = "".join(text_parts)
	with open(out_file, "w") as f:
		f.write(text)
