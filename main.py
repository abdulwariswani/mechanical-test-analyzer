import sys, logging 
from pathlib import Path



from src.data_loader import load_tensile_data
from src.parser import parsed_log
from src.analysis import IP_count


def get_path_from_the_arg():
    if len(sys.argv) >= 2:
        return sys.argv[1]
    logging.error("Usage: python main.py <file_path>")
    sys.exit(1)

def check_for_csv(file_path):
    path_object= Path(file_path)
    if path_object.suffix.lower() != '.csv':
        logging.error("This is not a CSV file.")
        sys.exit(1)

    return path_object
            



def main():
    file_path = get_path_from_the_arg()
    csv_file = check_for_csv(file_path)


    try:
        missing_cols = load_tensile_data(csv_file)
        logging.info('success!')
    except ValueError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    

    #records = parsed_log(lines)
    #counts = IP_count(records)
    #print(counts)


if __name__ == "__main__":
    main()

    


