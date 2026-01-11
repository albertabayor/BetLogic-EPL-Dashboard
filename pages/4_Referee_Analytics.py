"""
Page 4: Referee & Discipline

Referee statistics, card distributions, and discipline analysis.
"""

import streamlit as st
import pandas as pd
from src.features import get_referee_stats, get_team_stats, calculate_standings
from src.visualizations import plot_card_distribution_heatmap, plot_fouls_vs_points
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import load_data, page_header, page_footer, inject_custom_css

st.set_page_config(
    page_title="Referee Analytics | EPL Analytics",
    page_icon="🟨",
    layout="wide"
)

df = load_data()
page_header("Referee & Discipline", "Card statistics and discipline analysis")

# Initialize theme
inject_custom_css()

referee_stats = get_referee_stats(df)

if len(referee_stats) == 0:
    st.warning("No referee data available in the dataset.")
    st.stop()

# Top metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_yellows = referee_stats['Yellow Cards'].sum() / referee_stats['Matches'].sum()
    st.metric("Avg Yellows/Match", f"{avg_yellows:.2f}")
with col2:
    avg_reds = referee_stats['Red Cards'].sum() / referee_stats['Matches'].sum()
    st.metric("Avg Reds/Match", f"{avg_reds:.2f}")
with col3:
    total_cards = referee_stats['Yellow Cards'].sum() + referee_stats['Red Cards'].sum()
    st.metric("Total Cards", int(total_cards))
with col4:
    st.metric("Active Referees", len(referee_stats))

st.markdown("---")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Referee Leaderboard")
    min_matches = st.slider("Minimum matches refereed", 1, int(referee_stats['Matches'].max()), 5)
    filtered_refs = referee_stats[referee_stats['Matches'] >= min_matches].copy()
    sort_by = st.selectbox("Sort by", options=['Matches', 'Yellow Cards', 'Red Cards', 'Cards/Match', 'Fouls/Match'], index=0)
    ascending = sort_by not in ['Matches', 'Yellow Cards', 'Red Cards']
    filtered_refs = filtered_refs.sort_values(sort_by, ascending=ascending)

    st.dataframe(filtered_refs, hide_index=True, width="stretch")
    st.write(f"Showing {len(filtered_refs)} referees")

with right_col:
    st.subheader("Most Strict Referees")
    strictest_refs = referee_stats[referee_stats['Matches'] >= 5].nlargest(5, 'Cards/Match')
    for idx, row in strictest_refs.iterrows():
        st.write(f"**{row['Referee']}**")
        st.caption(f"{row['Cards/Match']:.2f} cards/match")

st.markdown("---")

# Card Distribution Heatmap
st.subheader("Card Distribution by Team")
fig_heatmap = plot_card_distribution_heatmap(df)
st.plotly_chart(fig_heatmap, width="stretch")

st.markdown("---")

# Fouls vs Points Correlation
st.subheader("Fouls vs Points Correlation")
col1, col2 = st.columns([3, 1])
with col1:
    fig_fouls = plot_fouls_vs_points(df)
    st.plotly_chart(fig_fouls, width="stretch")

with col2:
    st.write("**Analysis**")
    standings = calculate_standings(df)
    teams_data = []
    for team in standings['Team']:
        stats = get_team_stats(df, team)
        standings_row = standings[standings['Team'] == team].iloc[0]
        teams_data.append({
            'team': team,
            'fouls': stats.get('avg_fouls', 0),
            'points': standings_row['Pts']
        })
    fouls_df = pd.DataFrame(teams_data)
    if len(fouls_df) > 1:
        correlation = fouls_df['fouls'].corr(fouls_df['points'])
        st.metric("Correlation", f"{correlation:.3f}")
    st.info("Positive: More fouls = more points\nNegative: More fouls = fewer points")

st.markdown("---")

# Team Discipline Table
st.subheader("Team Discipline Overview")
standings = calculate_standings(df)
discipline_data = []

for team in standings['Team']:
    stats = get_team_stats(df, team)
    discipline_data.append({
        'Team': team,
        'Matches': stats['matches_played'],
        'Yellow Cards': stats['total_yellows'],
        'Red Cards': stats['total_reds'],
        'Total Cards': stats['total_yellows'] + stats['total_reds'],
        'Cards/Match': round((stats['total_yellows'] + stats['total_reds']) / max(stats['matches_played'], 1), 2),
        'Fouls/Match': round(stats['avg_fouls'], 2)
    })

discipline_df = pd.DataFrame(discipline_data).sort_values('Cards/Match')
st.dataframe(discipline_df, hide_index=True, width="stretch")

page_footer()
