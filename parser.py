import argparse
import pandas as pd
import sys
from utils import get_column_stats, parse_phone, parse_company

def main():
    parser = argparse.ArgumentParser(description="Parse Phone or Company columns.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    
    args = parser.parse_args()
    
    try:
        df = pd.read_csv(args.input)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # 1. Detect Column Types
    col_scores = []
    for col in df.columns:
        stats = get_column_stats(df[col])
        best_type = max(stats, key=stats.get)
        if stats[best_type] > 0.2: # Confidence Threshold
            col_scores.append({"col": col, "type": best_type, "score": stats[best_type]})

    output_df = pd.DataFrame()
    processed_any = False

    # 2. Parse Phone Numbers
    phone_cols = sorted([x for x in col_scores if x['type'] == 'Phone Number'], key=lambda x: x['score'], reverse=True)
    if phone_cols:
        target_col = phone_cols[0]['col']
        parsed_data = df[target_col].apply(parse_phone)
        output_df["Phone Number"] = df[target_col]
        output_df["Country"] = parsed_data.apply(lambda x: x[0])
        output_df["Number"] = parsed_data.apply(lambda x: x[1])
        processed_any = True

    # 3. Parse Company Names
    comp_cols = sorted([x for x in col_scores if x['type'] == 'Company Name'], key=lambda x: x['score'], reverse=True)
    if comp_cols:
        target_col = comp_cols[0]['col']
        parsed_data = df[target_col].apply(parse_company)
        output_df["CompanyName"] = df[target_col]
        output_df["Name"] = parsed_data.apply(lambda x: x[0])
        output_df["Legal"] = parsed_data.apply(lambda x: x[1])
        processed_any = True

    # 4. Save Results
    if processed_any:
        output_df.to_csv("output.csv", index=False)
        print(f"File parsed successfully. Output saved to 'output.csv'")
    else:
        print("None")

if __name__ == "__main__":
    main()