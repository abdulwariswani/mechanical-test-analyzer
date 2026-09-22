def read_lines(path):
    """Return the file's lines, stripped of trailing whitespace.

    Raises FileNotFoundError if `path` does not exist.
    """
    with open(path, 'r') as f:
        return [line.strip() for line in f]