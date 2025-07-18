from typing import Generator


def load(file_path: str) -> Generator[
	tuple[list[str], dict[str, str]],
	None,
	None,
]:
	with open(file_path, "r") as f:
		text = f.read()

	lines = text.split("\n")

	args = list()
	kwargs = dict()
	for line in lines:
		if line.startswith("#"):
			continue
		line = line.strip()
		if line == "":
			continue
		if line == '-':
			yield args.copy(), kwargs.copy()
			args.clear()
			kwargs.clear()
			continue

		splits = line.split(":", 1)
		if len(splits) == 1:
			args.append(line.strip())
		else:
			key, value = splits
			kwargs[key.strip()] = value.strip()

	if args or kwargs:
		yield args.copy(), kwargs.copy()
