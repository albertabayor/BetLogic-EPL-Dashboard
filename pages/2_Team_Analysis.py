"""
Page 2: Team Analysis

Detailed statistics and visualizations for a specific team.
"""

import streamlit as st
import pandas as pd
from src.features import get_team_stats, calculate_standings
from src.visualizations import (
    plot_team_performance_radar,
    plot_shot_efficiency,
    plot_home_away_comparison,
    plot_form_timeline
)
from src.data_loader import get_all_teams
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import load_data, page_header, page_footer, inject_custom_css

st.set_page_config(
    page_title="Team Analysis | EPL Analytics",
    page_icon="⚽",
    layout="wide"
)

# Load data
df = load_data()

# Get all teams
all_teams = get_all_teams(df)

# Page header
page_header("Team Analysis", "Detailed performance metrics by team")

# Initialize theme
inject_custom_css()

# Sidebar filters
with st.sidebar:
    st.subheader("Filters")
    selected_team = st.selectbox("Select Team", options=all_teams, index=0)
    venue_filter = st.radio("Venue Filter", options=["All Matches", "Home Only", "Away Only"], horizontal=True)

    venue_map = {
        "All Matches": None,
        "Home Only": "home",
        "Away Only": "away"
    }
    venue = venue_map[venue_filter]

# Get team statistics
team_stats = get_team_stats(df, selected_team, venue)

if team_stats['matches_played'] == 0:
    st.warning(f"No matches found for {selected_team} in the selected venue.")
    st.stop()

# Main content
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    standings = calculate_standings(df)
    team_row = standings[standings['Team'] == selected_team]
    pos = int(team_row.iloc[0]['Pos']) if len(team_row) > 0 else "-"
    st.metric("Position", pos)

with col2:
    st.metric("Matches", team_stats['matches_played'])

with col3:
    st.metric("Points", team_stats['points'])

with col4:
    st.metric("Win Rate", f"{team_stats['win_rate']}%")

with col5:
    st.metric("Goal Diff", team_stats['goal_difference'])

st.markdown("---")

# Two-column layout
left_col, right_col = st.columns([3, 2])

with left_col:
    st.subheader("Performance Radar")
    radar_stats = get_team_stats(df, selected_team, None)
    fig_radar = plot_team_performance_radar(radar_stats, selected_team)
    st.plotly_chart(fig_radar, width="stretch")

    st.subheader("Shot Efficiency")
    fig_shots = plot_shot_efficiency(df)
    st.plotly_chart(fig_shots, width="stretch")

with right_col:
    st.subheader(f"{selected_team} Statistics")

    col_w, col_d, col_l = st.columns(3)
    with col_w:
        st.metric("Wins", team_stats['wins'])
    with col_d:
        st.metric("Draws", team_stats['draws'])
    with col_l:
        st.metric("Losses", team_stats['losses'])

    st.write("---")
    st.write("**Goals**")
    col_gf, col_ga, col_gd = st.columns(3)
    with col_gf:
        st.metric("For", team_stats['goals_for'])
    with col_ga:
        st.metric("Against", team_stats['goals_against'])
    with col_gd:
        st.metric("Difference", team_stats['goal_difference'])

    st.write("---")
    st.write("**Additional Stats**")
    st.write(f"**Avg Goals/Match:** {team_stats['avg_goals_for']}")
    st.write(f"**Clean Sheets:** {team_stats['clean_sheets']}")
    st.write(f"**Avg Shots:** {team_stats['avg_shots']}")
    st.write(f"**Shot Accuracy:** {team_stats['shot_accuracy']}%")
    st.write(f"**Avg Fouls:** {team_stats['avg_fouls']}")
    st.write(f"**Avg Corners:** {team_stats['avg_corners']}")
    st.write(f"**Yellow Cards:** {team_stats['total_yellows']}")
    st.write(f"**Red Cards:** {team_stats['total_reds']}")

st.markdown("---")

if venue is None:
    st.subheader("Home vs Away Comparison")
    home_stats = get_team_stats(df, selected_team, 'home')
    away_stats = get_team_stats(df, selected_team, 'away')
    all_stats = get_team_stats(df, selected_team, None)
    fig_comparison = plot_home_away_comparison(all_stats, home_stats, away_stats, selected_team)
    st.plotly_chart(fig_comparison, width="stretch")
    st.markdown("---")

st.subheader("Recent Form Timeline")
num_matches = st.slider("Number of recent matches", 3, 10, 5)
fig_form = plot_form_timeline(df, selected_team, num_matches)
st.plotly_chart(fig_form, width="stretch")

page_footer()
