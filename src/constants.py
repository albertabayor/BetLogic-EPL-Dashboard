"""
Constants untuk EPL Analytics Dashboard
Menghindari hardcoded values dan menyediakan central configuration
"""

# ============================================
# DATA VALIDATION THRESHOLDS
# ============================================
ODDS_THRESHOLD_MIN = 1.01
ODDS_THRESHOLD_MAX = 100.0
MIN_MATCHES_FOR_FORM = 5
MIN_MATCHES_FOR_STANDINGS = 1

# ============================================
# COLUMN NAME CONSTANTS
# ============================================
# Basic match info
COL_DIV = "Div"
COL_DATE = "Date"
COL_TIME = "Time"
COL_HOME_TEAM = "HomeTeam"
COL_AWAY_TEAM = "AwayTeam"

# Full-time results
COL_FTHG = "FTHG"  # Full Time Home Goals
COL_FTAG = "FTAG"  # Full Time Away Goals
COL_FTR = "FTR"    # Full Time Result (H/D/A)

# Half-time results
COL_HTHG = "HTHG"  # Half Time Home Goals
COL_HTAG = "HTAG"  # Half Time Away Goals
COL_HTR = "HTR"    # Half Time Result

# Shots
COL_HS = "HS"      # Home Shots
COL_AS = "AS"      # Away Shots
COL_HST = "HST"    # Home Shots on Target
COL_AST = "AST"    # Away Shots on Target

# Fouls & Cards
COL_HF = "HF"      # Home Fouls
COL_AF = "AF"      # Away Fouls
COL_HC = "HC"      # Home Corners
COL_AC = "AC"      # Away Corners
COL_HY = "HY"      # Home Yellow Cards
COL_AY = "AY"      # Away Yellow Cards
COL_HR = "HR"      # Home Red Cards
COL_AR = "AR"      # Away Red Cards

# Referee
COL_REF = "Referee"

# ============================================
# BETTING ODDS COLUMNS
# ============================================
# Primary odds source (Bet365 - most complete)
ODDS_B365H = "B365H"  # Bet365 Home Win Odds
ODDS_B365D = "B365D"  # Bet365 Draw Odds
ODDS_B365A = "B365A"  # Bet365 Away Win Odds

# Average odds (recommended for analysis)
ODDS_AVGH = "AvgH"
ODDS_AVGD = "AvgD"
ODDS_AVGA = "AvgA"

# Over/Under 2.5 Goals
ODDS_B365_OVER25 = "B365>2.5"
ODDS_B365_UNDER25 = "B365<2.5"
ODDS_AVG_OVER25 = "Avg>2.5"
ODDS_AVG_UNDER25 = "Avg<2.5"

# Asian Handicap
ODDS_B365_AHH = "B365AHH"  # Asian Handicap Home
ODDS_B365_AHA = "B365AHA"  # Asian Handicap Away

# Other bookmakers (optional, untuk comparison)
BOOKMAKERS = ["B365", "BW", "PS", "WH", "1XB", "BF"]

# ============================================
# RESULT VALUES
# ============================================
RESULT_HOME_WIN = "H"
RESULT_DRAW = "D"
RESULT_AWAY_WIN = "A"

# ============================================
# POINTS SYSTEM
# ============================================
POINTS_WIN = 3
POINTS_DRAW = 1
POINTS_LOSS = 0

# ============================================
# CACHE SETTINGS
# ============================================
CACHE_TTL_SECONDS = 3600  # 1 hour

# ============================================
# TEAM COLORS (untuk visualizations)
# ============================================
TEAM_COLORS = {
    "Arsenal": "#EF0107",
    "Aston Villa": "#95BFE5",
    "Bournemouth": "#DA291C",
    "Brentford": "#E30613",
    "Brighton": "#0057B8",
    "Chelsea": "#034694",
    "Crystal Palace": "#1B458F",
    "Everton": "#003399",
    "Fulham": "#000000",
    "Ipswich": "#003399",
    "Leicester": "#003090",
    "Liverpool": "#C8102E",
    "Man City": "#6CABDD",
    "Man United": "#DA291C",
    "Newcastle": "#241F20",
    "Nott'm Forest": "#000000",
    "Southampton": "#D71920",
    "Tottenham": "#132257",
    "West Ham": "#7A263A",
    "Wolves": "#FDB913",
}

# ============================================
# CSV READING SETTINGS
# ============================================
# CRITICAL: Use utf-8-sig to handle BOM character in first column
CSV_ENCODING = "utf-8-sig"
# Date format in CSV is DD/MM/YYYY
CSV_DAYFIRST = True
