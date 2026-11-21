import json
import numpy as np
import nflreadpy as nfl
from sqlalchemy import text
from pipeline.db import engine

SEASONS = [2023, 2024, 2025]

TABLES = {
    "players":          lambda: nfl.load_players(),
    "contracts":        lambda: nfl.load_contracts(),
    "draft_picks":      lambda: nfl.load_draft_picks(),
    "schedules":        lambda: nfl.load_schedules(SEASONS),
    "rosters":          lambda: nfl.load_rosters(SEASONS),
    "rosters_weekly":   lambda: nfl.load_rosters_weekly(SEASONS),
    "player_stats":     lambda: nfl.load_player_stats(SEASONS),
    "snap_counts":      lambda: nfl.load_snap_counts(SEASONS),
    "pbp":              lambda: nfl.load_pbp(SEASONS),
    "injuries":         lambda: nfl.load_injuries(SEASONS),
    "depth_charts":     lambda: nfl.load_depth_charts(SEASONS),
}

PG_RESERVED = {"pass", "name", "location", "by", "as", "case", "end", "in", "is", "of", "on", "or", "to"}

def _rename_reserved(df):
    return df.rename(columns={c: f"{c}_" for c in df.columns if c.lower() in PG_RESERVED})

def _serialize_arrays(df):
    """Convert any object/array columns to JSON strings for Postgres compatibility."""
    for col in df.columns:
        if df[col].dtype == object:
            def _to_json(v):
                if isinstance(v, (np.ndarray, list)):
                    return json.dumps(v, default=str)
                return v
            df[col] = df[col].map(_to_json)
    return df

def run():
    for name, loader in TABLES.items():
        try:
            df = loader()
            if hasattr(df, "to_pandas"):
                df = df.to_pandas()
            df = _serialize_arrays(df)
            df = _rename_reserved(df)
            with engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS raw.{name} CASCADE"))
                conn.execute(text(f"DROP TYPE IF EXISTS raw.{name} CASCADE"))
                conn.commit()
            df.to_sql(name, engine, schema="raw", if_exists="replace",
                      index=False, chunksize=50_000)
            print(f"  raw.{name}: {len(df):,} rows")
        except Exception as e:
            print(f"  raw.{name} FAILED: {e}")
