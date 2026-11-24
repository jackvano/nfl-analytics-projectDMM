import os
import pandas as pd
from pipeline.db import engine

PFR_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "pfr")

TEAM_NAME_TO_ABB = {
    "Arizona Cardinals": "ARI", "Atlanta Falcons": "ATL", "Baltimore Ravens": "BAL",
    "Buffalo Bills": "BUF", "Carolina Panthers": "CAR", "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLE", "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN", "Detroit Lions": "DET", "Green Bay Packers": "GB",
    "Houston Texans": "HOU", "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC", "Los Angeles Rams": "LA", "Los Angeles Chargers": "LAC",
    "Las Vegas Raiders": "LV", "Miami Dolphins": "MIA", "Minnesota Vikings": "MIN",
    "New England Patriots": "NE", "New Orleans Saints": "NO", "New York Giants": "NYG",
    "New York Jets": "NYJ", "Philadelphia Eagles": "PHI", "Pittsburgh Steelers": "PIT",
    "Seattle Seahawks": "SEA", "San Francisco 49ers": "SF", "Tampa Bay Buccaneers": "TB",
    "Tennessee Titans": "TEN", "Washington Commanders": "WAS",
}

TABLES = {
    "pfr_ratings": "ratings.csv",
}

def run():
    for table_name, filename in TABLES.items():
        path = os.path.join(PFR_DIR, filename)
        if not os.path.exists(path):
            print(f"  raw.{table_name} SKIPPED (no file at data/pfr/{filename})")
            continue
        try:
            df = pd.read_csv(path)
            if "team" in df.columns and df["team"].str.contains(" ").any():
                df["team"] = df["team"].str.replace(r"[*+]", "", regex=True).str.strip()
                df["team"] = df["team"].map(TEAM_NAME_TO_ABB).fillna(df["team"])
            df.to_sql(table_name, engine, schema="raw", if_exists="replace",
                      index=False, chunksize=50_000)
            print(f"  raw.{table_name}: {len(df):,} rows")
        except Exception as e:
            print(f"  raw.{table_name} FAILED: {e}")
