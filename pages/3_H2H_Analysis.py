"""
Page 3: Head-to-Head Analysis

Compare two teams with historical matchup data and win probability prediction.
"""

import streamlit as st
import pandas as pd
from src.features import get_head_to_head_stats, calculate_win_probability, calculate_momentum_score
from src.data_loader import get_all_teams
from src.constants import TEAM_COLORS
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import load_data, page_header, page_footer, inject_custom_css, h2h_score_card

st.set_page_config(
    page_title="Head-to-Head | EPL Analytics",
    page_icon="⚔️",
    layout="wide"
)

df = load_data()
all_teams = get_all_teams(df)

# Initialize theme
inject_custom_css()

page_header("Head-to-Head Analysis", "Historical matchups and predictions")

# Team selection
col1, col2, col3 = st.columns([3, 1, 3])

with col1:
    team_a = st.selectbox("Team A", options=all_teams, index=0, key="h2h_team_a")

with col2:
    st.markdown("<div style='text-align: center; font-size: 2rem; padding-top: 1rem;'>VS</div>", unsafe_allow_html=True)

with col3:
    available_teams_b = [t for t in all_teams if t != team_a]
    team_b = st.selectbox("Team B", options=available_teams_b, index=0, key="h2h_team_b")

st.markdown("---")

col_home1, col_home2 = st.columns(2)
with col_home1:
    home_team = st.radio("Which team is playing at home?", options=[team_a, team_b], horizontal=True, key="h2h_home_team")

if team_a == team_b:
    st.error("Please select two different teams.")
    st.stop()

st.markdown("---")

# Calculate H2H stats
h2h_stats = get_head_to_head_stats(df, team_a, team_b)

# Display H2H Summary
col_a, col_vs, col_b = st.columns(3)

with col_a:
    h2h_score_card(team_a, h2h_stats['team_a_wins'], "wins", TEAM_COLORS.get(team_a, '#003399'))

with col_vs:
    h2h_score_card("Draw", h2h_stats['draws'], "draws")

with col_b:
    h2h_score_card(team_b, h2h_stats['team_b_wins'], "wins", TEAM_COLORS.get(team_b, '#003399'))

st.markdown("---")

# Historical matchups table
if h2h_stats['total_matches'] > 0:
    st.subheader(f"Historical Matchups ({h2h_stats['total_matches']} matches)")
    matches_df = h2h_stats['matches'].copy()

    matches_df['Result'] = matches_df.apply(
        lambda row: f"{team_a} Won" if ((row['HomeTeam'] == team_a) & (row['FTR'] == 'H')) or ((row['AwayTeam'] == team_a) & (row['FTR'] == 'A'))
        else (f"{team_b} Won" if ((row['HomeTeam'] == team_b) & (row['FTR'] == 'H')) or ((row['AwayTeam'] == team_b) & (row['FTR'] == 'A'))
        else "Draw"), axis=1
    )
    matches_df['Score'] = matches_df['FTHG'].astype(str) + '-' + matches_df['FTAG'].astype(str)

    display_cols = ['Date', 'HomeTeam', 'AwayTeam', 'Score', 'FTR', 'Referee']
    st.dataframe(matches_df[display_cols], hide_index=True, width="stretch")
else:
    st.info("No historical matchups found between these teams.")

st.markdown("---")

# Win Probability Prediction
st.subheader("Win Probability Prediction")
probability = calculate_win_probability(df, team_a, team_b, home_team)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(f"{home_team} Win", f"{probability['home_win']}%", delta=f"Confidence: {probability['confidence']}")
with col2:
    st.metric("Draw", f"{probability['draw']}%")
with col3:
    away_team = team_b if home_team == team_a else team_a
    st.metric(f"{away_team} Win", f"{probability['away_win']}%")

# Probability bar chart
import plotly.graph_objects as go
fig_probs = go.Figure(go.Bar(
    x=[probability['home_win'], probability['draw'], probability['away_win']],
    y=[f"{home_team} Win", "Draw", f"{away_team} Win"],
    orientation='h',
    marker_color=['#00CC96', '#F5F5F5', '#EF553B'],
    text=[f"{probability['home_win']}%", f"{probability['draw']}%", f"{probability['away_win']}%"],
    textposition='auto'
))
fig_probs.update_layout(title="Predicted Match Outcome Probabilities", xaxis_title="Probability (%)", height=300)
st.plotly_chart(fig_probs, width="stretch")

page_footer()
