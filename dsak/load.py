from typing import Generator


def load(file_path: str) -> Generator[
	tuple[list[str], dict[str, str]],
	None,
	None,
]:
	with open(file_path, "r") as f:
		text = f.read()

	lines = text.split("\n")

	pending_key: str = None
	pending_value: str = None

	last_continue_line = False

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
		if line.endswith("\\"):
			line = line[:-1]

			if last_continue_line:
				pending_value = f"{pending_value}\n{line.strip()}"
			else:
				splits = line.split(":", 1)
				if len(splits) == 1:
					pending_value = line.strip()
				else:
					pending_key, pending_value = splits
					pending_key = pending_key.strip()
					pending_value = pending_value.strip()
			last_continue_line = True
			continue

		if last_continue_line:
			if pending_key is None:
				args.append(line.strip())
				pending_value = None
				last_continue_line = False
			else:
				kwargs[pending_key] = f"{pending_value}\n{line.strip()}"
				pending_key = None
				pending_value = None
			last_continue_line = False
		else:
			splits = line.split(":", 1)
			if len(splits) == 1:
				args.append(line.strip())
			else:
				key, value = splits
				kwargs[key.strip()] = value.strip()

	if args or kwargs:
		yield args.copy(), kwargs.copy()
