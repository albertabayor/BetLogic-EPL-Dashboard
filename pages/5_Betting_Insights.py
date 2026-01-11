"""
Page 5: Betting Insights

Odds analysis, value bet detection, and bookmaker comparisons.
"""

import streamlit as st
import pandas as pd
from src.visualizations import plot_odds_movement, plot_over_under_analysis, plot_bookmaker_comparison
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import load_data, page_header, page_footer, inject_custom_css

st.set_page_config(
    page_title="Betting Insights | EPL Analytics",
    page_icon="💰",
    layout="wide"
)

df = load_data()
page_header("Betting Insights", "Odds analysis and value betting opportunities")

# Initialize theme
inject_custom_css()

# Check if odds columns exist
odds_cols = ['AvgH', 'AvgD', 'AvgA', 'B365H', 'B365D', 'B365A', 'Avg>2.5', 'Avg<2.5']
available_odds = [col for col in odds_cols if col in df.columns]

if len(available_odds) == 0:
    st.error("No betting odds data available in the dataset.")
    st.info("Please ensure your dataset includes odds columns (B365H, AvgH, etc.)")
    st.stop()

# Top metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_home_win = df['AvgH'].mean() if 'AvgH' in df.columns else 0
    st.metric("Avg Home Win Odds", f"{avg_home_win:.2f}")
with col2:
    avg_draw = df['AvgD'].mean() if 'AvgD' in df.columns else 0
    st.metric("Avg Draw Odds", f"{avg_draw:.2f}")
with col3:
    avg_away_win = df['AvgA'].mean() if 'AvgA' in df.columns else 0
    st.metric("Avg Away Win Odds", f"{avg_away_win:.2f}")
with col4:
    if 'Avg>2.5' in df.columns and 'Avg<2.5' in df.columns:
        avg_over = df['Avg>2.5'].mean()
        st.metric("Avg Over 2.5", f"{avg_over:.2f}")

st.markdown("---")

# Odds Movement Chart
st.subheader("Odds Movement by Matchweek")
if 'AvgH' in df.columns and 'AvgD' in df.columns and 'AvgA' in df.columns:
    fig_odds = plot_odds_movement(df)
    st.plotly_chart(fig_odds, width="stretch")

st.markdown("---")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Over/Under 2.5 Goals Analysis")
    if 'Avg>2.5' in df.columns and 'Avg<2.5' in df.columns:
        fig_ou = plot_over_under_analysis(df)
        st.plotly_chart(fig_ou, width="stretch")

        # ROI Simulation
        st.write("**ROI Simulation**")
        df_goals = df.copy()
        df_goals['TotalGoals'] = df_goals['FTHG'] + df_goals['FTAG']
        df_goals['OverWon'] = (df_goals['TotalGoals'] > 2.5).astype(int)

        total_matches = len(df_goals)
        over_wins = df_goals['OverWon'].sum()

        if 'Avg>2.5' in df.columns:
            avg_odds_over = df_goals['Avg>2.5'].mean()
            stake = 100
            total_staked = stake * total_matches
            total_return = over_wins * stake * avg_odds_over
            profit = total_return - total_staked
            roi = (profit / total_staked) * 100

            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("Total Bets", total_matches)
            with col_r2:
                st.metric("Win Rate", f"{over_wins / total_matches * 100:.1f}%")
            with col_r3:
                profit_color = "normal" if profit >= 0 else "inverse"
                st.metric("Profit/Loss", f"£{profit:.2f}", delta=f"{roi:.1f}%", delta_color=profit_color)

with right_col:
    st.subheader("Value Bet Detector")
    st.write("""
    **What are Value Bets?**

    A value bet occurs when the implied probability from odds differs significantly from the actual outcome probability.

    *Note: This is a simplified analysis for educational purposes.*
    """)

    # Find potential value bets
    if 'AvgH' in df.columns and 'AvgD' in df.columns and 'AvgA' in df.columns:
        value_bets = []
        for idx, row in df.iterrows():
            implied_h = 1 / row['AvgH'] if row['AvgH'] > 0 else 0
            implied_d = 1 / row['AvgD'] if row['AvgD'] > 0 else 0
            implied_a = 1 / row['AvgA'] if row['AvgA'] > 0 else 0

            actual = row['FTR']

            if actual == 'H' and implied_h < 0.5:
                value_bets.append({
                    'Date': row['Date'],
                    'HomeTeam': row['HomeTeam'],
                    'AwayTeam': row['AwayTeam'],
                    'BetType': 'Home Win',
                    'Odds': row['AvgH']
                })
            elif actual == 'D' and implied_d < 0.35:
                value_bets.append({
                    'Date': row['Date'],
                    'HomeTeam': row['HomeTeam'],
                    'AwayTeam': row['AwayTeam'],
                    'BetType': 'Draw',
                    'Odds': row['AvgD']
                })
            elif actual == 'A' and implied_a < 0.5:
                value_bets.append({
                    'Date': row['Date'],
                    'HomeTeam': row['HomeTeam'],
                    'AwayTeam': row['AwayTeam'],
                    'BetType': 'Away Win',
                    'Odds': row['AvgA']
                })

        if value_bets:
            st.success(f"Found {len(value_bets)} potential value bets!")
        else:
            st.info("No clear value bets detected in recent matches.")

st.markdown("---")

# Bookmaker Comparison
st.subheader("Bookmaker Comparison")
bookmaker_cols = ['B365H', 'BWH', 'PSH', 'WHH']
available_bookmakers = [col for col in bookmaker_cols if col in df.columns]

if len(available_bookmakers) > 0:
    fig_bookie = plot_bookmaker_comparison(df)
    st.plotly_chart(fig_bookie, width="stretch")

st.markdown("---")

# Betting Tips Disclaimer
st.info("""
**Disclaimer**: This dashboard is for informational and educational purposes only.
The analysis presented here does not constitute financial or betting advice.
Always gamble responsibly and only bet what you can afford to lose.
""")

page_footer()
