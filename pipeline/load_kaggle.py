import os
import pandas as pd
from pipeline.db import engine

KAGGLE_DIR = os.getenv(
    "KAGGLE_DIR",
    r"C:\Users\vanou\OneDrive\Desktop\databowl2027proj\nfl-big-data-bowl-2027"
)

SMALL_TABLES = [
    "players",
    "games",
    "combine_results",
    "player_career_successes",
    "player_play",
    "combine_tracking",
]

def _load_csv(filename):
    return pd.read_csv(os.path.join(KAGGLE_DIR, filename))

def _load_game_tracking():
    dfs = []
    for year in [2023, 2024, 2025]:
        path = os.path.join(KAGGLE_DIR, f"game_tracking_{year}.csv")
        print(f"    reading game_tracking_{year}.csv ...")
        dfs.append(pd.read_csv(path))
    return pd.concat(dfs, ignore_index=True)

def run():
    for name in SMALL_TABLES:
        try:
            df = _load_csv(f"{name}.csv")
            df.to_sql(f"kaggle_{name}", engine, schema="raw", if_exists="replace",
                      index=False, chunksize=50_000)
            print(f"  raw.kaggle_{name}: {len(df):,} rows")
        except Exception as e:
            print(f"  raw.kaggle_{name} FAILED: {e}")

    try:
        df = _load_game_tracking()
        df.to_sql("kaggle_game_tracking", engine, schema="raw", if_exists="replace",
                  index=False, chunksize=50_000)
        print(f"  raw.kaggle_game_tracking: {len(df):,} rows")
    except Exception as e:
        print(f"  raw.kaggle_game_tracking FAILED: {e}")
