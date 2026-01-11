"""
Page 7: Form Calendar View

Visual calendar of match results like GitHub contributions graph.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared import load_data, page_header, page_footer, inject_custom_css, format_form_badges
from src.data_loader import get_all_teams
from src.features import get_team_stats

st.set_page_config(
    page_title="Form Calendar | EPL Analytics",
    page_icon="📅",
    layout="wide"
)

# Load data
df = load_data()
all_teams = get_all_teams(df)

# Initialize theme
inject_custom_css()

page_header("Form Calendar View", "Visual match results calendar like GitHub contributions")

st.markdown("""
This calendar shows every match result as a colored square, similar to GitHub's contribution graph.
Green = Win, Gray = Draw, Red = Loss. Hover over any square to see match details.
""")

st.markdown("---")

# Team selection
col1, col2 = st.columns([2, 1])

with col1:
    selected_team = st.selectbox("Select Team", options=all_teams, index=0)

with col2:
    view_mode = st.radio(
        "View Mode",
        options=["Season", "Home Only", "Away Only"],
        horizontal=True,
        label_visibility="collapsed"
    )

# Get team's matches
if view_mode == "Season":
    team_matches = df[
        ((df['HomeTeam'] == selected_team) | (df['AwayTeam'] == selected_team))
    ].copy()
elif view_mode == "Home Only":
    team_matches = df[df['HomeTeam'] == selected_team].copy()
else:
    team_matches = df[df['AwayTeam'] == selected_team].copy()

if len(team_matches) == 0:
    st.warning(f"No matches found for {selected_team} in the selected view.")
    st.stop()

# Sort by date
team_matches = team_matches.sort_values('Date').reset_index(drop=True)

# Determine result for each match
def get_match_result(row, team):
    """Get the result for the selected team."""
    if row['HomeTeam'] == team:
        if row['FTR'] == 'H':
            return 'W', 'Home', row['AwayTeam'], row['FTHG'], row['FTAG']
        elif row['FTR'] == 'D':
            return 'D', 'Home', row['AwayTeam'], row['FTHG'], row['FTAG']
        else:
            return 'L', 'Home', row['AwayTeam'], row['FTHG'], row['FTAG']
    else:
        if row['FTR'] == 'A':
            return 'W', 'Away', row['HomeTeam'], row['FTAG'], row['FTHG']
        elif row['FTR'] == 'D':
            return 'D', 'Away', row['HomeTeam'], row['FTAG'], row['FTHG']
        else:
            return 'L', 'Away', row['HomeTeam'], row['FTAG'], row['FTHG']

results = []
for idx, row in team_matches.iterrows():
    result, venue, opponent, goals_for, goals_against = get_match_result(row, selected_team)
    results.append({
        'Date': pd.to_datetime(row['Date']),
        'Result': result,
        'Venue': venue,
        'Opponent': opponent,
        'Score': f"{goals_for}-{goals_against}",
        'OpponentTeam': opponent
    })

results_df = pd.DataFrame(results)

# Color mapping - colors that work in both light and dark modes
color_map = {
    'W': '#2ECC71',  # Green (works on both themes)
    'D': '#95A5A6',  # Gray (works on both themes)
    'L': '#E74C3C'   # Red (works on both themes)
}

# Empty/neutral color for days without matches
empty_color = '#34495E'  # Dark gray that works on both themes

# Top metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    wins = (results_df['Result'] == 'W').sum()
    st.metric("Wins", wins, delta_color="normal")

with col2:
    draws = (results_df['Result'] == 'D').sum()
    st.metric("Draws", draws)

with col3:
    losses = (results_df['Result'] == 'L').sum()
    st.metric("Losses", losses, delta_color="inverse")

with col4:
    total = len(results_df)
    win_rate = (wins / total * 100) if total > 0 else 0
    st.metric("Win Rate", f"{win_rate:.1f}%")

st.markdown("---")

# Create calendar heatmap
st.subheader(f"📅 {selected_team} Match Calendar")

# Prepare data for heatmap
results_df['Week'] = results_df['Date'].dt.isocalendar().week
results_df['DayOfWeek'] = results_df['Date'].dt.dayofweek
results_df['Color'] = results_df['Result'].map(color_map)

# Get date range
date_range = pd.date_range(start=results_df['Date'].min(), end=results_df['Date'].max(), freq='D')

# Create a pivot table for the calendar
calendar_data = []
for date in date_range:
    day_matches = results_df[results_df['Date'].dt.date == date.date()]
    if len(day_matches) > 0:
        for _, match in day_matches.iterrows():
            calendar_data.append({
                'Date': date,
                'Week': date.isocalendar().week,
                'DayOfWeek': date.dayofweek,
                'Result': match['Result'],
                'Color': match['Color'],
                'Opponent': match['Opponent'],
                'Venue': match['Venue'],
                'Score': match['Score']
            })
    else:
        # Empty day - use neutral color
        calendar_data.append({
            'Date': date,
            'Week': date.isocalendar().week,
            'DayOfWeek': date.dayofweek,
            'Result': None,
            'Color': empty_color,
            'Opponent': None,
            'Venue': None,
            'Score': None
        })

calendar_df = pd.DataFrame(calendar_data)

# Create the heatmap with theme-aware colors
fig = go.Figure(data=go.Scatter(
    x=calendar_df['Week'],
    y=calendar_df['DayOfWeek'],
    mode='markers',
    marker=dict(
        size=20,
        color=calendar_df['Color'],
        symbol='square',
        line=dict(color='#7F8C8D', width=1)  # Neutral gray border
    ),
    customdata=calendar_df[['Date', 'Result', 'Opponent', 'Venue', 'Score']],
    hovertemplate='<b>%{customdata[0]|%a, %b %d, %Y}</b><br>' +
                  'Result: %{customdata[1]}<br>' +
                  'vs %{customdata[2]} (%{customdata[3]})<br>' +
                  'Score: %{customdata[4]}<br>' +
                  '<extra></extra>',
    showlegend=False
))

# Update layout with theme-aware colors
fig.update_layout(
    title=f"{selected_team} - Match Results Calendar ({view_mode})",
    xaxis_title="Week of Year",
    xaxis=dict(
        gridcolor='rgba(0,0,0,0.1)',  # Subtle grid
        showgrid=True
    ),
    yaxis=dict(
        tickmode='array',
        tickvals=[0, 1, 2, 3, 4, 5, 6],
        ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        autorange="reversed",
        gridcolor='rgba(0,0,0,0.1)',  # Subtle grid
        showgrid=True
    ),
    height=300,
    margin=dict(l=50, r=20, t=50, b=50),
    plot_bgcolor='rgba(0,0,0,0)',  # Transparent, adapts to theme
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent, adapts to theme
    font_color='#7F8C8D',  # Neutral gray text
    hovermode='closest'
)

st.plotly_chart(fig, width="stretch")

# Legend with theme-aware colors
col_l1, col_l2, col_l3 = st.columns(3)
with col_l1:
    st.markdown("<div style='display: flex; align-items: center; gap: 0.5rem;'><div style='width: 20px; height: 20px; background-color: #2ECC71; border-radius: 3px;'></div><span>Win</span></div>", unsafe_allow_html=True)
with col_l2:
    st.markdown("<div style='display: flex; align-items: center; gap: 0.5rem;'><div style='width: 20px; height: 20px; background-color: #95A5A6; border-radius: 3px;'></div><span>Draw</span></div>", unsafe_allow_html=True)
with col_l3:
    st.markdown("<div style='display: flex; align-items: center; gap: 0.5rem;'><div style='width: 20px; height: 20px; background-color: #E74C3C; border-radius: 3px;'></div><span>Loss</span></div>", unsafe_allow_html=True)

st.markdown("---")

# Monthly view
st.subheader("📊 Monthly Breakdown")

results_df['Month'] = results_df['Date'].dt.to_period('M').astype(str)

# Create monthly summary
monthly_summary = []
for month in results_df['Month'].unique():
    month_data = results_df[results_df['Month'] == month]
    monthly_summary.append({
        'Month': month,
        'Matches': int(len(month_data)),
        'Wins': int((month_data['Result'] == 'W').sum()),
        'Draws': int((month_data['Result'] == 'D').sum()),
        'Losses': int((month_data['Result'] == 'L').sum()),
        'Points': int((month_data['Result'] == 'W').sum() * 3 + (month_data['Result'] == 'D').sum()),
        'Win Rate': f"{((month_data['Result'] == 'W').sum() / len(month_data) * 100):.1f}%"
    })

monthly_df = pd.DataFrame(monthly_summary)

st.dataframe(
    monthly_df,
    column_config={
        "Month": st.column_config.TextColumn("Month", width="medium"),
        "Matches": st.column_config.NumberColumn("Matches", width="small"),
        "Wins": st.column_config.NumberColumn("Wins", width="small"),
        "Draws": st.column_config.NumberColumn("Draws", width="small"),
        "Losses": st.column_config.NumberColumn("Losses", width="small"),
        "Points": st.column_config.NumberColumn("Points", width="small"),
        "Win Rate": st.column_config.TextColumn("Win Rate", width="small"),
    },
    hide_index=True,
    width="stretch"
)

st.markdown("---")

# Recent form with badges
st.subheader("📈 Recent Form")

last_10 = results_df.tail(10)
form_string = ''.join(last_10['Result'].tolist())

col_f1, col_f2 = st.columns([2, 1])

with col_f1:
    st.markdown("### Last 10 Matches")
    st.markdown(f"<div style='font-size: 2rem; letter-spacing: 0.5rem;'>{format_form_badges(form_string)}</div>", unsafe_allow_html=True)

with col_f2:
    st.markdown("**Last 10 Stats**")
    w = (last_10['Result'] == 'W').sum()
    d = (last_10['Result'] == 'D').sum()
    l = (last_10['Result'] == 'L').sum()
    pts = w * 3 + d
    st.metric(f"Points", pts)
    st.caption(f"{w}W {d}D {l}L")

# Match list
st.markdown("---")
st.subheader("📋 Match List")

display_matches = results_df.copy()
display_matches['Date'] = display_matches['Date'].dt.strftime('%a, %d %b %Y')
display_matches = display_matches[['Date', 'Venue', 'Opponent', 'Result', 'Score']]
display_matches.columns = ['Date', 'Venue', 'Opponent', 'Result', 'Score']

# Add result badges
def result_badge(result):
    if result == 'W':
        return '✅ Win'
    elif result == 'D':
        return '⚪ Draw'
    else:
        return '❌ Loss'

display_matches['Result'] = display_matches['Result'].apply(result_badge)

st.dataframe(
    display_matches,
    column_config={
        "Date": st.column_config.TextColumn("Date", width="medium"),
        "Venue": st.column_config.TextColumn("Venue", width="small"),
        "Opponent": st.column_config.TextColumn("Opponent", width="medium"),
        "Result": st.column_config.TextColumn("Result", width="small"),
        "Score": st.column_config.TextColumn("Score", width="small"),
    },
    hide_index=True,
    width="stretch"
)

st.info("""
💡 **Tip**: Click on any square in the calendar to see match details including opponent, venue, and score.
Use the view selector to see all matches, home games only, or away games only.
""")

page_footer()
