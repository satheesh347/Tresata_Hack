import argparse
import pandas as pd
import sys
from utils import get_column_type

def main():
    parser = argparse.ArgumentParser(description="Predict semantic type of a column.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--column", required=True, help="Column name to classify")

    args = parser.parse_args()

    try:
        # Load only the requested column to be efficient
        df = pd.read_csv(args.input, usecols=[args.column])
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Use the logic from utils.py
    prediction = get_column_type(df[args.column])

    # Map to the specific output format requested
    mapping = {
        "Phone Number": "phoneNumber",
        "Company Name": "companyName",
        "Country": "country",
        "Date": "date",
        "Other": "other"
    }
    
    print(mapping.get(prediction, prediction))

if __name__ == "__main__":
    main()