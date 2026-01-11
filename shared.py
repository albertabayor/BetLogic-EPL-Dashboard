"""
Shared utilities for EPL Dashboard pages.
"""

import streamlit as st
import pandas as pd
from pathlib import Path


def inject_custom_css():
    """Inject custom CSS that works with both light and dark themes."""
    css = """
<style>
    /* Main header - works with Streamlit theme */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #003399;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid currentColor;
        margin-bottom: 2rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: rgba(0, 0, 0, 0.6);
        font-size: 0.8rem;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
        margin-top: 3rem;
    }

    /* H2H score display */
    .h2h-score .team-name {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .h2h-score .score {
        font-size: 3rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }

    .h2h-score .label {
        font-size: 0.875rem;
        opacity: 0.7;
    }
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_data():
    """Load and cache the EPL dataset."""
    from src.data_loader import load_epl_data, validate_dataframe, clean_odds_columns

    data_path = Path(__file__).parent / "dataset" / "english2024-2025.csv"

    if not data_path.exists():
        st.error(f"Data file not found at: {data_path}")
        st.info("Please ensure the dataset file is in the 'dataset' folder.")
        st.stop()

    try:
        df = load_epl_data(str(data_path))
        df = clean_odds_columns(df)

        is_valid, errors = validate_dataframe(df)
        if not is_valid:
            st.error("Data validation failed:")
            for error in errors:
                st.error(f"  • {error}")
            st.stop()

        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please check the data file format and try again.")
        st.stop()


def format_form_badges(form_string: str) -> str:
    """Format form string with emoji badges (not HTML)."""
    if not form_string or pd.isna(form_string):
        return ""

    badges = []
    for char in form_string:
        if char == 'W':
            badges.append("✅")
        elif char == 'D':
            badges.append("⚪")
        elif char == 'L':
            badges.append("❌")
    return " ".join(badges)


def page_header(title: str, subtitle: str = ""):
    """Render a consistent page header."""
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)


def page_footer():
    """Render the footer."""
    st.markdown("""
    <div class="footer">
        <p>EPL Analytics Dashboard • Data provided by Football-Data.co.uk</p>
        <p>Built with Streamlit • Last updated: January 2026</p>
    </div>
    """, unsafe_allow_html=True)


def h2h_score_card(team_name: str, score: int, label: str, color: str = "#003399"):
    """Render an H2H score card as columns."""
    st.markdown(f"**<span style='color: {color}; font-size: 1.5rem;'>{team_name}</span>**", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 3rem; font-weight: 700; text-align: center;'>{score}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center; color: #666;'>{label}</div>", unsafe_allow_html=True)
