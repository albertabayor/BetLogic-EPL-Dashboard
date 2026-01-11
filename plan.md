# Project Plan: EPL 2024/2025 Analytics Dashboard (Revised)

## 1. Objectives
Membangun dashboard interaktif untuk memvisualisasikan performa tim, statistik pertandingan, dan analisis peluang (odds) menggunakan dataset musim 2024/2025 dengan fokus pada **data quality**, **user experience**, dan **actionable insights**.

---

## 2. Tech Stack
- **Language:** Python 3.10+
- **Framework:** Streamlit 1.28+
- **Data Manipulation:** Pandas, NumPy
- **Visualization:** Plotly (Interaktif), Matplotlib/Seaborn (Statik)
- **Testing:** Pytest (untuk validasi logika)
- **Deployment:** Streamlit Cloud / Hugging Face Spaces
- **Version Control:** Git + GitHub

---

## 3. Data Processing Pipeline

### 3.1 Data Validation
```python
# CRITICAL: Handle BOM character in first column name
- Remove BOM from column names (Div appears as ﻿Div in raw CSV)
- Cek duplikasi pertandingan (Date + HomeTeam + AwayTeam)
- Validasi konsistensi: Total Shots ≥ Shots on Target
- Handling outlier odds (nilai < 1.01 atau > 100)
- Normalisasi nama tim (dataset uses consistent names like "Man United", "Man City", "Nott'm Forest")
```

### 3.2 Data Cleaning
- **BOM Handling:** Use `encoding='utf-8-sig'` when reading CSV to handle BOM character
- **Date Parsing:** Convert DD/MM/YYYY format to datetime with `dayfirst=True`
- Penanganan missing values:
  - Odds: Gunakan median dari bookmaker lain
  - Empty odds (some Betfair Exchange columns are empty): Skip or use Avg odds
  - Referee: Tandai sebagai "Unknown"
  - Shots/Fouls: Tandai sebagai NaN (jangan impute)

### 3.3 Feature Engineering
- **Poin Calculation:** Win: 3, Draw: 1, Loss: 0
- **Goal Difference (GD):** FTHG - FTAG
- **Form String:** "WWDLW" dari 5 pertandingan terakhir
- **Home/Away Splits:** Pisahkan statistik kandang dan tandang
- **Implied Probability:** Konversi odds ke probabilitas (1/odds) dengan normalisasi
  - Gunakan AvgH/AvgD/AvgA columns (already calculated across bookmakers)
- **Momentum Score:** Weighted points dari 5 pertandingan terakhir (match terakhir weight lebih tinggi)
- **Odds Categories:** Classify matches as Favorite/Underdog/Neutral based on odds

---

## 4. Core Features & Pages (Sitemap)

### 📊 Page 1: League Overview
**Components:**
- **Live Standing Table:** 
  - Kolom: Position, Team, Played, Won, Draw, Lost, GF, GA, GD, Points, Form (last 5)
  - Sortable & searchable
- **Top Performers Cards:**
  - Top Scorers (Team): Total goals home + away
  - Best Defense: Least goals conceded
  - Momentum Leaders: Top 3 teams dengan form terbaik
- **Season Progress Chart:**
  - Line chart akumulasi poin 6 tim besar sepanjang musim
  - Toggle untuk melihat semua tim

### ⚽ Page 2: Team Analysis
**Sidebar Filters:**
- Dropdown: Pilih Tim
- Toggle: Home Only / Away Only / All Matches

**Visualizations:**
- **Metric Cards:** Peringkat, W-D-L, Goals For/Against, Points
- **Performance Radar Chart:** 
  - Axes: Goals, Shots Accuracy, Discipline (fewer cards = better), Clean Sheets, Win Rate
- **Shot Efficiency:**
  - Scatter plot: Shots vs Shots on Target (bubble size = goals scored)
- **Home vs Away Comparison:**
  - Bar chart: Win%, Goals/Match, Points/Match
- **Recent Form Timeline:**
  - Visual timeline 5 pertandingan terakhir dengan score dan opponent

### ⚔️ Page 3: Head-to-Head (H2H)
**Input:**
- Two dropdowns untuk memilih Team A vs Team B

**Analysis:**
- **Historical Matchups Table:** Semua pertemuan musim ini (Date, Score, Venue)
- **Direct Comparison Cards:**
  - Overall record (wins, draws)
  - Goals scored/conceded dalam H2H
  - Average odds dari bookmakers
- **Win Probability Calculation:**
  ```
  Weighted formula:
  - Recent form (40%)
  - H2H history (30%)
  - Home advantage factor (15%)
  - Bookmaker odds (15%)
  ```
- **Prediction Confidence Indicator:** Low/Medium/High berdasarkan data availability

### 🟨 Page 4: Referee & Discipline
**Features:**
- **Referee Leaderboard:**
  - Table: Referee, Matches, Yellow Cards, Red Cards, Cards/Match ratio
  - Filter by referee name
- **Card Distribution Heatmap:**
  - X-axis: Teams, Y-axis: Match week
  - Color intensity: Total cards received
- **Fouls vs Results Correlation:**
  - Scatter plot: Total fouls vs Points earned
  - Insight text: "Teams dengan foul <X per match win Y% more"

### 💰 Page 5: Betting Insights
**Available Data (from actual dataset):**
- Bookmakers: Bet365 (B365), Bet&Win (BW), Betfair (BF/BFE), Pinnacle (PS), William Hill (WH), 1XB
- Odds Types: Home/Draw/Away, Over/Under 2.5, Asian Handicap, Asian Handicap (Closing)

**Analysis Tools:**
- **Odds Movement Tracker:**
  - Line chart: Average odds (AvgH/AvgD/AvgA) per matchweek
  - Highlight pertandingan dengan odds swing terbesar (Max vs Min odds)
- **Over/Under 2.5 Goals:**
  - Pie chart: Actual vs Predicted (berdasarkan Avg>2.5 / Avg<2.5 odds)
  - ROI simulation: "If bet £100 on Over 2.5 in all matches → Profit/Loss"
  - Use B365>2.5/B365<2.5 columns as primary odds source
- **Value Bet Detector:**
  - Table: Matches di mana actual probability berbeda >15% dari implied odds
  - Compare Max odds vs Avg odds untuk find value opportunities
  - Flag: "Potential Value Bet" dengan confidence level
- **Bookmaker Comparison:**
  - Box plot: Distribusi odds dari Bet365, PSH, WH untuk outcome yang sama
  - Highlight when Max odds differs significantly from Avg odds (>10%)

### 📈 Page 6: Advanced Metrics (Optional MVP)
- **Expected vs Actual Points:** Jika tersedia xG data
- **Fixture Difficulty:** Upcoming matches color-coded by opponent strength
- **Player Stats:** Top scorers, assists (jika data tersedia)

---

## 5. Implementation Roadmap

### ✅ Phase 1: Foundation (Day 1-2)
- [ ] Setup environment (venv, requirements.txt dengan pinned versions)
- [ ] Initialize Git repo dengan .gitignore (cache, __pycache__, .env)
- [ ] Create `constants.py` dengan:
  - Team name mappings (jika diperlukan)
  - Column name constants untuk odds (B365H, B365D, B365A, dll)
  - Data validation thresholds (ODDS_THRESHOLD_MIN=1.01, ODDS_THRESHOLD_MAX=100.0)
  - MIN_MATCHES_FOR_FORM = 5
- [ ] Basic Streamlit app structure:
  - Multi-page layout dengan st.sidebar
  - App title, favicon, custom theme (theme.toml)
- [ ] Create README.md dengan screenshot placeholders

### ✅ Phase 2: Data Pipeline (Day 2-3)
- [ ] Data loading function dengan `@st.cache_data(ttl=3600)`
  - **CRITICAL:** Use `pd.read_csv(path, encoding='utf-8-sig')` untuk handle BOM
  - Parse dates dengan `dayfirst=True` untuk DD/MM/YYYY format
- [ ] Implement validation function (validate_data):
  - Check required columns exist (handle BOM in first column)
  - Validate data types
  - Check for impossible values (negative shots, etc.)
  - Verify odds columns numeric (some may have empty strings)
- [ ] Data cleaning pipeline
  - Clean column names (strip whitespace, remove BOM)
  - Handle empty Betfair Exchange odds (fill NaN or drop columns)
- [ ] Feature engineering functions:
  - calculate_standings()
  - calculate_form()
  - calculate_momentum_score()
  - calculate_implied_probability() - gunakan AvgH/AvgD/AvgA

### ✅ Phase 2.5: Testing (Day 3)
- [ ] Write unit tests untuk:
  - Standing calculation (test dengan dummy data)
  - Form string generation
  - Edge cases (team dengan 0 matches played)
- [ ] Create sample_data.csv (5-10 rows) untuk demo

### ✅ Phase 3: Core Pages (Day 4-6)
- [ ] **Page 1:** League Overview
  - Standing table dengan st.dataframe styling
  - Top performers metric cards
  - Season progress chart (Plotly line)
- [ ] **Page 2:** Team Analysis
  - Sidebar filters
  - Metric cards dengan st.metric delta
  - Radar chart dan shot efficiency scatter

### ✅ Phase 4: Interactive Features (Day 7-8)
- [ ] **Page 3:** H2H Analysis
  - Team selection widgets
  - Win probability calculation
  - Confidence indicator logic
- [ ] **Page 4:** Referee Analytics
  - Leaderboard table
  - Heatmap visualization

### ✅ Phase 5: Betting Module (Day 9-10)
- [ ] **Page 5:** Betting Insights
  - Odds movement chart
  - Over/Under analysis
  - Value bet detector algorithm
  - ROI simulation calculator

### ✅ Phase 5.5: Performance Optimization (Day 10)
- [ ] Implement lazy loading untuk grafik berat
- [ ] Add st.spinner untuk operasi lambat
- [ ] Optimize DataFrame operations (vectorization)

### ✅ Phase 6: UI/UX Polish (Day 11-12)
- [ ] Custom CSS untuk:
  - Team colors pada standing table
  - Card styling (shadows, borders)
  - Responsive layout
- [ ] Add team logos (dari API gratis atau local assets)
- [ ] Error handling:
  - Empty state messages ("No data available")
  - Invalid input warnings
  - Fallback values untuk missing data
- [ ] Loading indicators (st.progress, st.spinner)

### ✅ Phase 6.5: Documentation & Deploy (Day 13)
- [ ] Finalize README.md:
  - Installation instructions
  - Screenshots of each page
  - Data source attribution
- [ ] Create CHANGELOG.md
- [ ] Deploy to Streamlit Cloud:
  - Setup secrets for API keys (jika ada)
  - Test on mobile viewport
- [ ] Share link for feedback

---

## 6. Error Handling & Edge Cases

### Critical Checks
```python
# Di setiap page:
try:
    if df.empty:
        st.warning("⚠️ No data available. Please check data source.")
        st.stop()
except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("Please refresh the page or contact support.")
```

### Edge Cases to Handle
- **BOM Character Issue:** First column may contain BOM character, use encoding='utf-8-sig'
- **Empty Odds Columns:** Some Betfair Exchange (BFE*) columns may be empty strings instead of NaN
- **Team dengan < 5 pertandingan** (form string tidak lengkap) → Show partial form dengan warning
- **Missing odds dari semua bookmakers** → Skip bet insights, show "No odds data available"
- **Referee tanpa nama** → Tampilkan "Unknown Referee"
- **User memilih team yang sama di H2H** → Show warning
- **Date parsing issues** → DD/MM/YYYY format requires dayfirst=True parameter

---

## 7. Future Enhancements (Post-MVP)

### Short-term (1-2 weeks post-launch)
- [ ] **Player Statistics Page:**
  - Top scorers, assists, cards
  - Player comparison tool
- [ ] **Export Functionality:**
  - Download standing table as CSV
  - Export match report to PDF (ReportLab)
- [ ] **Fixture Difficulty Tracker:**
  - Visual calendar dengan color-coded opponents
  - Strength of Schedule (SOS) calculation

### Medium-term (1-2 months)
- [ ] **Machine Learning Predictions:**
  - Start dengan Logistic Regression (Win/Draw/Loss)
  - Feature importance visualization
  - Model performance metrics (accuracy, precision)
- [ ] **Historical Data Integration:**
  - Load previous seasons (2023/24, 2022/23)
  - Multi-season comparison charts
- [ ] **Real-time Updates:**
  - Integrate free API (football-data.org, 500 req/day)
  - Auto-refresh dashboard setiap 10 menit saat matchday

### Long-term (3+ months)
- [ ] **Advanced ML Models:**
  - XGBoost untuk accuracy improvement
  - Neural Network untuk goal prediction
- [ ] **User Accounts:**
  - Save favorite teams
  - Custom alerts (WhatsApp/Email) untuk hasil pertandingan
- [ ] **Mobile App:**
  - Convert to PWA (Progressive Web App)
  - Push notifications

---

## 8. Pre-Deployment Checklist

### Code Quality
- [ ] All functions have docstrings
- [ ] No hardcoded values (use constants.py)
- [ ] Type hints untuk main functions
- [ ] Code formatted dengan Black/Autopep8

### Documentation
- [ ] README.md complete dengan:
  - Project overview
  - Installation steps (pip install -r requirements.txt)
  - Usage instructions
  - Screenshots (at least 3 pages)
  - License (MIT)
- [ ] requirements.txt dengan versions:
  ```
  streamlit==1.28.0
  pandas==2.1.0
  plotly==5.17.0
  numpy==1.25.0
  pytest==7.4.0
  ```
- [ ] Sample data included (epl_sample.csv)

### Testing
- [ ] Manual testing pada:
  - Chrome, Firefox, Safari
  - Desktop & mobile viewport
- [ ] All pages load without errors
- [ ] All filters/dropdowns work correctly
- [ ] pytest suite passes (min 80% coverage)

### Deployment
- [ ] Streamlit Cloud configured:
  - Python version: 3.10
  - Requirements.txt uploaded
  - Secrets configured (jika ada API keys)
- [ ] Custom domain (optional): epl-analytics.streamlit.app
- [ ] Analytics tracking (Streamlit built-in atau Google Analytics)

---

## 9. Success Metrics (Post-Launch)

### Technical
- Dashboard loads in < 3 seconds
- No crashes in first week (99.9% uptime)
- All unit tests pass

### User Engagement
- Target: 100 unique visitors in first month
- Avg session duration: > 5 minutes
- Most popular page: League Overview (expected)

### Feedback Goals
- Collect 10+ user feedbacks via GitHub issues
- Implement top 3 requested features in v1.1

---

## 10. Risk Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **BOM character in CSV** | High | **Confirmed** | Use encoding='utf-8-sig' when reading CSV |
| Data source changes format | High | Medium | Validate schema on load, alert on failure |
| Streamlit Cloud downtime | High | Low | Have backup deploy on Hugging Face |
| Empty Betfair odds columns | Medium | **Confirmed** | Check for empty strings, fill with NaN or drop |
| Missing odds data | Medium | Medium | Fallback to average, disable bet insights |
| Date format confusion | Medium | Medium | Use dayfirst=True for DD/MM/YYYY format |
| Performance issues with large data | Medium | High | Implement pagination, lazy loading |
| User finds bugs | Low | High | Add feedback button, monitor errors |

---

## 11. Team & Timeline

**Solo Developer:** 13 days for MVP (Phase 1-6.5)

**Working Hours:** 4-6 hours/day

**Target Launch:** 2 weeks from start date

**Post-Launch Support:** 2-3 hours/week for bug fixes & feature requests

---

## 12. Constants File Template

Create `src/constants.py` dengan struktur berikut:

```python
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
```

---

## 13. Resources & References

### Data Sources
- EPL 2024/25 Dataset: [Football-Data.co.uk](http://www.football-data.co.uk/)
- Team Logos: [API-Football](https://www.api-football.com/) (Free tier)

### Learning Resources
- Streamlit Docs: https://docs.streamlit.io
- Plotly Python: https://plotly.com/python/
- Football Analytics: [StatsBomb](https://statsbomb.com/articles/)

### Inspiration
- [FiveThirtyEight Soccer Predictions](https://projects.fivethirtyeight.com/soccer-predictions/)
- [Understat](https://understat.com/)

---

## Notes
- **Prioritas:** Focus on MVP (Page 1-5) before advanced features
- **Fail Fast:** Deploy early, gather feedback, iterate
- **Data Quality > Quantity:** Better to have 5 accurate metrics than 20 unreliable ones
- **User First:** Design for non-technical football fans, not data scientists

---

**Version:** 1.1 (Data-Verified)
**Last Updated:** January 2026 (verified against actual dataset)
**Status:** Ready for Implementation 🚀

**Change Log:**
- v1.1: Added BOM character handling, updated odds columns based on actual data
- v1.0: Initial plan release