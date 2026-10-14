import os
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# Database Connection Configuration
# Requirement: Relative path DB = '../data/ipl.db'
# ==============================================================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB = os.path.join(PROJECT_ROOT, 'data', 'ipl.db')

if not os.path.exists(DB):
    for candidate in [
        os.path.join(PROJECT_ROOT, '2_IPL_Cricket', 'ipl.db'),
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'ipl.db')),
        os.path.abspath(os.path.join(os.getcwd(), 'data', 'ipl.db')),
    ]:
        if os.path.exists(candidate):
            DB = candidate
            break


def q(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Helper function to execute SQL queries with parameters.
    Rule: All numbers come directly out of SQL via q(). Nothing is calculated in pandas.
    """
    with sqlite3.connect(DB) as conn:
        return pd.read_sql_query(sql, conn, params=params)


# Validate the database before rendering the dashboard.
try:
    with sqlite3.connect(DB) as _test_conn:
        _test_conn.execute("SELECT 1")
except Exception as _db_error:
    st.error(f"Database connection failed: {_db_error}")
    st.info(f"Database path: {DB}")
    st.stop()


# ==============================================================================
# Page Configuration & Clean Light-Theme + Forest Green Sidebar Styling
# ==============================================================================
st.set_page_config(
    page_title="IPL Bowling Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    /* Global Base */
    .stApp {
        background-color: #0B1020;
        color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Left Sidebar Styling - Deep Forest Green */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #243047;
    }
    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        background: transparent;
        gap: 6px;
    }
    [data-testid="stSidebar"] .stRadio label {
        background: transparent;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 500;
        font-size: 14px;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: #1E293B !important;
    }
    [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
        background: #312E81 !important;
        font-weight: 700;
        color: #FFFFFF !important;
    }

    /* Page Header */
    .page-title {
        font-size: 26px;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 2px;
        line-height: 1.2;
    }
    .page-subtitle {
        font-size: 13.5px;
        color: #94A3B8;
        margin-bottom: 14px;
        font-weight: 450;
    }

    /* Filter Strip Card */
    .filter-card {
        background: #111827;
        border: 1px solid #26324A;
        border-radius: 10px;
        padding: 10px 16px;
        margin-bottom: 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }

    /* Top KPI Metric Cards */
    .metric-card {
        background: #111827;
        border: 1px solid #26324A;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        min-height: 112px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-header {
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        color: #F8FAFC;
        margin-bottom: 6px;
    }
    .metric-num {
        font-size: 32px;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.1;
    }
    .metric-desc {
        font-size: 11.5px;
        color: #94A3B8;
        margin-top: 4px;
    }
    .metric-dual-flex {
        display: flex;
        align-items: baseline;
        gap: 28px;
    }

    /* Chart Container Card */
    .chart-card {
        background: #111827;
        border: 1px solid #26324A;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        margin-bottom: 14px;
    }
    .chart-card-title {
        font-size: 14px;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 8px;
    }

    /* Streamlit Input Styling Adjustments */
    .stSelectbox label, .stTextInput label, .stNumberInput label {
        font-size: 11.5px !important;
        font-weight: 600 !important;
        color: #CBD5E1 !important;
        margin-bottom: 2px !important;
    }
    div[data-baseweb="select"] > div {
        border-radius: 6px !important;
        border-color: #334155 !important;
        background-color: #111827 !important;
        min-height: 36px !important;
    }
    div[data-baseweb="input"] > div {
        border-radius: 6px !important;
        border-color: #334155 !important;
        background-color: #111827 !important;
        min-height: 36px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# Color Palette (Matching Clean Sage & Forest Green Design)
# ==============================================================================
DARK_GREEN = "#8B5CF6"    # Deep Forest Green / Pine
LIGHT_GREEN = "#22D3EE"   # Sage / Mint Green
MID_GREEN = "#6366F1"     # Mid Sage Green
LINE_COLOR = "#8B5CF6"    # Line color
LEAGUE_LINE = "#94A3B8"   # Slate dashed league line
CARD_BG = "#111827"


# ==============================================================================
# Left Sidebar Navigation (Matching exact UI in screenshot)
# ==============================================================================
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 10px 0 20px 4px;">
            <div style="font-size: 32px; font-weight: 900; color: #111827; letter-spacing: -0.5px;">IPL</div>
            <div style="font-size: 13px; color: #A5B4FC; margin-top: -3px; font-weight: 500;">2008 - 2026</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_selection = st.radio(
        "Navigation",
        ["📊 Bowlers Overview", "🎯 Individual Bowler"],
        index=0,
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div style="margin-top: 18px; padding-left: 6px; display: flex; flex-direction: column; gap: 14px; opacity: 0.65; font-size: 14px;">
            <div style="display: flex; align-items: center; gap: 10px; cursor: not-allowed;">
                <span>👤</span> <span>Matches</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px; cursor: not-allowed;">
                <span>🏟️</span> <span>Teams & Venues</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Common Database Queries
try:
    season_rows = q("SELECT DISTINCT season_id FROM v_ball ORDER BY season_id DESC;")
    db_seasons = [str(s) for s in season_rows["season_id"].tolist()] if not season_rows.empty else []
except Exception:
    db_seasons = []

if not db_seasons:
    db_seasons = [str(y) for y in range(2026, 2007, -1)]  # IPL seasons: 2008–2026

all_seasons_list = ["All Seasons"] + db_seasons

# Build team list from v_ball.bowling_team (actual data, not teams table which has stale names)
team_rows = q("SELECT DISTINCT bowling_team FROM v_ball WHERE bowling_team IS NOT NULL ORDER BY bowling_team ASC;")
all_teams_list = ["All Teams"] + [t for t in team_rows["bowling_team"].tolist() if t]

# Exact 5 style groups present in the data (Others = 0 balls, removed)
style_options_tab1 = [
    "All",
    "Right-arm pace",
    "Left-arm pace",
    "Right-arm off spin",
    "Left-arm orthodox",
    "Leg spin",
]

# Canonical CASE WHEN expression for the 5 style groups.
# Priority order matters: Legbreak/Wrist spin > Offbreak > Orthodox > Left arm pace > Right arm pace
# bowler_type uses 'Left arm' / 'Right arm' (with space), NOT 'Left%' / 'Right%'
STYLE_CASE = """
    CASE
        WHEN bowler_type LIKE '%Wrist spin%' OR bowler_type LIKE '%Legbreak%' OR bowler_type LIKE '%Googly%' THEN 'Leg spin'
        WHEN bowler_type LIKE '%Offbreak%' THEN 'Right-arm off spin'
        WHEN bowler_type LIKE '%Orthodox%' THEN 'Left-arm orthodox'
        WHEN bowler_type LIKE '%Left arm%' AND (bowler_type LIKE '%Fast%' OR bowler_type LIKE '%Medium%') THEN 'Left-arm pace'
        WHEN bowler_type LIKE '%Right arm%' AND (bowler_type LIKE '%Fast%' OR bowler_type LIKE '%Medium%') THEN 'Right-arm pace'
        ELSE 'Others'
    END
"""

# Spin vs Pace CASE (used in Screen 1 hero chart and Screen 2 style filter)
SPIN_CASE = """
    CASE WHEN bowler_type LIKE '%Legbreak%'
              OR bowler_type LIKE '%Offbreak%'
              OR bowler_type LIKE '%Orthodox%'
              OR bowler_type LIKE '%Googly%'
              OR bowler_type LIKE '%Wrist spin%'
         THEN 'Spin' ELSE 'Pace' END
"""

# Condition to exclude NULL / blank / space bowler_type rows
BT_NOT_BLANK = "trim(coalesce(bowler_type, '')) NOT IN ('', ' ')"


# ==============================================================================
# SCREEN 1: BOWLERS OVERVIEW
# ==============================================================================
if nav_selection == "📊 Bowlers Overview":
    st.markdown('<div class="page-title">Bowlers Overview</div>', unsafe_allow_html=True)
    # Requirement 15: Named reader sentence visible on dashboard
    st.markdown(
        '<div class="page-subtitle">For the bowling coach, deciding which bowler to pick and for which overs</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------------------------
    # Filter Bar
    # --------------------------------------------------------------------------
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    fc1, fc2, fc3, fc4 = st.columns(4)

    with fc1:
        sel_seasons_s1 = st.multiselect(
            "Season",
            all_seasons_list,
            default=["All Seasons"],
            key="s1_season",
            help="Choose one or more seasons. Select All Seasons to include every year.",
        )
        selected_years_s1 = sorted(
            [int(year) for year in sel_seasons_s1 if year != "All Seasons"]
        )
        param_season_s1 = ",".join(map(str, selected_years_s1)) if selected_years_s1 else None

    with fc2:
        sel_style_s1 = st.selectbox("Bowling Style", style_options_tab1, index=0, key="s1_style")
        param_style_s1 = None if sel_style_s1 == "All" else sel_style_s1

    with fc3:
        min_balls_s1 = st.selectbox("Minimum Balls", [100, 200, 300, 500], index=0, key="s1_min_balls")

    with fc4:
        sel_team_s1 = st.selectbox("Team", all_teams_list, index=0, key="s1_team")
        param_team_s1 = None if sel_team_s1 == "All Teams" else sel_team_s1

    st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # Contextual Filter Detail Strip — visible only when any filter is active
    # --------------------------------------------------------------------------
    any_filter_active = param_season_s1 or param_team_s1 or param_style_s1

    if any_filter_active:
        # Build a human-readable label for the active context
        ctx_parts = []
        if param_season_s1:
            ctx_parts.append("Seasons " + param_season_s1.replace(",", ", "))
        if param_team_s1:
            ctx_parts.append(param_team_s1)
        if param_style_s1:
            ctx_parts.append(param_style_s1)
        ctx_label = "  ·  ".join(ctx_parts)

        # Pull live stats for the current filter context
        ctx_df = q(
            f"""
            SELECT
                COUNT(DISTINCT match_id)   AS matches,
                COUNT(DISTINCT bowler)     AS bowlers,
                SUM(is_legal)              AS balls,
                SUM(bowler_wicket)         AS wickets,
                ROUND(6.0 * SUM(bowler_runs) / NULLIF(SUM(is_legal), 0), 2) AS economy
            FROM v_ball
            WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
              AND (? IS NULL OR bowling_team = ?)
              AND (? IS NULL OR ({STYLE_CASE} = ?));
            """,
            (
                param_season_s1, param_season_s1,
                param_team_s1,   param_team_s1,
                param_style_s1,  param_style_s1,
            ),
        )

        # Top bowler for the context (by wickets)
        top_df = q(
            f"""
            SELECT bowler, SUM(bowler_wicket) AS wkts
            FROM v_ball
            WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
              AND (? IS NULL OR bowling_team = ?)
              AND (? IS NULL OR ({STYLE_CASE} = ?))
            GROUP BY bowler
            ORDER BY wkts DESC
            LIMIT 1;
            """,
            (
                param_season_s1, param_season_s1,
                param_team_s1,   param_team_s1,
                param_style_s1,  param_style_s1,
            ),
        )

        # Extract values safely
        ctx_matches = int(ctx_df["matches"].iloc[0]) if not ctx_df.empty and pd.notnull(ctx_df["matches"].iloc[0]) else 0
        ctx_bowlers = int(ctx_df["bowlers"].iloc[0]) if not ctx_df.empty and pd.notnull(ctx_df["bowlers"].iloc[0]) else 0
        ctx_balls   = int(ctx_df["balls"].iloc[0])   if not ctx_df.empty and pd.notnull(ctx_df["balls"].iloc[0]) else 0
        ctx_wkts    = int(ctx_df["wickets"].iloc[0]) if not ctx_df.empty and pd.notnull(ctx_df["wickets"].iloc[0]) else 0
        ctx_econ    = float(ctx_df["economy"].iloc[0]) if not ctx_df.empty and pd.notnull(ctx_df["economy"].iloc[0]) else 0.0
        ctx_top     = f"{top_df['bowler'].iloc[0]} ({int(top_df['wkts'].iloc[0])} wkts)" if not top_df.empty else "—"
        ctx_overs   = ctx_balls // 6

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #111827 0%, #312E81 100%);
                border-radius: 8px;
                padding: 10px 18px;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 0;
                flex-wrap: wrap;
            ">
                <div style="color:#A5B4FC; font-size:11px; font-weight:700;
                            letter-spacing:0.6px; text-transform:uppercase;
                            margin-right:16px; white-space:nowrap; padding-right:16px;
                            border-right:1px solid rgba(255,255,255,0.15);">
                    🔍 {ctx_label}
                </div>
                <div style="display:flex; gap:0; flex-wrap:wrap; flex:1; align-items:center;">
                    <div style="padding:0 18px 0 0; margin-right:18px;
                                border-right:1px solid rgba(255,255,255,0.12);">
                        <div style="color:#fff; font-size:18px; font-weight:800; line-height:1.1;">{ctx_matches:,}</div>
                        <div style="color:#A5B4FC; font-size:10px; font-weight:600;
                                    letter-spacing:0.4px; text-transform:uppercase;">Matches</div>
                    </div>
                    <div style="padding:0 18px 0 0; margin-right:18px;
                                border-right:1px solid rgba(255,255,255,0.12);">
                        <div style="color:#fff; font-size:18px; font-weight:800; line-height:1.1;">{ctx_bowlers:,}</div>
                        <div style="color:#A5B4FC; font-size:10px; font-weight:600;
                                    letter-spacing:0.4px; text-transform:uppercase;">Bowlers</div>
                    </div>
                    <div style="padding:0 18px 0 0; margin-right:18px;
                                border-right:1px solid rgba(255,255,255,0.12);">
                        <div style="color:#fff; font-size:18px; font-weight:800; line-height:1.1;">{ctx_overs:,}</div>
                        <div style="color:#A5B4FC; font-size:10px; font-weight:600;
                                    letter-spacing:0.4px; text-transform:uppercase;">Overs</div>
                    </div>
                    <div style="padding:0 18px 0 0; margin-right:18px;
                                border-right:1px solid rgba(255,255,255,0.12);">
                        <div style="color:#fff; font-size:18px; font-weight:800; line-height:1.1;">{ctx_wkts:,}</div>
                        <div style="color:#A5B4FC; font-size:10px; font-weight:600;
                                    letter-spacing:0.4px; text-transform:uppercase;">Wickets</div>
                    </div>
                    <div style="padding:0 18px 0 0; margin-right:18px;
                                border-right:1px solid rgba(255,255,255,0.12);">
                        <div style="color:#fff; font-size:18px; font-weight:800; line-height:1.1;">{ctx_econ:.2f}</div>
                        <div style="color:#A5B4FC; font-size:10px; font-weight:600;
                                    letter-spacing:0.4px; text-transform:uppercase;">Avg Economy</div>
                    </div>
                    <div>
                        <div style="color:#fff; font-size:14px; font-weight:700; line-height:1.2;">{ctx_top}</div>
                        <div style="color:#A5B4FC; font-size:10px; font-weight:600;
                                    letter-spacing:0.4px; text-transform:uppercase;">Top Bowler</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------------------------
    # Top Metric Cards Strip (Exactly 3 Cards)

    # --------------------------------------------------------------------------
    mc1, mc2, mc3 = st.columns(3)

    # Card 1: BOWLERS (Total bowlers & Qualified bowlers)
    card1_df = q(
        f"""
        SELECT
            COUNT(DISTINCT bowler) AS total_bowlers,
            COUNT(DISTINCT CASE WHEN balls >= ? THEN bowler END) AS qualified_bowlers
        FROM (
            SELECT bowler, SUM(is_legal) AS balls
            FROM v_ball
            WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
              AND (? IS NULL OR bowling_team = ?)
              AND (? IS NULL OR ({STYLE_CASE} = ?))
            GROUP BY bowler
        );
        """,
        (
            min_balls_s1,
            param_season_s1, param_season_s1,
            param_team_s1, param_team_s1,
            param_style_s1, param_style_s1,
        ),
    )
    tot_bowlers = int(card1_df["total_bowlers"].iloc[0]) if not card1_df.empty else 0
    qual_bowlers = int(card1_df["qualified_bowlers"].iloc[0]) if not card1_df.empty else 0

    with mc1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-header">BOWLERS</div>
                <div class="metric-dual-flex">
                    <div>
                        <div class="metric-num">{tot_bowlers:,}</div>
                        <div class="metric-desc">Total bowlers</div>
                    </div>
                    <div>
                        <div class="metric-num">{qual_bowlers:,}</div>
                        <div class="metric-desc">Qualified bowlers (≥ {min_balls_s1} balls)</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Card 2: TOTAL WICKETS (Credited to bowlers, fully reactive to season, team, and style filters)
    card2_df = q(
        f"""
        SELECT SUM(bowler_wicket) AS bowler_wickets
        FROM v_ball
        WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
          AND (? IS NULL OR bowling_team = ?)
          AND (? IS NULL OR ({STYLE_CASE} = ?));
        """,
        (
            param_season_s1, param_season_s1,
            param_team_s1, param_team_s1,
            param_style_s1, param_style_s1,
        ),
    )
    tot_wickets_all = int(card2_df["bowler_wickets"].iloc[0]) if not card2_df.empty and pd.notnull(card2_df["bowler_wickets"].iloc[0]) else 0

    filters_applied = []
    if param_season_s1:
        filters_applied.append(param_season_s1.replace(",", ", "))
    if param_team_s1:
        filters_applied.append(param_team_s1)
    if param_style_s1:
        filters_applied.append(param_style_s1)
    c2_desc = f"Credited to bowlers ({', '.join(filters_applied)})" if filters_applied else "Credited to bowlers (All seasons)"

    with mc2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-header">TOTAL WICKETS</div>
                <div class="metric-num">{tot_wickets_all:,}</div>
                <div class="metric-desc">{c2_desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Card 3: SPIN vs PACE (Tested finding + reactive economy for active filters)
    card3_df = q(
        f"""
        SELECT
            {SPIN_CASE} AS bowling_style,
            ROUND(6.0 * SUM(bowler_runs) / NULLIF(SUM(is_legal), 0), 2) AS economy
        FROM v_ball
        WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
          AND (? IS NULL OR bowling_team = ?)
          AND {BT_NOT_BLANK}
        GROUP BY bowling_style;
        """,
        (param_season_s1, param_season_s1, param_team_s1, param_team_s1),
    )
    spin_econ_val = 7.70
    pace_econ_val = 8.49
    if not card3_df.empty:
        for _, r in card3_df.iterrows():
            if r["bowling_style"] == "Spin" and pd.notnull(r["economy"]):
                spin_econ_val = float(r["economy"])
            elif r["bowling_style"] == "Pace" and pd.notnull(r["economy"]):
                pace_econ_val = float(r["economy"])

    with mc3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-header">SPIN vs PACE</div>
                <div style="font-size: 14.5px; font-weight: 700; color: #F8FAFC; margin-top: 2px;">
                    Spin {spin_econ_val:.2f} vs Pace {pace_econ_val:.2f}
                </div>
                <div class="metric-desc" style="font-weight: 500;">
                    Economy rate calculated from the selected data
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # --------------------------------------------------------------------------
    # Visual 1 (The Hero): Economy by Phase of the Innings — Spin vs Pace
    # --------------------------------------------------------------------------
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chart-card-title">Economy by Phase of the Innings — Spin vs Pace</div>',
        unsafe_allow_html=True,
    )

    hero_phase_df = q(
        f"""
        SELECT
            CASE phase
                WHEN 'Powerplay' THEN 'Powerplay (1–6)'
                WHEN 'Middle' THEN 'Middle Overs (7–15)'
                ELSE 'Death Overs (16–20)'
            END AS phase_label,
            {SPIN_CASE} AS bowling_style,
            ROUND(6.0 * SUM(bowler_runs) / NULLIF(SUM(is_legal), 0), 2) AS economy,
            SUM(is_legal) AS balls_bowled
        FROM v_ball
        WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
          AND (? IS NULL OR bowling_team = ?)
          AND {BT_NOT_BLANK}
        GROUP BY phase_label, bowling_style
        ORDER BY CASE phase_label
            WHEN 'Powerplay (1–6)' THEN 1
            WHEN 'Middle Overs (7–15)' THEN 2
            ELSE 3 END, bowling_style;
        """,
        (param_season_s1, param_season_s1, param_team_s1, param_team_s1),
    )

    overall_econ_s1 = q(
        """
        SELECT ROUND(6.0 * SUM(bowler_runs) / SUM(is_legal), 2) AS econ
        FROM v_ball
        WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
          AND (? IS NULL OR bowling_team = ?);
        """,
        (param_season_s1, param_season_s1, param_team_s1, param_team_s1),
    )
    league_ref_s1 = float(overall_econ_s1["econ"].iloc[0]) if not overall_econ_s1.empty and pd.notnull(overall_econ_s1["econ"].iloc[0]) else 8.25

    fig_hero_s1 = px.bar(
        hero_phase_df,
        x="phase_label",
        y="economy",
        color="bowling_style",
        barmode="group",
        category_orders={"phase_label": ["Powerplay (1–6)", "Middle Overs (7–15)", "Death Overs (16–20)"]},
        color_discrete_map={"Spin": DARK_GREEN, "Pace": LIGHT_GREEN},
        labels={"economy": "Economy Rate", "phase_label": "", "bowling_style": ""},
        text="economy",
    )
    fig_hero_s1.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
        width=0.28,
    )
    fig_hero_s1.add_hline(
        y=league_ref_s1,
        line_dash="dash",
        line_color=LEAGUE_LINE,
        annotation_text="--- League Average",
        annotation_position="top right",
        annotation_font=dict(color=LEAGUE_LINE, size=11),
    )
    fig_hero_s1.update_layout(
        template="plotly_dark",
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
            font=dict(color="#E5E7EB"),
        height=320,
        margin=dict(l=30, r=30, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(range=[0, 13], dtick=2, title="Economy Rate (Runs per 6 Legal Balls)", gridcolor="#243047"),
        xaxis=dict(title="Innings Phase", gridcolor="#243047"),
    )
    st.plotly_chart(fig_hero_s1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # Middle Row: Visual 2 (Economy by Bowling Style) & Visual 3 (Wickets by Innings Phase)
    # --------------------------------------------------------------------------
    m_row_col1, m_row_col2 = st.columns(2)

    with m_row_col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-card-title">Economy by Bowling Style</div>',
            unsafe_allow_html=True,
        )
        style_econ_df = q(
            f"""
            SELECT
                {STYLE_CASE} AS style_group,
                ROUND(6.0 * SUM(bowler_runs) / NULLIF(SUM(is_legal), 0), 2) AS economy,
                SUM(is_legal) AS balls
            FROM v_ball
            WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
              AND (? IS NULL OR bowling_team = ?)
              AND (? IS NULL OR ({STYLE_CASE} = ?))
              AND {BT_NOT_BLANK}
            GROUP BY style_group
            HAVING SUM(is_legal) >= 20
            ORDER BY economy ASC;
            """,
            (
                param_season_s1, param_season_s1,
                param_team_s1, param_team_s1,
                param_style_s1, param_style_s1,
            ),
        )

        fig_style_econ = px.bar(
            style_econ_df,
            x="economy",
            y="style_group",
            orientation="h",
            text="economy",
            labels={"economy": "", "style_group": ""},
        )
        fig_style_econ.update_traces(
            marker_color=DARK_GREEN,
            texttemplate="%{text:.2f}",
            textposition="inside",
        )
        fig_style_econ.update_layout(
            template="plotly_dark",
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font=dict(color="#E5E7EB"),
            height=250,
            margin=dict(l=10, r=20, t=10, b=10),
            yaxis=dict(autorange="reversed", title="Bowling Style"),
            xaxis=dict(title="Economy Rate (Runs per 6 Legal Balls)", range=[0, 10], dtick=2, gridcolor="#243047"),
        )
        st.plotly_chart(fig_style_econ, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with m_row_col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-card-title">Wickets by Innings Phase</div>',
            unsafe_allow_html=True,
        )
        phase_wkts_df = q(
            f"""
            SELECT
                CASE phase
                    WHEN 'Powerplay' THEN 'Powerplay (1–6)'
                    WHEN 'Middle' THEN 'Middle Overs (7–15)'
                    ELSE 'Death Overs (16–20)'
                END AS phase_label,
                SUM(bowler_wicket) AS wickets
            FROM v_ball
            WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
              AND (? IS NULL OR bowling_team = ?)
              AND (? IS NULL OR ({STYLE_CASE} = ?))
            GROUP BY phase_label
            ORDER BY CASE phase_label
                WHEN 'Powerplay (1–6)' THEN 1
                WHEN 'Middle Overs (7–15)' THEN 2
                ELSE 3 END;
            """,
            (
                param_season_s1, param_season_s1,
                param_team_s1, param_team_s1,
                param_style_s1, param_style_s1,
            ),
        )

        fig_phase_wkts = px.bar(
            phase_wkts_df,
            x="phase_label",
            y="wickets",
            text="wickets",
            color="phase_label",
            color_discrete_sequence=[DARK_GREEN, MID_GREEN, LIGHT_GREEN],
            labels={"wickets": "", "phase_label": ""},
        )
        fig_phase_wkts.update_traces(
            texttemplate="%{y:,}",
            textposition="outside",
            width=0.45,
        )
        fig_phase_wkts.update_layout(
            template="plotly_dark",
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font=dict(color="#E5E7EB"),
            height=250,
            showlegend=False,
            margin=dict(l=20, r=20, t=10, b=10),
            yaxis=dict(title="Wickets", gridcolor="#243047"),
            xaxis=dict(title="Innings Phase", gridcolor="#243047"),
        )
        st.plotly_chart(fig_phase_wkts, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # Bottom Row: Visual 4 (Dot-ball Share by Style) & Visual 5 (Economy Trend by Season)
    # --------------------------------------------------------------------------
    b_row_col1, b_row_col2 = st.columns(2)

    with b_row_col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-card-title">Dot-ball Share by Bowling Style</div>',
            unsafe_allow_html=True,
        )
        dot_style_df = q(
            f"""
            SELECT
                {STYLE_CASE} AS style_group,
                ROUND(100.0 * SUM(CASE WHEN total_runs = 0 THEN 1 ELSE 0 END) / NULLIF(SUM(is_legal), 0), 1) AS dot_ball_pct
            FROM v_ball
            WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
              AND (? IS NULL OR bowling_team = ?)
              AND (? IS NULL OR ({STYLE_CASE} = ?))
              AND {BT_NOT_BLANK}
            GROUP BY style_group
            HAVING SUM(is_legal) >= 20
            ORDER BY dot_ball_pct DESC;
            """,
            (
                param_season_s1, param_season_s1,
                param_team_s1, param_team_s1,
                param_style_s1, param_style_s1,
            ),
        )

        fig_dot_style = px.bar(
            dot_style_df,
            x="dot_ball_pct",
            y="style_group",
            orientation="h",
            text="dot_ball_pct",
            labels={"dot_ball_pct": "", "style_group": ""},
        )
        fig_dot_style.update_traces(
            marker_color=DARK_GREEN,
            texttemplate="%{text:.1f}%",
            textposition="inside",
        )
        fig_dot_style.update_layout(
            template="plotly_dark",
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font=dict(color="#E5E7EB"),
            height=250,
            margin=dict(l=10, r=20, t=10, b=10),
            yaxis=dict(autorange="reversed", title="Bowling Style"),
            xaxis=dict(title="Dot-ball Share (%)", range=[0, 45], dtick=10, gridcolor="#243047"),
        )
        st.plotly_chart(fig_dot_style, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with b_row_col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-card-title">Economy Trend by Season</div>',
            unsafe_allow_html=True,
        )
        season_trend_df = q(
            f"""
            SELECT
                CAST(season_id AS INTEGER) AS season,
                ROUND(6.0 * SUM(bowler_runs) / NULLIF(SUM(is_legal), 0), 2) AS economy
            FROM v_ball
            WHERE CAST(season_id AS INTEGER) BETWEEN 2008 AND 2026
              AND (? IS NULL OR bowling_team = ?)
              AND (? IS NULL OR ({STYLE_CASE} = ?))
            GROUP BY CAST(season_id AS INTEGER)
            ORDER BY CAST(season_id AS INTEGER) ASC;
            """,
            (
                param_team_s1, param_team_s1,
                param_style_s1, param_style_s1,
            ),
        )
        if not season_trend_df.empty:
            season_trend_df["season"] = pd.to_numeric(
                season_trend_df["season"], errors="coerce"
            )
            season_trend_df = season_trend_df.dropna(subset=["season"])
            season_trend_df["season"] = season_trend_df["season"].astype(int)
            season_trend_df = season_trend_df[
                season_trend_df["season"].between(2008, 2026)
            ]

        fig_season_trend = px.line(
            season_trend_df,
            x="season",
            y="economy",
            markers=True,
            labels={"season": "", "economy": ""},
        )
        fig_season_trend.update_traces(
            line=dict(color=DARK_GREEN, width=2.5),
            marker=dict(size=7, color=DARK_GREEN),
        )
        if selected_years_s1:
            sel_season_pt = season_trend_df[season_trend_df["season"].isin(selected_years_s1)]
            if not sel_season_pt.empty:
                fig_season_trend.add_trace(
                    go.Scatter(
                        x=sel_season_pt["season"],
                        y=sel_season_pt["economy"],
                        mode="markers",
                        name="Selected Seasons",
                        marker=dict(size=10, color="#F59E0B", symbol="diamond"),
                        hovertemplate="%{x}: %{y:.2f} RPO<extra></extra>",
                    )
                )
        fig_season_trend.update_layout(
            template="plotly_dark",
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font=dict(color="#E5E7EB"),
            height=250,
            margin=dict(l=20, r=20, t=10, b=10),
            yaxis=dict(range=[6, 10.5], dtick=1, title="Economy Rate (Runs per 6 Legal Balls)", gridcolor="#243047"),
            xaxis=dict(title="IPL Season (2008–2026)", type="linear", range=[2008, 2026], autorange=False, tickmode="array", tickvals=list(range(2008, 2027, 2)), ticktext=[str(y) for y in range(2008, 2027, 2)], gridcolor="#243047"),
        )
        st.plotly_chart(fig_season_trend, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================



    # --------------------------------------------------------------------------
    # Data Tables 1–3 — all respond to the selected season and overview filters
    # --------------------------------------------------------------------------
    st.markdown('<div class="section-title">Bowling Data Tables</div>', unsafe_allow_html=True)

    selected_season_label = (
        ("Seasons " + param_season_s1.replace(",", ", ")) if param_season_s1 is not None else "All Seasons"
    )
    st.caption(
        f"Showing bowling details for {selected_season_label}. Change the Season filter above "
        "to refresh these tables."
    )

    st.markdown('<div class="chart-card-title">Table 1 — All Bowlers and Their Season Details</div>', unsafe_allow_html=True)
    season_bowlers_table = q(
        f"""
        SELECT
            bowler AS "Bowler",
            ({STYLE_CASE}) AS "Bowling Style",
            SUM(bowler_wicket) AS "Credited Wickets",
            SUM(is_legal) AS "Legal Balls",
            ROUND(SUM(bowler_runs), 0) AS "Bowler Runs",
            ROUND(6.0 * SUM(bowler_runs) / NULLIF(SUM(is_legal), 0), 2) AS "Economy Rate",
            ROUND(
                100.0 * SUM(CASE WHEN total_runs = 0 AND is_legal = 1 THEN 1 ELSE 0 END)
                / NULLIF(SUM(is_legal), 0), 1
            ) AS "Dot-ball Share (%)"
        FROM v_ball
        WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
          AND (? IS NULL OR bowling_team = ?)
          AND (? IS NULL OR ({STYLE_CASE} = ?))
          AND TRIM(COALESCE(bowler_type, '')) <> ''
        GROUP BY bowler
        HAVING SUM(is_legal) >= ?
        ORDER BY SUM(bowler_wicket) DESC, "Economy Rate" ASC, bowler ASC;
        """,
        (param_season_s1, param_season_s1,
         param_team_s1, param_team_s1,
         param_style_s1, param_style_s1,
         int(min_balls_s1)),
    )
    st.dataframe(season_bowlers_table, use_container_width=True, hide_index=True)
    st.caption(
        f"{len(season_bowlers_table)} bowlers shown; minimum {min_balls_s1} legal balls. "
        "The table is not limited to the top 10 and updates when Season, Team, Bowling Style, "
        "or Minimum Balls changes."
    )

    tbl_col1, tbl_col2 = st.columns(2)
    with tbl_col1:
        st.markdown('<div class="chart-card-title">Table 2 — Wickets by Innings Phase</div>', unsafe_allow_html=True)
        wickets_phase_table = q(
            f"""
            SELECT
                phase AS "Innings Phase",
                SUM(bowler_wicket) AS "Credited Wickets",
                SUM(is_legal) AS "Legal Balls"
            FROM v_ball
            WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
              AND (? IS NULL OR bowling_team = ?)
              AND (? IS NULL OR ({STYLE_CASE} = ?))
            GROUP BY phase
            ORDER BY CASE phase
                WHEN 'Powerplay' THEN 1
                WHEN 'Middle' THEN 2
                WHEN 'Death' THEN 3
                ELSE 4
            END;
            """,
            (param_season_s1, param_season_s1,
             param_team_s1, param_team_s1,
             param_style_s1, param_style_s1),
        )
        st.dataframe(wickets_phase_table, use_container_width=True, hide_index=True)
        st.caption("Credited wickets and legal balls by phase for the selected season and filters.")

    with tbl_col2:
        st.markdown('<div class="chart-card-title">Table 3 — Economy by Bowling Style</div>', unsafe_allow_html=True)
        economy_style_table = q(
            f"""
            SELECT
                ({STYLE_CASE}) AS "Bowling Style",
                COUNT(DISTINCT bowler) AS "Bowlers",
                SUM(is_legal) AS "Legal Balls",
                ROUND(6.0 * SUM(bowler_runs) / NULLIF(SUM(is_legal), 0), 2) AS "Economy Rate"
            FROM v_ball
            WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
              AND (? IS NULL OR bowling_team = ?)
              AND (? IS NULL OR ({STYLE_CASE} = ?))
              AND TRIM(COALESCE(bowler_type, '')) <> ''
            GROUP BY ({STYLE_CASE})
            ORDER BY "Economy Rate" ASC;
            """,
            (param_season_s1, param_season_s1,
             param_team_s1, param_team_s1,
             param_style_s1, param_style_s1),
        )
        st.dataframe(economy_style_table, use_container_width=True, hide_index=True)
        st.caption("Economy is bowler-conceded runs per six legal balls; counts update with the active filters.")
# SCREEN 2: INDIVIDUAL BOWLER
# ==============================================================================
else:
    st.markdown('<div class="page-title">Individual Bowler</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Evaluate one bowler and decide which overs to use</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------------------------
    # Filter Bar
    # --------------------------------------------------------------------------
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    ifc1, ifc2, ifc3, ifc4, ifc5 = st.columns([2.5, 1.5, 1.5, 1.5, 1.5])

    with ifc2:
        sel_seasons_s2 = st.multiselect(
            "Season",
            all_seasons_list,
            default=["All Seasons"],
            key="s2_season",
            help="Choose one or more seasons. Select All Seasons to include every year.",
        )
        selected_years_s2 = sorted(
            [int(year) for year in sel_seasons_s2 if year != "All Seasons"]
        )
        param_season_s2 = ",".join(map(str, selected_years_s2)) if selected_years_s2 else None

    with ifc3:
        sel_style_s2 = st.selectbox("Bowling Style", ["All", "Spin", "Pace"], index=0, key="s2_style")
        param_style_s2 = None if sel_style_s2 == "All" else sel_style_s2

    with ifc4:
        min_balls_s2 = st.selectbox("Minimum Balls", [100, 200, 300, 500, 0], index=0, key="s2_min_balls")

    with ifc5:
        min_wkts_s2 = st.selectbox("Minimum Wickets", [0, 5, 10, 25, 50], index=0, key="s2_min_wkts")

    # Dynamic query to narrow bowler candidates based on filters
    bowler_list_df = q(
        f"""
        SELECT DISTINCT b.bowler
        FROM (
            SELECT
                bowler,
                {SPIN_CASE} AS style,
                SUM(is_legal) AS balls,
                SUM(bowler_wicket) AS wickets
            FROM v_ball
            WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
              AND {BT_NOT_BLANK}
            GROUP BY bowler
            HAVING SUM(is_legal) >= ? AND SUM(bowler_wicket) >= ?
        ) b
        WHERE (? IS NULL OR b.style = ?)
        ORDER BY b.wickets DESC, b.bowler ASC;
        """,
        (
            param_season_s2, param_season_s2,
            min_balls_s2,
            min_wkts_s2,
            param_style_s2, param_style_s2,
        ),
    )
    all_bowler_candidates = bowler_list_df["bowler"].tolist() if not bowler_list_df.empty else []

    with ifc1:
        if not all_bowler_candidates:
            st.warning("No bowlers matched criteria. Showing top available bowlers.")
            fallback_df = q(
                """
                SELECT DISTINCT bowler
                FROM v_ball
                WHERE (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
                GROUP BY bowler
                ORDER BY SUM(bowler_wicket) DESC, bowler ASC
                LIMIT 50;
                """,
                (param_season_s2, param_season_s2),
            )
            all_bowler_candidates = fallback_df["bowler"].tolist() if not fallback_df.empty else ["YS Chahal"]

        default_idx = 0
        for fav in ["YS Chahal", "JJ Bumrah", "B Kumar", "SP Narine", "Rashid Khan"]:
            if fav in all_bowler_candidates:
                default_idx = all_bowler_candidates.index(fav)
                break
        selected_bowler = st.selectbox("Search Bowler", all_bowler_candidates, index=default_idx, key="s2_bowler")

    st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # Top Metric Cards Strip (Exactly 3 Cards)
    # --------------------------------------------------------------------------
    bmc1, bmc2, bmc3 = st.columns(3)

    b_stats_df = q(
        """
        SELECT
            SUM(bowler_wicket) AS wickets,
            SUM(is_legal) AS balls,
            ROUND(6.0 * SUM(bowler_runs) / NULLIF(SUM(is_legal), 0), 2) AS economy,
            ROUND(100.0 * SUM(CASE WHEN total_runs = 0 THEN 1 ELSE 0 END) / NULLIF(SUM(is_legal), 0), 1) AS dot_ball_pct,
            SUM(CASE WHEN total_runs = 0 THEN 1 ELSE 0 END) AS dot_balls
        FROM v_ball
        WHERE bowler = ?
          AND (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0);
        """,
        (selected_bowler, param_season_s2, param_season_s2),
    )
    b_wkts = int(b_stats_df["wickets"].iloc[0]) if not b_stats_df.empty and pd.notnull(b_stats_df["wickets"].iloc[0]) else 0
    b_balls = int(b_stats_df["balls"].iloc[0]) if not b_stats_df.empty and pd.notnull(b_stats_df["balls"].iloc[0]) else 0
    b_econ = float(b_stats_df["economy"].iloc[0]) if not b_stats_df.empty and pd.notnull(b_stats_df["economy"].iloc[0]) else 0.0
    b_dot_pct = float(b_stats_df["dot_ball_pct"].iloc[0]) if not b_stats_df.empty and pd.notnull(b_stats_df["dot_ball_pct"].iloc[0]) else 0.0
    b_dots = int(b_stats_df["dot_balls"].iloc[0]) if not b_stats_df.empty and pd.notnull(b_stats_df["dot_balls"].iloc[0]) else 0
    b_overs = round(b_balls / 6.0, 1)

    with bmc1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-header">WICKETS</div>
                <div class="metric-num">{b_wkts:,}</div>
                <div class="metric-desc">({b_balls:,} balls)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with bmc2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-header">ECONOMY</div>
                <div class="metric-num">{b_econ:.2f}</div>
                <div class="metric-desc">({b_overs:.1f} overs)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with bmc3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-header">DOT-BALL SHARE</div>
                <div class="metric-num">{b_dot_pct:.0f}%</div>
                <div class="metric-desc">(n = {b_dots:,})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # --------------------------------------------------------------------------
    # Visual 1 (The Hero): Economy by Season
    # --------------------------------------------------------------------------
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chart-card-title">Economy by Season</div>',
        unsafe_allow_html=True,
    )

    bowler_season_df = q(
        """
        SELECT
            CAST(b.season_id AS INTEGER) AS season,
            ROUND(6.0 * SUM(b.bowler_runs) / NULLIF(SUM(b.is_legal), 0), 2) AS bowler_economy,
            l.league_economy
        FROM v_ball b
        JOIN (
            SELECT
                CAST(season_id AS INTEGER) AS season_id,
                ROUND(6.0 * SUM(bowler_runs) / NULLIF(SUM(is_legal), 0), 2) AS league_economy
            FROM v_ball
            WHERE CAST(season_id AS INTEGER) BETWEEN 2008 AND 2026
            GROUP BY CAST(season_id AS INTEGER)
        ) l ON CAST(b.season_id AS INTEGER) = l.season_id
        WHERE b.bowler = ?
          AND CAST(b.season_id AS INTEGER) BETWEEN 2008 AND 2026
        GROUP BY CAST(b.season_id AS INTEGER)
        ORDER BY CAST(b.season_id AS INTEGER) ASC;
        """,
        (selected_bowler,),
    )

    fig_b_season = go.Figure()
    if not bowler_season_df.empty:
        fig_b_season.add_trace(
            go.Scatter(
                x=bowler_season_df["season"],
                y=bowler_season_df["bowler_economy"],
                mode="lines+markers",
                name="Bowler",
                line=dict(color=DARK_GREEN, width=2.5),
                marker=dict(size=7, color=DARK_GREEN),
                hovertemplate="Season %{x}: %{y:.2f} RPO<extra></extra>",
            )
        )
        fig_b_season.add_trace(
            go.Scatter(
                x=bowler_season_df["season"],
                y=bowler_season_df["league_economy"],
                mode="lines",
                name="--- League Average",
                line=dict(color=LEAGUE_LINE, width=1.5, dash="dash"),
                hovertemplate="League (%{x}): %{y:.2f} RPO<extra></extra>",
            )
        )
        if selected_years_s2:
            sel_b_pt = bowler_season_df[bowler_season_df["season"].isin(selected_years_s2)]
            if not sel_b_pt.empty:
                fig_b_season.add_trace(
                    go.Scatter(
                        x=sel_b_pt["season"],
                        y=sel_b_pt["bowler_economy"],
                        mode="markers",
                        name="Selected Seasons",
                        marker=dict(size=10, color="#F59E0B", symbol="diamond"),
                        hovertemplate="%{x}: %{y:.2f} RPO<extra></extra>",
                    )
                )

    fig_b_season.update_layout(
        template="plotly_dark",
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
            font=dict(color="#E5E7EB"),
        height=300,
        margin=dict(l=30, r=30, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(range=[4, 12], dtick=2, title="Economy Rate (Runs per 6 Legal Balls)", gridcolor="#243047"),
        xaxis=dict(title="IPL Season (2008–2026)", type="linear", range=[2008, 2026], autorange=False, tickmode="array", tickvals=list(range(2008, 2027, 2)), ticktext=[str(y) for y in range(2008, 2027, 2)], gridcolor="#243047"),
    )
    st.plotly_chart(fig_b_season, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # Middle Row: Visual 2 (Wickets & Economy by Phase) & Visual 3 (Economy vs Opponent)
    # --------------------------------------------------------------------------
    b_mid_col1, b_mid_col2 = st.columns(2)

    with b_mid_col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-card-title">Wickets & Economy by Phase</div>',
            unsafe_allow_html=True,
        )
        b_phase_stats = q(
            """
            SELECT
                CASE phase
                    WHEN 'Powerplay' THEN 'Powerplay (1–6)'
                    WHEN 'Middle' THEN 'Middle Overs (7–15)'
                    ELSE 'Death Overs (16–20)'
                END AS phase_label,
                SUM(bowler_wicket) AS wickets,
                ROUND(6.0 * SUM(bowler_runs) / NULLIF(SUM(is_legal), 0), 2) AS economy,
                SUM(is_legal) AS balls
            FROM v_ball
            WHERE bowler = ?
              AND (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
            GROUP BY phase_label
            ORDER BY CASE phase_label
                WHEN 'Powerplay (1–6)' THEN 1
                WHEN 'Middle Overs (7–15)' THEN 2
                ELSE 3 END;
            """,
            (selected_bowler, param_season_s2, param_season_s2),
        )

        fig_b_phase = go.Figure()
        if not b_phase_stats.empty:
            fig_b_phase.add_trace(
                go.Bar(
                    x=b_phase_stats["phase_label"],
                    y=b_phase_stats["wickets"],
                    name="Wickets",
                    marker_color=LIGHT_GREEN,
                    yaxis="y",
                    width=0.4,
                )
            )
            fig_b_phase.add_trace(
                go.Scatter(
                    x=b_phase_stats["phase_label"],
                    y=b_phase_stats["economy"],
                    name="Economy",
                    mode="lines+markers",
                    line=dict(color=DARK_GREEN, width=2.5),
                    marker=dict(size=8, color=DARK_GREEN),
                    yaxis="y2",
                )
            )

        fig_b_phase.update_layout(
            template="plotly_dark",
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font=dict(color="#E5E7EB"),
            height=260,
            margin=dict(l=20, r=20, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(title="Wickets", side="left", gridcolor="#243047"),
            yaxis2=dict(title="Economy Rate (Runs per 6 Legal Balls)", side="right", overlaying="y", range=[0, 14], dtick=2),
            xaxis=dict(title="Innings Phase", gridcolor="#243047"),
        )
        st.plotly_chart(fig_b_phase, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with b_mid_col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-card-title">Economy vs Opponent</div>',
            unsafe_allow_html=True,
        )
        b_opp_df = q(
            """
            SELECT
                batting_team AS opponent,
                ROUND(6.0 * SUM(bowler_runs) / NULLIF(SUM(is_legal), 0), 2) AS economy,
                SUM(is_legal) AS balls
            FROM v_ball
            WHERE bowler = ?
              AND (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
            GROUP BY batting_team
            HAVING SUM(is_legal) >= 12
            ORDER BY economy ASC
            LIMIT 8;
            """,
            (selected_bowler, param_season_s2, param_season_s2),
        )

        fig_b_opp = px.bar(
            b_opp_df,
            x="economy",
            y="opponent",
            orientation="h",
            text="economy",
            labels={"economy": "", "opponent": ""},
        )
        fig_b_opp.update_traces(
            marker_color=MID_GREEN,
            texttemplate="%{text:.2f}",
            textposition="inside",
        )
        fig_b_opp.update_layout(
            template="plotly_dark",
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font=dict(color="#E5E7EB"),
            height=260,
            margin=dict(l=10, r=20, t=10, b=10),
            yaxis=dict(autorange="reversed", title="Opposition Team"),
            xaxis=dict(title="Economy Rate (Runs per 6 Legal Balls)", range=[0, 15], dtick=5, gridcolor="#243047"),
        )
        st.plotly_chart(fig_b_opp, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # Bottom Row: Visual 4 (Economy by Ground, venue_clean) & Visual 5 (Dismissal Types)
    # --------------------------------------------------------------------------
    b_bot_col1, b_bot_col2 = st.columns(2)

    with b_bot_col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-card-title">Economy by Ground</div>',
            unsafe_allow_html=True,
        )
        # Requirement: Ground names come from venue_clean, never from venue!
        b_ground_df = q(
            """
            SELECT
                m.venue_clean AS ground,
                ROUND(6.0 * SUM(b.bowler_runs) / NULLIF(SUM(b.is_legal), 0), 2) AS economy,
                SUM(b.is_legal) AS balls
            FROM v_ball b
            JOIN matches_clean m ON b.match_id = m.match_id
            WHERE b.bowler = ?
              AND (? IS NULL OR instr(',' || ? || ',', ',' || CAST(b.season_id AS INTEGER) || ',') > 0)
            GROUP BY m.venue_clean
            HAVING SUM(b.is_legal) >= 24
            ORDER BY economy ASC
            LIMIT 5;
            """,
            (selected_bowler, param_season_s2, param_season_s2),
        )

        fig_b_ground = px.bar(
            b_ground_df,
            x="economy",
            y="ground",
            orientation="h",
            text="economy",
            labels={"economy": "", "ground": ""},
        )
        fig_b_ground.update_traces(
            marker_color=MID_GREEN,
            texttemplate="%{text:.2f}",
            textposition="inside",
        )
        fig_b_ground.update_layout(
            template="plotly_dark",
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font=dict(color="#E5E7EB"),
            height=250,
            margin=dict(l=10, r=20, t=10, b=10),
            yaxis=dict(autorange="reversed", title="Ground / Venue"),
            xaxis=dict(title="Economy Rate (Runs per 6 Legal Balls)", range=[0, 15], dtick=5, gridcolor="#243047"),
        )
        st.plotly_chart(fig_b_ground, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with b_bot_col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown(
            '<div class="chart-card-title">Dismissal Types</div>',
            unsafe_allow_html=True,
        )
        b_dism_types = q(
            """
            SELECT
                CASE wicket_kind
                    WHEN 'bowled' THEN 'Bowled'
                    WHEN 'caught' THEN 'Caught'
                    WHEN 'lbw' THEN 'LBW'
                    WHEN 'caught and bowled' THEN 'Caught & Bowled'
                    WHEN 'stumped' THEN 'Stumped'
                    WHEN 'hit wicket' THEN 'Hit Wicket'
                    ELSE 'Others'
                END AS dismissal_label,
                COUNT(*) AS count
            FROM v_ball
            WHERE bowler = ?
              AND (? IS NULL OR instr(',' || ? || ',', ',' || CAST(season_id AS INTEGER) || ',') > 0)
              AND bowler_wicket = 1
            GROUP BY dismissal_label
            ORDER BY count DESC;
            """,
            (selected_bowler, param_season_s2, param_season_s2),
        )

        fig_b_dism = px.bar(
            b_dism_types,
            x="count",
            y="dismissal_label",
            orientation="h",
            text="count",
            labels={"count": "", "dismissal_label": ""},
        )
        fig_b_dism.update_traces(
            marker_color=DARK_GREEN,
            texttemplate="%{text}",
            textposition="inside",
        )
        fig_b_dism.update_layout(
            template="plotly_dark",
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font=dict(color="#E5E7EB"),
            height=250,
            margin=dict(l=10, r=20, t=10, b=10),
            yaxis=dict(autorange="reversed", title="Dismissal Type"),
            xaxis=dict(title="Wickets", gridcolor="#243047"),
        )
        st.plotly_chart(fig_b_dism, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)