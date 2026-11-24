import nflreadpy as nfl
import json, numpy as np
from sqlalchemy import text
from pipeline.db import engine

SEASONS = [2023, 2024, 2025]
PG_RESERVED = {"pass", "name", "location", "by", "as", "case", "end", "in", "is", "of", "on", "or", "to"}

def _serialize_arrays(df):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map(lambda v: json.dumps(v, default=str) if isinstance(v, (np.ndarray, list)) else v)
    return df

def _rename_reserved(df):
    return df.rename(columns={c: f"{c}_" for c in df.columns if c.lower() in PG_RESERVED})

def load(name, loader):
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
        df.to_sql(name, engine, schema="raw", if_exists="replace", index=False, chunksize=50_000)
        print(f"  raw.{name}: {len(df):,} rows")
    except Exception as e:
        print(f"  raw.{name} FAILED: {e}")

load("pbp", lambda: nfl.load_pbp(SEASONS))
load("depth_charts", lambda: nfl.load_depth_charts(SEASONS))
print("Done")
