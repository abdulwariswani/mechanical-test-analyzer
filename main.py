import sys, logging 
import pandas as pd
import os 


from src.data_loader import load_tensile_data
from src.preprocessing import clean_data
from src.analysis import IP_count



def get_path_from_the_arg():
    if len(sys.argv) >= 2:
        return sys.argv[1]
    logging.error("Usage: python main.py <file_path>")
    sys.exit(1)


            



def main():
    file_path: str = get_path_from_the_arg()


    try:
        raw_df = load_tensile_data(file_path)
        logging.info('success!')
    except ValueError or FileNotFoundError as e:
        logging.error(f"Error: {e}")
        sys.exit(1)

    directory = os.path.dirname('results/processed_6061.csv')
    directory = os.path.dirname('results/processed_6061.csv')
    if directory:
           os.makedirs(directory, exist_ok=True)
    

    processed_df, summary = clean_data(raw_df, width_mm=2.0, thickness_mm=2.0)
    processed_df.to_csv('results/processed_6061.csv', index=False)
    logging.info(summary)
    


if __name__ == "__main__":
    main()

    


