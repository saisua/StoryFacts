from typing import Final

from db.init_db import init_db
from db.from_dsak import from_dsak


DB_URI: Final[str] = "sqlite:///storyfacts.db"
DSAK_FILE: Final[str] = "story_sample.dsak"


def main():
	init_db(DB_URI)

	from_dsak(
		DB_URI,
		DSAK_FILE,
	)


if __name__ == "__main__":
	main()
