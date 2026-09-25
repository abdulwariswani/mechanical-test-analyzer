import pandas as pd 
import pytest
from src.data_loader import load_tensile_data

# Test1: Missing columns raise error ---
def test_missing_columns_raises_error(tmp_path):
    # create a dummy dataframe missing force and strain 
    invalid_data = {
        'Time(s)': [1, 2, 3]
    }
    df =pd.DataFrame(invalid_data)
    # save it to a temporary csv file
    tmp_csv = tmp_path / "invalid_tensile.csv"
    df.to_csv(tmp_csv,index =False)

    # expect pytest to catch the error
    with pytest.raises(ValueError) as exc_info:
        load_tensile_data(tmp_csv)

    assert "Missing required columns" in str(exc_info.value)

