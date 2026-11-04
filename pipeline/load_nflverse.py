import nflreadpy as nfl
from pipeline.db import engine

SEASONS = [2023, 2024, 2025]

TABLES = {
    "players":      lambda: nfl.load_players(),
    "contracts":    lambda: nfl.load_contracts(),
    "draft_picks":  lambda: nfl.load_draft_picks(),
    "schedules":    lambda: nfl.load_schedules(SEASONS),
    "player_stats": lambda: nfl.load_player_stats(SEASONS),
    "snap_counts":  lambda: nfl.load_snap_counts(SEASONS),
    "pbp":          lambda: nfl.load_pbp(SEASONS),
}

def run():
    for name, loader in TABLES.items():
        try:
            df = loader().to_pandas()
            df.to_sql(name, engine, schema="raw", if_exists="replace",
                      index=False, chunksize=50_000)
            print(f"✓ raw.{name}: {len(df):,} rows")
        except Exception as e:
            print(f"✗ raw.{name} failed: {e}")