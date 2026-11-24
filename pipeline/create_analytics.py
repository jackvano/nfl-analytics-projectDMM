from sqlalchemy import text
from pipeline.db import engine

STATEMENTS = [
    ("analytics schema", "CREATE SCHEMA IF NOT EXISTS analytics"),

    ("dim_player", """
CREATE OR REPLACE VIEW analytics.dim_player AS
SELECT gsis_id, display_name, position, position_group,
    birth_date, height, weight, college_name,
    draft_year, draft_round, draft_pick, draft_team,
    rookie_season, pfr_id, otc_id
FROM raw.players
"""),

    ("player_season_stats", """
CREATE OR REPLACE VIEW analytics.player_season_stats AS
SELECT
    player_id AS gsis_id, season, team, position,
    COUNT(*) AS games_played,
    SUM(completions) AS completions,
    SUM(attempts) AS attempts,
    SUM(passing_yards) AS passing_yards,
    SUM(passing_tds) AS passing_tds,
    SUM(passing_interceptions) AS passing_interceptions,
    AVG(passing_epa) AS passing_epa_avg,
    AVG(passing_cpoe) AS passing_cpoe_avg,
    SUM(carries) AS carries,
    SUM(rushing_yards) AS rushing_yards,
    SUM(rushing_tds) AS rushing_tds,
    AVG(rushing_epa) AS rushing_epa_avg,
    SUM(receptions) AS receptions,
    SUM(targets) AS targets,
    SUM(receiving_yards) AS receiving_yards,
    SUM(receiving_tds) AS receiving_tds,
    AVG(receiving_epa) AS receiving_epa_avg,
    AVG(target_share) AS target_share_avg,
    SUM(def_tackles_solo) AS def_tackles_solo,
    SUM(def_sacks) AS def_sacks,
    SUM(def_interceptions) AS def_interceptions,
    SUM(def_pass_defended) AS def_pass_defended,
    SUM(def_tackles_for_loss) AS def_tackles_for_loss,
    SUM(def_qb_hits) AS def_qb_hits,
    SUM(fantasy_points_ppr) AS fantasy_points_ppr
FROM raw.player_stats
WHERE season_type = 'REG'
GROUP BY player_id, season, team, position
"""),

    ("player_season_snaps", """
CREATE OR REPLACE VIEW analytics.player_season_snaps AS
SELECT pfr_player_id, season, team, position,
    SUM(offense_snaps) AS offense_snaps,
    SUM(defense_snaps) AS defense_snaps,
    SUM(st_snaps) AS st_snaps,
    AVG(offense_pct) AS offense_snap_pct,
    AVG(defense_pct) AS defense_snap_pct,
    AVG(st_pct) AS st_snap_pct
FROM raw.snap_counts
WHERE game_type = 'REG'
GROUP BY pfr_player_id, season, team, position
"""),

    ("dim_team_season", """
CREATE OR REPLACE VIEW analytics.dim_team_season AS
SELECT DISTINCT s.team, s.season, r.srs, r.osrs, r.dsrs
FROM (
    SELECT home_team AS team, season FROM raw.schedules WHERE season IS NOT NULL
    UNION
    SELECT away_team AS team, season FROM raw.schedules WHERE season IS NOT NULL
) s
LEFT JOIN raw.pfr_ratings r ON s.team = r.team AND s.season = r.season
"""),

    ("drop fact view", "DROP VIEW IF EXISTS analytics.fact_player_season CASCADE"),
    ("drop fact table", "DROP TABLE IF EXISTS analytics.fact_player_season CASCADE"),

    ("fact_player_season", """
CREATE TABLE analytics.fact_player_season AS
WITH active_contract AS (
    SELECT DISTINCT ON (gsis_id, s.season)
        gsis_id,
        year_signed AS contract_start,
        s.season,
        apy,
        value AS contract_value,
        guaranteed,
        years AS contract_years,
        apy_cap_pct
    FROM raw.contracts
    CROSS JOIN LATERAL generate_series(
        year_signed::int,
        (year_signed + years - 1)::int
    ) AS s(season)
    WHERE gsis_id IS NOT NULL AND years IS NOT NULL
    ORDER BY gsis_id, s.season, year_signed DESC
)
SELECT
    p.gsis_id, p.display_name, p.position, p.position_group,
    p.birth_date, p.draft_year, p.draft_round, p.draft_pick, p.draft_team, p.pfr_id,
    s.season, s.team, s.games_played,
    sn.offense_snaps, sn.defense_snaps, sn.offense_snap_pct, sn.defense_snap_pct,
    s.completions, s.attempts, s.passing_yards, s.passing_tds,
    s.passing_interceptions, s.passing_epa_avg, s.passing_cpoe_avg,
    s.carries, s.rushing_yards, s.rushing_tds, s.rushing_epa_avg,
    s.receptions, s.targets, s.receiving_yards, s.receiving_tds,
    s.receiving_epa_avg, s.target_share_avg,
    s.def_tackles_solo, s.def_sacks, s.def_interceptions,
    s.def_pass_defended, s.def_tackles_for_loss, s.def_qb_hits,
    s.fantasy_points_ppr,
    c.apy, c.contract_value, c.guaranteed, c.contract_years, c.apy_cap_pct, c.contract_start,
    t.srs, t.osrs, t.dsrs,
    dp.w_av, dp.car_av
FROM analytics.player_season_stats s
JOIN analytics.dim_player p ON s.gsis_id = p.gsis_id
LEFT JOIN analytics.player_season_snaps sn ON p.pfr_id = sn.pfr_player_id AND s.season = sn.season AND s.team = sn.team
LEFT JOIN active_contract c ON p.gsis_id = c.gsis_id AND s.season = c.season
LEFT JOIN analytics.dim_team_season t ON s.team = t.team AND s.season = t.season
LEFT JOIN raw.draft_picks dp ON p.pfr_id = dp.pfr_player_id
"""),
]

def run():
    for name, sql in STATEMENTS:
        try:
            with engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            print(f"  {name}: ok")
        except Exception as e:
            print(f"  {name} FAILED: {e}")

if __name__ == "__main__":
    run()
