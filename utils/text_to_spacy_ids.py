import spacy

from models.character import Character
from models.oov_words import OOVWords


NLP_MODEL = "en_core_web_sm"
try:
    nlp: spacy.Language = spacy.load(NLP_MODEL)
except OSError:
    spacy.cli.download(NLP_MODEL)
    nlp: spacy.Language = spacy.load(NLP_MODEL)

spacy_vocab = nlp.vocab.strings
b63_mask = 2**63 - 1


def text_to_spacy_ids(session, text: str) -> list[int]:
    if not text:
        return []

    doc = nlp(text)

    tokens = []
    for token in doc:
        if token.is_oov:  # Check if token is out-of-vocabulary
            # Try to find matching character
            char = session.query(Character)\
                .filter(
                    Character.name == token.text.lower().replace(" ", "_"),
                )\
                .first()
            if char:
                tokens.append(ord('('))  # Use ASCII code instead of token
                tokens.append(ord('c'))  # Use ASCII code for 'character'
                tokens.append(char.id)
                tokens.append(ord(')'))  # Use ASCII code instead of token
            else:
                spacy_id = token.lower & b63_mask

                oov_word = session.query(OOVWords)\
                    .filter(
                        OOVWords.spacy_id == spacy_id,
                    )\
                    .first()
                if oov_word:
                    tokens.append(oov_word.spacy_id)
                else:
                    session.add(OOVWords(word=token.lower_, spacy_id=spacy_id))
                    tokens.append(spacy_id)
        else:
            tokens.append(token.i)

    return tokens
