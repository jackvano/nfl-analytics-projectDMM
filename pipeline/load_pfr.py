import os
import pandas as pd
from pipeline.db import engine

PFR_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "pfr")

TABLES = {
    "pfr_av":       "av.csv",
    "pfr_draft":    "draft.csv",
    "pfr_ratings":  "ratings.csv",
}

def run():
    for table_name, filename in TABLES.items():
        path = os.path.join(PFR_DIR, filename)
        if not os.path.exists(path):
            print(f"  raw.{table_name} SKIPPED (no file at data/pfr/{filename})")
            continue
        try:
            df = pd.read_csv(path)
            df.to_sql(table_name, engine, schema="raw", if_exists="replace",
                      index=False, chunksize=50_000)
            print(f"  raw.{table_name}: {len(df):,} rows")
        except Exception as e:
            print(f"  raw.{table_name} FAILED: {e}")
