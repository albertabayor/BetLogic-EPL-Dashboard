"""
EPL Analytics Dashboard - Compact Single Page
Designed for easy viewing with high contrast and clear typography.
Works in both Light and Dark modes.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from shared import load_data, inject_custom_css
from src.features import calculate_standings
from src.data_loader import get_all_teams

# Page config - Force Light Mode as default
st.set_page_config(
    page_title="EPL Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme-aware CSS for both Light and Dark modes
st.markdown("""
<style>
    /* ===== LIGHT MODE (default) ===== */
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #003399;
    }

    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        border-bottom: 3px solid #0052cc;
        padding-bottom: 0.5rem;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #003399;
    }

    /* Metric cards - always consistent */
    .metric-card {
        background: linear-gradient(135deg, #0052cc 0%, #003399 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1.2;
    }

    .metric-label {
        font-size: 1.1rem;
        font-weight: 600;
        opacity: 0.95;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Selectbox & Radio styling */
    .stSelectbox > div > div {
        font-size: 1.2rem;
        font-weight: 600;
    }

    .stRadio > div > div > label {
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* Tooltip help icon */
    .help-tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        margin-left: 8px;
    }

    .help-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        color: white;
        border-radius: 50%;
        font-size: 18px;
        font-weight: bold;
        transition: transform 0.2s ease;
        background: linear-gradient(135deg, #0052cc 0%, #003399 100%);
    }

    .help-icon:hover {
        transform: scale(1.15);
    }

    /* Tooltip text box */
    .tooltip-text {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        z-index: 1000;
        text-align: left;
        border-radius: 12px;
        padding: 25px 30px;
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: 90%;
        max-width: 900px;
        transition: opacity 0.3s ease, visibility 0.3s ease;
        font-size: 1.15rem;
        line-height: 1.7;
        border: 3px solid #0052cc;
        background-color: #ffffff;
        color: #000000;
        box-shadow: 0 4px 25px rgba(0, 82, 204, 0.3);
    }

    .tooltip-text strong {
        color: #003399;
        font-size: 1.3rem;
        font-weight: 700;
    }

    .help-tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }

    .section-with-tooltip {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-bottom: 1rem;
    }

    /* ===== DARK MODE OVERRIDES ===== */
    /* Streamlit adds [data-theme="dark"] when dark mode is active */
    [data-theme="dark"] .dashboard-title {
        color: #4A9EFF;
    }

    [data-theme="dark"] .section-header {
        color: #4A9EFF;
        border-bottom-color: #0066FF;
    }

    [data-theme="dark"] .tooltip-text {
        background-color: #1E1E1E;
        color: #E0E0E0;
        border-color: #0066FF;
        box-shadow: 0 4px 25px rgba(0, 102, 255, 0.4);
    }

    [data-theme="dark"] .tooltip-text strong {
        color: #4A9EFF;
    }

    [data-theme="dark"] .help-icon {
        background: linear-gradient(135deg, #0066FF 0%, #0044AA 100%);
    }
</style>
""", unsafe_allow_html=True)

# Load data
df = load_data()

# Inject custom CSS
inject_custom_css()

# ===== SIDEBAR FILTERS =====
st.sidebar.title("⚽ EPL Dashboard Filters")
st.sidebar.markdown("---")

# Team Filter in Sidebar
st.sidebar.markdown("### 🏃 Filter by Team")
selected_team_sidebar = st.sidebar.selectbox(
    "Select Team",
    options=["All Teams"] + sorted(get_all_teams(df)),
    index=0,
    label_visibility="collapsed",
    key="sidebar_team_filter"
)

st.sidebar.markdown("---")

# Chart Layout in Sidebar
st.sidebar.markdown("### 📊 Chart Layout")
chart_layout_sidebar = st.sidebar.radio(
    "Choose Layout",
    options=["Grid View (3 columns)", "Stacked View (one by one)"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**💡 Tips:**
• Hover over **?** icons for explanations
• Use filters to focus on specific teams
• Toggle layout for different views
""")

# ===== MAIN CONTENT =====

# Dashboard title
st.markdown('<div class="dashboard-title">⚽ EPL Dashboard 2024/2025</div>', unsafe_allow_html=True)

# Calculate standings
standings = calculate_standings(df)

# Filter data based on sidebar selection
if selected_team_sidebar == "All Teams":
    filtered_standings = standings
    chart_data = standings
else:
    filtered_standings = standings[standings['Team'] == selected_team_sidebar].copy()
    chart_data = filtered_standings

# Calculate summary metrics
total_points = filtered_standings['Pts'].sum()
total_wins = filtered_standings['W'].sum()
total_losses = filtered_standings['L'].sum()
total_draws = filtered_standings['D'].sum()
total_goals_for = filtered_standings['GF'].sum()
total_goals_against = filtered_standings['GA'].sum()
total_matches = filtered_standings['P'].sum()

st.markdown("---")

# 7 Metric Cards with tooltip
st.markdown("""
<div class="section-with-tooltip">
    <div class="section-header" style="margin-bottom: 0;">Summary Statistics</div>
    <div class="help-tooltip">
        <div class="help-icon">?</div>
        <div class="tooltip-text">
            <strong>📊 SUMMARY CARDS:</strong><br><br>
            • <strong>POINTS:</strong> Win = 3 pts | Draw = 1 pt | Loss = 0 pts. Higher points = better league rank.<br><br>
            • <strong>WINS:</strong> Matches where team scored MORE goals than opponent.<br><br>
            • <strong>LOSSES:</strong> Matches where team scored FEWER goals.<br><br>
            • <strong>DRAWS:</strong> Matches with SAME score (tie game).<br><br>
            • <strong>GOAL FAVOUR:</strong> Total goals SCORED by team.<br><br>
            • <strong>GOAL AGAINST:</strong> Total goals CONCEDED (opponents scored).<br><br>
            • <strong>MATCHES:</strong> Total games played this season.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_points}</div>
        <div class="metric-label">Points</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_wins}</div>
        <div class="metric-label">Wins</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_losses}</div>
        <div class="metric-label">Losses</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_draws}</div>
        <div class="metric-label">Draws</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_goals_for}</div>
        <div class="metric-label">Goal Favour</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_goals_against}</div>
        <div class="metric-label">Goal Against</div>
    </div>
    """, unsafe_allow_html=True)

with col7:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_matches}</div>
        <div class="metric-label">Matches</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Charts Section with tooltip
st.markdown("""
<div class="section-with-tooltip">
    <div class="section-header" style="margin-bottom: 0;">Team Statistics Charts</div>
    <div class="help-tooltip">
        <div class="help-icon">?</div>
        <div class="tooltip-text">
            <strong>📈 CHARTS EXPLAINED:</strong><br><br>
            <strong>TOP ROW:</strong><br>
            • <strong>DRAWS:</strong> Tie games. More draws = inconsistent team.<br><br>
            • <strong>GOALS:</strong> Blue = Scored | Dark Blue = Conceded. Compare offense vs defense.<br><br>
            • <strong>WINS:</strong> Total victories. Higher = stronger team.<br><br>
            <strong>BOTTOM ROW:</strong><br>
            • <strong>LOSSES:</strong> Total defeats. Higher = struggling team.<br><br>
            • <strong>POINTS:</strong> League rank (Win=3pts, Draw=1pt). Taller = better position.<br><br>
            • <strong>LEADERBOARD:</strong> Full ranking table. See "?" next to it for column meanings.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sort for better visualization
chart_data_draws = chart_data.sort_values('D', ascending=True)
chart_data_goals = chart_data.sort_values('GF', ascending=True)
chart_data_wins = chart_data.sort_values('W', ascending=True)
chart_data_losses = chart_data.sort_values('L', ascending=True)
chart_data_points = chart_data.sort_values('Pts', ascending=True)

# Define chart colors with high contrast
COLOR_PRIMARY = "#0052CC"
COLOR_SECONDARY = "#003399"
COLOR_SUCCESS = "#00CC96"
COLOR_DANGER = "#EF553B"
COLOR_WARNING = "#F5A623"
COLOR_INFO = "#00A3BF"

# Create charts with consistent styling for both themes
def create_horizontal_bar_chart(data, x_col, y_col, title, color):
    """Create a horizontal bar chart with consistent styling."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=data[x_col],
        y=data[y_col],
        orientation='h',
        marker_color=color,
        text=data[x_col],
        textposition='outside',
        textfont=dict(size=13, color='#333333'),
        hovertemplate='<b>%{y}</b><br>%{x}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color='#0052CC', family='Arial Black'),
            x=0.5,
            xanchor='center'
        ),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            title_font=dict(size=13, color='#666666'),
            tickfont=dict(size=12, color='#666666'),
        ),
        yaxis=dict(
            showgrid=False,
            title_font=dict(size=13, color='#666666'),
            tickfont=dict(size=12, color='#333333'),
            autorange='reversed'
        ),
        showlegend=False
    )

    return fig

def create_stacked_bar_chart(data, y_col, x1_col, x2_col, title):
    """Create a stacked horizontal bar chart for goals."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=data[y_col],
        x=data[x1_col],
        orientation='h',
        name='Goal Favour',
        marker_color=COLOR_PRIMARY,
        text=data[x1_col],
        textposition='inside',
        insidetextfont=dict(size=11, color='white'),
        hovertemplate='<b>%{y}</b><br>Goal Favour: %{x}<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        y=data[y_col],
        x=data[x2_col],
        orientation='h',
        name='Goal Against',
        marker_color=COLOR_SECONDARY,
        text=data[x2_col],
        textposition='inside',
        insidetextfont=dict(size=11, color='white'),
        hovertemplate='<b>%{y}</b><br>Goal Against: %{x}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color='#0052CC', family='Arial Black'),
            x=0.5,
            xanchor='center'
        ),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        barmode='stack',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            title_font=dict(size=13, color='#666666'),
            tickfont=dict(size=12, color='#666666'),
        ),
        yaxis=dict(
            showgrid=False,
            title_font=dict(size=13, color='#666666'),
            tickfont=dict(size=12, color='#333333'),
            autorange='reversed'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(size=13, color='#666666')
        ),
        hovermode='y unified'
    )

    return fig

def create_vertical_bar_chart(data, x_col, y_col, title, color):
    """Create a vertical bar chart for points."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=data[x_col],
        y=data[y_col],
        marker_color=color,
        text=data[y_col],
        textposition='outside',
        textfont=dict(size=13, color='#333333'),
        hovertemplate='<b>%{x}</b><br>%{y} points<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color='#0052CC', family='Arial Black'),
            x=0.5,
            xanchor='center'
        ),
        height=400,
        margin=dict(l=20, r=20, t=50, b=80),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(
            showgrid=False,
            title_font=dict(size=13, color='#666666'),
            tickfont=dict(size=11, color='#666666'),
            tickangle=-45
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            title_font=dict(size=13, color='#666666'),
            tickfont=dict(size=12, color='#666666')
        ),
        showlegend=False
    )

    return fig

# Render charts based on selected layout from sidebar
if chart_layout_sidebar == "Grid View (3 columns)":
    # ===== GRID LAYOUT (3 columns) =====

    # Row 1: Draws by Team, Goal Favour & Against, Wins by Team
    col1, col2, col3 = st.columns(3)

    with col1:
        fig_draws = create_horizontal_bar_chart(
            chart_data_draws, 'D', 'Team',
            'DRAWS BY TEAM',
            COLOR_WARNING
        )
        st.plotly_chart(fig_draws, width='stretch')

    with col2:
        fig_goals = create_stacked_bar_chart(
            chart_data_goals, 'Team', 'GF', 'GA',
            'GOAL FAVOUR & AGAINST BY TEAM'
        )
        st.plotly_chart(fig_goals, width='stretch')

    with col3:
        fig_wins = create_horizontal_bar_chart(
            chart_data_wins, 'W', 'Team',
            'WINS BY TEAM',
            COLOR_SUCCESS
        )
        st.plotly_chart(fig_wins, width='stretch')

    # Row 2: Losses by Team, Points by Team, Leaderboard
    col1, col2, col3 = st.columns(3)

    with col1:
        fig_losses = create_horizontal_bar_chart(
            chart_data_losses, 'L', 'Team',
            'LOSES BY TEAM',
            COLOR_DANGER
        )
        st.plotly_chart(fig_losses, width='stretch')

    with col2:
        fig_points = create_vertical_bar_chart(
            chart_data_points, 'Team', 'Pts',
            'POINTS BY TEAM',
            COLOR_PRIMARY
        )
        st.plotly_chart(fig_points, width='stretch')

    with col3:
        st.markdown("""
        <div class="section-with-tooltip">
            <div class="section-header" style="margin-bottom: 0;">Leaderboard</div>
            <div class="help-tooltip">
                <div class="help-icon">?</div>
                <div class="tooltip-text">
                    <strong>📋 COLUMN DEFINITIONS:</strong><br><br>
                    • <strong>PL (Played):</strong> Total games played.<br><br>
                    • <strong>W (Wins):</strong> Matches won. Each = 3 points.<br><br>
                    • <strong>L (Losses):</strong> Matches lost. Each = 0 points.<br><br>
                    • <strong>D (Draws):</strong> Tie games. Each = 1 point.<br><br>
                    • <strong>Pts:</strong> Total points. Formula: (Wins × 3) + (Draws × 1). Higher = better rank.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Leaderboard toggle
        show_all = st.radio(
            "Show",
            options=["All", "Top 10"],
            horizontal=True,
            label_visibility="collapsed"
        )

        # Prepare leaderboard data
        lb_data = standings.copy()
        if show_all == "Top 10":
            lb_data = lb_data.head(10)

        # Add total row if showing all
        if show_all == "All":
            total_row = {
                'Pos': '',
                'Team': '**TOTAL**',
                'P': lb_data['P'].sum(),
                'W': lb_data['W'].sum(),
                'L': lb_data['L'].sum(),
                'D': lb_data['D'].sum(),
                'GF': lb_data['GF'].sum(),
                'GA': lb_data['GA'].sum(),
                'GD': lb_data['GD'].sum(),
                'Pts': lb_data['Pts'].sum(),
                'Form': ''
            }
            lb_data = pd.concat([lb_data, pd.DataFrame([total_row])], ignore_index=True)

        # Display leaderboard
        leaderboard_display = lb_data[['Team', 'P', 'W', 'L', 'D', 'Pts']].copy()
        leaderboard_display.columns = ['Team', 'PL', 'W', 'L', 'D', 'Pts']

        st.dataframe(
            leaderboard_display,
            use_container_width=True,
            hide_index=True,
            height=400
        )

else:  # ===== STACKED LAYOUT (one by one) =====

    # Chart 1: Draws by Team
    st.markdown("#### DRAWS BY TEAM")
    fig_draws = create_horizontal_bar_chart(
        chart_data_draws, 'D', 'Team',
        'DRAWS BY TEAM',
        COLOR_WARNING
    )
    st.plotly_chart(fig_draws, width='stretch')
    st.markdown("---")

    # Chart 2: Goal Favour & Against by Team
    st.markdown("#### GOAL FAVOUR & AGAINST BY TEAM")
    fig_goals = create_stacked_bar_chart(
        chart_data_goals, 'Team', 'GF', 'GA',
        'GOAL FAVOUR & AGAINST BY TEAM'
    )
    st.plotly_chart(fig_goals, width='stretch')
    st.markdown("---")

    # Chart 3: Wins by Team
    st.markdown("#### WINS BY TEAM")
    fig_wins = create_horizontal_bar_chart(
        chart_data_wins, 'W', 'Team',
        'WINS BY TEAM',
        COLOR_SUCCESS
    )
    st.plotly_chart(fig_wins, width='stretch')
    st.markdown("---")

    # Chart 4: Losses by Team
    st.markdown("#### LOSSES BY TEAM")
    fig_losses = create_horizontal_bar_chart(
        chart_data_losses, 'L', 'Team',
        'LOSES BY TEAM',
        COLOR_DANGER
    )
    st.plotly_chart(fig_losses, width='stretch')
    st.markdown("---")

    # Chart 5: Points by Team
    st.markdown("#### POINTS BY TEAM")
    fig_points = create_vertical_bar_chart(
        chart_data_points, 'Team', 'Pts',
        'POINTS BY TEAM',
        COLOR_PRIMARY
    )
    st.plotly_chart(fig_points, width='stretch')
    st.markdown("---")

    # Leaderboard
    st.markdown("""
    <div class="section-with-tooltip">
        <div class="section-header" style="margin-bottom: 0;">Leaderboard</div>
        <div class="help-tooltip">
            <div class="help-icon">?</div>
            <div class="tooltip-text">
                <strong>📋 COLUMN DEFINITIONS:</strong><br><br>
                • <strong>PL (Played):</strong> Total games played.<br><br>
                • <strong>W (Wins):</strong> Matches won. Each = 3 points.<br><br>
                • <strong>L (Losses):</strong> Matches lost. Each = 0 points.<br><br>
                • <strong>D (Draws):</strong> Tie games. Each = 1 point.<br><br>
                • <strong>Pts:</strong> Total points. Formula: (Wins × 3) + (Draws × 1). Higher = better rank.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Leaderboard toggle
    show_all = st.radio(
        "Show",
        options=["All", "Top 10"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # Prepare leaderboard data
    lb_data = standings.copy()
    if show_all == "Top 10":
        lb_data = lb_data.head(10)

    # Add total row if showing all
    if show_all == "All":
        total_row = {
            'Pos': '',
            'Team': '**TOTAL**',
            'P': lb_data['P'].sum(),
            'W': lb_data['W'].sum(),
            'L': lb_data['L'].sum(),
            'D': lb_data['D'].sum(),
            'GF': lb_data['GF'].sum(),
            'GA': lb_data['GA'].sum(),
            'GD': lb_data['GD'].sum(),
            'Pts': lb_data['Pts'].sum(),
            'Form': ''
        }
        lb_data = pd.concat([lb_data, pd.DataFrame([total_row])], ignore_index=True)

    # Display leaderboard
    leaderboard_display = lb_data[['Team', 'P', 'W', 'L', 'D', 'Pts']].copy()
    leaderboard_display.columns = ['Team', 'PL', 'W', 'L', 'D', 'Pts']

    st.dataframe(
        leaderboard_display,
        use_container_width=True,
        hide_index=True,
        height=400
    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1.5rem; color: #666; font-size: 0.95rem;">
    <p><strong>EPL Analytics Dashboard</strong> • Data provided by Football-Data.co.uk</p>
    <p>Built with Streamlit • 2024/2025 Season</p>
</div>
""", unsafe_allow_html=True)
