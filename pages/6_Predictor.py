"""
Page 6: Match Predictor Simulator

Interactive match outcome prediction with adjustable weights and real-time updates.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import load_data, page_header, page_footer, inject_custom_css, format_form_badges
from src.features import get_head_to_head_stats, get_team_stats, calculate_standings
from src.data_loader import get_all_teams
from src.constants import TEAM_COLORS

st.set_page_config(
    page_title="Match Predictor | EPL Analytics",
    page_icon="🔮",
    layout="wide"
)

# Load data
df = load_data()
all_teams = get_all_teams(df)

# Initialize theme
inject_custom_css()

page_header("Match Predictor Simulator", "Adjust weights and see real-time predictions")

st.markdown("""
**How it works:** This simulator combines multiple factors to predict match outcomes.
Adjust the weights below to see how different factors impact the prediction.
""")

st.markdown("---")

# Team selection
col1, col2, col3 = st.columns([3, 1, 3])

with col1:
    team_a = st.selectbox("Home Team", options=all_teams, index=0, key="pred_team_a")

with col2:
    st.markdown("<div style='text-align: center; font-size: 2rem; padding-top: 1rem;'>VS</div>", unsafe_allow_html=True)

with col3:
    available_teams_b = [t for t in all_teams if t != team_a]
    team_b = st.selectbox("Away Team", options=available_teams_b, index=0, key="pred_team_b")

st.markdown("---")

# Calculate base stats
standings = calculate_standings(df)
home_stats = get_team_stats(df, team_a, None)
away_stats = get_team_stats(df, team_b, None)
h2h_stats = get_head_to_head_stats(df, team_a, team_b)

home_row = standings[standings['Team'] == team_a].iloc[0] if len(standings[standings['Team'] == team_a]) > 0 else None
away_row = standings[standings['Team'] == team_b].iloc[0] if len(standings[standings['Team'] == team_b]) > 0 else None

# Weight sliders in sidebar
with st.sidebar:
    st.subheader("⚖️ Prediction Weights")
    st.caption("Adjust how much each factor impacts the prediction")

    home_advantage = st.slider("Home Advantage", 0, 100, 15, help="Base percentage added to home team")
    form_weight = st.slider("Recent Form", 0, 100, 25, help="Impact of last 5 matches")
    h2h_weight = st.slider("Head-to-Head History", 0, 100, 20, help="Historical matchup results")
    table_weight = st.slider("League Position", 0, 100, 30, help="Current standing difference")
    goals_weight = st.slider("Goal Difference", 0, 100, 10, help="Goals scored/conceded ratio")

    st.markdown("---")
    st.subheader("📊 Current Factors")

    # Show current stats
    st.markdown(f"**{team_a}**")
    if home_row is not None:
        st.caption(f"Position: {home_row['Pos']}")
        st.caption(f"Points: {home_row['Pts']}")
        st.caption(f"GD: {home_row['GD']}")

    st.markdown(f"**{team_b}**")
    if away_row is not None:
        st.caption(f"Position: {away_row['Pos']}")
        st.caption(f"Points: {away_row['Pts']}")
        st.caption(f"GD: {away_row['GD']}")

    st.markdown("---")
    st.markdown(f"**Head-to-Head**")
    st.caption(f"{team_a}: {h2h_stats['team_a_wins']} wins")
    st.caption(f"Draws: {h2h_stats['draws']}")
    st.caption(f"{team_b}: {h2h_stats['team_b_wins']} wins")


# Calculate prediction scores
def calculate_prediction_scores():
    """Calculate prediction scores based on all factors."""

    # Base scores (start at 50-50)
    home_score = 50
    away_score = 50

    # Home advantage
    home_score += home_advantage

    # Recent form factor
    total_h2h = h2h_stats['total_matches']
    if total_h2h > 0:
        home_form_pct = (h2h_stats['team_a_wins'] / total_h2h) * 100
        away_form_pct = (h2h_stats['team_b_wins'] / total_h2h) * 100

        home_score += (home_form_pct - 50) * (h2h_weight / 100)
        away_score += (away_form_pct - 50) * (h2h_weight / 100)

    # Table position factor
    if home_row is not None and away_row is not None:
        pos_diff = home_row['Pos'] - away_row['Pos']
        # Negative pos_diff means home is higher (better)
        home_score += (-pos_diff * 2) * (table_weight / 100)
        away_score += (pos_diff * 2) * (table_weight / 100)

        # Points difference
        pts_diff = home_row['Pts'] - away_row['Pts']
        home_score += (pts_diff / 2) * (table_weight / 100)
        away_score += (-pts_diff / 2) * (table_weight / 100)

    # Goal difference factor
    if home_row is not None and away_row is not None:
        gd_diff = home_row['GD'] - away_row['GD']
        home_score += (gd_diff / 3) * (goals_weight / 100)
        away_score += (-gd_diff / 3) * (goals_weight / 100)

    # Form momentum (recent form string)
    home_form = home_row.get('Form', '') if home_row is not None else ''
    away_form = away_row.get('Form', '') if away_row is not None else ''

    def calculate_form_score(form_str):
        if not form_str or pd.isna(form_str):
            return 0
        score = 0
        for char in form_str[:5]:  # Last 5 matches
            if char == 'W':
                score += 3
            elif char == 'D':
                score += 1
            elif char == 'L':
                score -= 1
        return score

    home_form_score = calculate_form_score(home_form)
    away_form_score = calculate_form_score(away_form)

    home_score += (home_form_score * 2) * (form_weight / 100)
    away_score += (away_form_score * 2) * (form_weight / 100)

    # Normalize to 0-100 range
    total = home_score + away_score
    if total > 0:
        home_pct = (home_score / total) * 100
        away_pct = (away_score / total) * 100
    else:
        home_pct = 50
        away_pct = 50

    # Draw probability (higher when teams are closely matched)
    draw_pct = max(5, min(30, 25 - abs(home_pct - away_pct) / 2))

    # Adjust home/away to account for draw
    remaining = 100 - draw_pct
    home_final = (home_pct / (home_pct + away_pct)) * remaining
    away_final = (away_pct / (home_pct + away_pct)) * remaining

    return round(home_final, 1), round(draw_pct, 1), round(away_final, 1)


# Calculate predictions
home_win, draw, away_win = calculate_prediction_scores()

# Display prediction
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🔮 Prediction Result")

    # Create prediction bar chart
    fig = go.Figure()

    categories = [f"{team_a} Win", "Draw", f"{team_b} Win"]
    values = [home_win, draw, away_win]
    colors = ['#00CC96', '#F5F5F5', '#EF553B']

    for cat, val, color in zip(categories, values, colors):
        fig.add_trace(go.Bar(
            x=[val],
            y=[cat],
            orientation='h',
            name=cat,
            marker_color=color,
            text=[f"{val}%"],
            textposition='auto',
            textfont={'size': 16, 'color': 'black' if val > 15 else 'gray'},
        ))

    fig.update_layout(
        title="Match Outcome Probabilities",
        xaxis_title="Probability (%)",
        xaxis=dict(range=[0, 100]),
        yaxis=dict(categoryorder='total ascending'),
        height=250,
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False
    )

    st.plotly_chart(fig, width="stretch")

    # Confidence indicator
    abs_diff = abs(home_win - away_win)
    if abs_diff > 30:
        confidence = "High"
        confidence_color = "🟢"
    elif abs_diff > 15:
        confidence = "Medium"
        confidence_color = "🟡"
    else:
        confidence = "Low"
        confidence_color = "🔴"

    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.metric("Prediction Confidence", confidence)
    with col_c2:
        st.metric(f"{team_a} Win", f"{home_win}%")
    with col_c3:
        st.metric(f"{team_b} Win", f"{away_win}%")

with col_right:
    st.subheader("💡 Recommendation")

    if home_win > 50:
        rec_team = team_a
        rec_pct = home_win
        rec_emoji = "🏠"
    elif away_win > 50:
        rec_team = team_b
        rec_pct = away_win
        rec_emoji = "✈️"
    else:
        rec_team = "Draw"
        rec_pct = draw
        rec_emoji = "🤝"

    st.markdown(f"""
    <div style='text-align: center; padding: 1rem; background-color: #F0F2F6; border-radius: 0.5rem;'>
        <div style='font-size: 3rem;'>{rec_emoji}</div>
        <div style='font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;'>{rec_team}</div>
        <div style='font-size: 2rem; color: #00CC96;'>{rec_pct}%</div>
        <div style='font-size: 0.875rem; color: #666; margin-top: 0.5rem;'>probability</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("**Key Factors:**")
    if home_row is not None and away_row is not None:
        pos_diff = home_row['Pos'] - away_row['Pos']
        if pos_diff < 0:
            st.caption(f"📈 {team_a} is {-pos_diff} positions higher")
        elif pos_diff > 0:
            st.caption(f"📉 {team_b} is {pos_diff} positions higher")

    if h2h_stats['total_matches'] > 0:
        if h2h_stats['team_a_wins'] > h2h_stats['team_b_wins']:
            st.caption(f"🏆 {team_a} leads H2H {h2h_stats['team_a_wins']}-{h2h_stats['team_b_wins']}")
        elif h2h_stats['team_b_wins'] > h2h_stats['team_a_wins']:
            st.caption(f"🏆 {team_b} leads H2H {h2h_stats['team_b_wins']}-{h2h_stats['team_a_wins']}")

st.markdown("---")

# Detailed breakdown
st.subheader("📋 Detailed Factor Breakdown")

factor_data = []

# Form factor
home_form = home_row.get('Form', '') if home_row is not None else ''
away_form = away_row.get('Form', '') if away_row is not None else ''
factor_data.append({
    'Factor': 'Recent Form',
    f'{team_a}': format_form_badges(home_form) if home_form else 'N/A',
    f'{team_b}': format_form_badges(away_form) if away_form else 'N/A',
    'Weight': f"{form_weight}%"
})

# Table position
factor_data.append({
    'Factor': 'League Position',
    f'{team_a}': f"#{home_row['Pos']}" if home_row is not None else 'N/A',
    f'{team_b}': f"#{away_row['Pos']}" if away_row is not None else 'N/A',
    'Weight': f"{table_weight}%"
})

# Points
factor_data.append({
    'Factor': 'Points',
    f'{team_a}': str(home_row['Pts']) if home_row is not None else 'N/A',
    f'{team_b}': str(away_row['Pts']) if away_row is not None else 'N/A',
    'Weight': f"{table_weight}%"
})

# Goal Difference
factor_data.append({
    'Factor': 'Goal Difference',
    f'{team_a}': str(home_row['GD']) if home_row is not None else 'N/A',
    f'{team_b}': str(away_row['GD']) if away_row is not None else 'N/A',
    'Weight': f"{goals_weight}%"
})

# H2H
factor_data.append({
    'Factor': 'Head-to-Head',
    f'{team_a}': f"{h2h_stats['team_a_wins']} wins" if h2h_stats['total_matches'] > 0 else 'N/A',
    f'{team_b}': f"{h2h_stats['team_b_wins']} wins" if h2h_stats['total_matches'] > 0 else 'N/A',
    'Weight': f"{h2h_weight}%"
})

# Home advantage
factor_data.append({
    'Factor': 'Home Advantage',
    f'{team_a}': f"+{home_advantage}%",
    f'{team_b}': "0%",
    'Weight': "Base"
})

st.dataframe(
    pd.DataFrame(factor_data),
    hide_index=True,
    width="stretch"
)

st.info("""
💡 **Tip**: Adjust the weights in the sidebar to see how different factors impact the prediction.
For example, increase "Recent Form" weight to prioritize current team momentum over historical performance.
""")

page_footer()
