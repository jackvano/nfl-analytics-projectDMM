import os
import pandas as pd
from pipeline.db import engine

KAGGLE_DIR = os.getenv("KAGGLE_DIR", r"C:\Users\vanou\OneDrive\Desktop\databowl2027proj\nfl-big-data-bowl-2027")

SMALL_TABLES = ["players", "games", "combine_results", "player_career_successes", "player_play", "combine_tracking"]

def run():
    for name in SMALL_TABLES:
        try:
            df = pd.read_csv(os.path.join(KAGGLE_DIR, f"{name}.csv"))
            df.to_sql(f"kaggle_{name}", engine, schema="raw", if_exists="replace", index=False, chunksize=50_000)
            print(f"  raw.kaggle_{name}: {len(df):,} rows")
        except Exception as e:
            print(f"  raw.kaggle_{name} FAILED: {e}")
