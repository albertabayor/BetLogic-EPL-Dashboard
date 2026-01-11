"""
EPL Analytics Dashboard - Main Landing Page

Streamlit multi-page application entry point.
Use the sidebar to navigate to different pages.
"""

import streamlit as st
from shared import load_data, inject_custom_css

st.set_page_config(
    page_title="EPL Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
df = load_data()

# Inject custom CSS
inject_custom_css()

# Main landing page
st.title("⚽ EPL Analytics Dashboard 2024/2025")
st.markdown("---")

st.markdown("""
### Welcome to the EPL Analytics Dashboard

Explore comprehensive statistics, insights, and analysis for the English Premier League 2024/25 season.

**Navigate using the sidebar 👈🏻:**
""")

# Feature cards in columns
col1, col2, col3 = st.columns(3)

# Theme-aware card style
card_style = """
<style>
    .feature-card {
        padding: 1rem;
        background-color: rgba(240, 242, 246, 0.5);
        border-radius: 0.5rem;
        border-left: 4px solid #003399;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    .feature-card:hover {
        background-color: rgba(240, 242, 246, 0.8);
        transform: translateX(4px);
    }
    .feature-icon {
        font-size: 2rem;
    }
    .feature-title {
        font-weight: 600;
        margin: 0.5rem 0;
        color: inherit;
    }
    .feature-desc {
        font-size: 0.875rem;
        color: #7F8C8D;
    }
    .new-features-card {
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 0.5rem;
        color: white;
    }
</style>
"""

st.markdown(card_style, unsafe_allow_html=True)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">League Overview</div>
        <div class="feature-desc">Current standings, form tracker, and season progress charts</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⚔️</div>
        <div class="feature-title">Head-to-Head</div>
        <div class="feature-desc">Historical matchups and win probability predictions</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📅</div>
        <div class="feature-title">Form Calendar</div>
        <div class="feature-desc">Visual match results like GitHub contributions</div>
    </div>
    """, unsafe_allow_html=True)

    


with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⚽</div>
        <div class="feature-title">Team Analysis</div>
        <div class="feature-desc">Detailed performance metrics and radar charts</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🟨</div>
        <div class="feature-title">Referee & Discipline</div>
        <div class="feature-desc">Card statistics and discipline analysis</div>
    </div>
    """, unsafe_allow_html=True)


with col3:
    st.markdown("""
    <div class="feature-card" style="border-left-color: #9B59B6;">
        <div class="feature-icon">🔮</div>
        <div class="feature-title">Match Predictor</div>
        <div class="feature-desc">Interactive simulator with adjustable weights</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">💰</div>
        <div class="feature-title">Betting Insights</div>
        <div class="feature-desc">Odds analysis and value betting opportunities</div>
    </div>
    """, unsafe_allow_html=True)


    st.markdown("<div style='margin-top: 3.5rem;'></div>", unsafe_allow_html=True)

    


st.markdown("---")

# Quick stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Matches", len(df))

with col2:
    total_goals = df['FTHG'].sum() + df['FTAG'].sum()
    st.metric("Total Goals", int(total_goals))

with col3:
    avg_goals = total_goals / len(df) if len(df) > 0 else 0
    st.metric("Avg Goals/Match", f"{avg_goals:.2f}")

with col4:
    home_wins = len(df[df['FTR'] == 'H'])
    home_win_rate = home_wins / len(df) * 100 if len(df) > 0 else 0
    st.metric("Home Win Rate", f"{home_win_rate:.1f}%")

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p>Data provided by Football-Data.co.uk • Built with Streamlit</p>
    <p>Use the sidebar navigation to explore different pages</p>
</div>
""", unsafe_allow_html=True)
