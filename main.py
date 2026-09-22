import sys
import logging

from src.data_loader import read_lines
from src.parser import parsed_log
from src.analysis import IP_count


def get_path_from_the_arg():
    if len(sys.argv) >= 2:
        return sys.argv[1]
    logging.error("Usage: python main.py <file_path>")
    sys.exit(1)


def main():
    path = get_path_from_the_arg()

    try:
        lines = read_lines(path)
    except FileNotFoundError:
        logging.error(f"Error: file {path} not found")
        sys.exit(1)

    records = parsed_log(lines)
    counts = IP_count(records)
    print(counts)


if __name__ == "__main__":
    main()

    


