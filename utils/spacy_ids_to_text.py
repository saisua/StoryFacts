import pickle as pkl

import spacy

from models.character import Character
from models.oov_words import OOVWords


NLP_MODEL = "en_core_web_sm"
try:
    nlp = spacy.load(NLP_MODEL)
except OSError:
    spacy.cli.download(NLP_MODEL)
    nlp = spacy.load(NLP_MODEL)

spacy_vocab = nlp.vocab.strings


def spacy_ids_to_text(session, spacy_ids: bytes) -> str:
    if not spacy_ids:
        return ""
    if isinstance(spacy_ids, str):
        return spacy_ids

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
                result.append(spacy_vocab[spacy_ids[i]])
            except KeyError:
                oov_word = session.query(OOVWords)\
                    .filter(
                        OOVWords.spacy_id == spacy_ids[i],
                    )\
                    .first()
                result.append(oov_word.word if oov_word else "?")
            i += 1
    return ' '.join(result)
