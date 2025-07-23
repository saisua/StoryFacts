import os
from typing import Final

from db.init_db import init_db
from db.from_dsak import from_dsak

from graph.plot_graph import plot_graph
from db.generate_markdown import generate_markdown


DB_FILE: Final[str] = "storyfacts.db"
DB_URI: Final[str] = f"sqlite:///{DB_FILE}"
DSAK_FILE: Final[str] = "story_sample.dsak"

PURGE_DB: Final[bool] = True
LOAD_DSAK: Final[bool] = True
GENERATE_TEXT: Final[bool] = True
GENERATE_GRAPH: Final[bool] = False


def main():
	if PURGE_DB:
		try:
			os.remove(DB_FILE)
		except OSError:
			pass

	init_db(DB_URI)

	if LOAD_DSAK:
		from_dsak(
			DB_URI,
			DSAK_FILE,
		)

	if GENERATE_TEXT:
		generate_markdown(DB_URI)

	if GENERATE_GRAPH:
		plot_graph(DB_URI)


if __name__ == "__main__":
	main()
