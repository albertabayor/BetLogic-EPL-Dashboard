"""
Page 1: League Overview

Displays the current standings, top performers, and season progress charts.
"""

import streamlit as st
import pandas as pd
from src.features import calculate_standings, calculate_momentum_score
from src.visualizations import plot_season_progress
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import load_data, page_header, page_footer, inject_custom_css, format_form_badges

# Set page config
st.set_page_config(
    page_title="League Overview | EPL Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #003399;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #666;
        font-size: 0.8rem;
        border-top: 1px solid #e0e0e0;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize theme
inject_custom_css()

# Load data
df = load_data()

# Page header
page_header("League Overview", "Current standings and season analysis")

# Calculate standings
standings = calculate_standings(df)

# Ensure numeric columns are properly typed
standings = standings.astype({
    'Pos': int,
    'P': int,
    'W': int,
    'D': int,
    'L': int,
    'GF': int,
    'GA': int,
    'GD': int,
    'Pts': int
})

# Layout: Top metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_matches = len(df)
    st.metric("Total Matches", total_matches)

with col2:
    total_goals = df['FTHG'].sum() + df['FTAG'].sum()
    st.metric("Total Goals", int(total_goals))

with col3:
    avg_goals = total_goals / total_matches if total_matches > 0 else 0
    st.metric("Avg Goals/Match", f"{avg_goals:.2f}")

with col4:
    home_wins = len(df[df['FTR'] == 'H'])
    home_win_rate = home_wins / total_matches * 100 if total_matches > 0 else 0
    st.metric("Home Win Rate", f"{home_win_rate:.1f}%")

st.markdown("---")

# Top Performers Section
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("League Standings")

    # Create display dataframe with emoji badges for form
    display_df = standings.copy()
    display_df['Form'] = display_df['Form'].apply(format_form_badges)

    # Apply row styling based on position with proper text colors
    def color_rows(row):
        """Apply background and text color based on league position."""
        pos = row['Pos']
        if pos <= 4:  # Champions League
            return ['background-color: #E6F3FF; color: #003399; font-weight: 500;'] * len(row)
        elif pos <= 6:  # Europa League
            return ['background-color: #FFF4E6; color: #995800; font-weight: 500;'] * len(row)
        elif pos <= 7:  # Conference League
            return ['background-color: #F0E6FF; color: #6B3FA0; font-weight: 500;'] * len(row)
        elif pos >= len(display_df) - 2:  # Relegation Zone (last 3)
            return ['background-color: #FFE6E6; color: #991B1B; font-weight: 500;'] * len(row)
        else:
            return [''] * len(row)

    # Apply styling to dataframe
    styled_df = display_df.style.apply(color_rows, axis=1)

    st.dataframe(
        styled_df,
        column_config={
            "Pos": st.column_config.NumberColumn("Pos", width="small"),
            "Team": st.column_config.TextColumn("Team", width="medium"),
            "P": st.column_config.NumberColumn("P", width="small"),
            "W": st.column_config.NumberColumn("W", width="small"),
            "D": st.column_config.NumberColumn("D", width="small"),
            "L": st.column_config.NumberColumn("L", width="small"),
            "GF": st.column_config.NumberColumn("GF", width="small"),
            "GA": st.column_config.NumberColumn("GA", width="small"),
            "GD": st.column_config.NumberColumn("GD", width="small"),
            "Pts": st.column_config.NumberColumn("Pts", width="small"),
            "Form": st.column_config.TextColumn("Form", width="large"),
        },
        hide_index=True,
        width="stretch"
    )

    # Legend
    st.markdown("""
    <div style="font-size: 0.8rem; margin-top: 10px;">
        <span style="display: inline-block; width: 15px; height: 15px; background-color: #E6F3FF; border: 1px solid #003399; margin-right: 5px;"></span> Champions League
        <span style="display: inline-block; width: 15px; height: 15px; background-color: #FFF4E6; border: 1px solid #FF9500; margin-right: 5px; margin-left: 15px;"></span> Europa League
        <span style="display: inline-block; width: 15px; height: 15px; background-color: #F0E6FF; border: 1px solid #9B59B6; margin-right: 5px; margin-left: 15px;"></span> Conference League
        <span style="display: inline-block; width: 15px; height: 15px; background-color: #FFE6E6; border: 1px solid #EF553B; margin-right: 5px; margin-left: 15px;"></span> Relegation Zone
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.subheader("Top Performers")

    # Top Scorers
    top_scorers = standings.nlargest(5, 'GF')[['Team', 'GF']].copy()
    st.write("**Top Scorers**")
    for idx, row in top_scorers.iterrows():
        st.write(f"{idx + 1}. {row['Team']}: {row['GF']} goals")

    st.write("")

    # Best Defense
    best_defense = standings.nsmallest(5, 'GA')[['Team', 'GA']].copy()
    st.write("**Best Defense**")
    for idx, row in best_defense.iterrows():
        st.write(f"{idx + 1}. {row['Team']}: {row['GA']} conceded")

    st.write("")

    # Momentum Leaders
    momentum_scores = []
    for team in standings['Team']:
        score = calculate_momentum_score(df, team)
        momentum_scores.append({'Team': team, 'Momentum': score})

    momentum_df = pd.DataFrame(momentum_scores).sort_values('Momentum', ascending=False).head(5)
    st.write("**Momentum Leaders**")
    for idx, row in momentum_df.iterrows():
        st.write(f"{idx + 1}. {row['Team']}: {row['Momentum']:.1f}")

st.markdown("---")

# Season Progress Chart
st.subheader("Season Progress")

# Team selection for chart
all_teams = sorted(standings['Team'].tolist())
default_teams = standings.head(6)['Team'].tolist()

selected_teams = st.multiselect(
    "Select teams to compare",
    options=all_teams,
    default=default_teams,
    label_visibility="collapsed"
)

if selected_teams:
    fig = plot_season_progress(df, selected_teams)
    st.plotly_chart(fig, width="stretch")
else:
    st.info("Select teams to view their season progress")

# Footer
page_footer()
