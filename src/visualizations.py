"""
Visualization utilities for EPL Analytics Dashboard

This module contains all Plotly chart creation functions.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional

from .constants import TEAM_COLORS, RESULT_HOME_WIN, RESULT_DRAW, RESULT_AWAY_WIN


def apply_theme_settings(fig: go.Figure) -> go.Figure:
    """
    Apply theme-aware settings to a Plotly figure for both light and dark modes.

    Args:
        fig: Plotly figure to style

    Returns:
        Styled Plotly figure
    """
    fig.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent, adapts to theme
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent, adapts to theme
        font=dict(color='#7F8C8D'),  # Neutral text color for both themes
        title_font=dict(color='#7F8C8D'),
        xaxis=dict(
            gridcolor='rgba(127, 140, 141, 0.3)',  # Subtle grid
            zerolinecolor='rgba(127, 140, 141, 0.5)'
        ),
        yaxis=dict(
            gridcolor='rgba(127, 140, 141, 0.3)',  # Subtle grid
            zerolinecolor='rgba(127, 140, 141, 0.5)'
        )
    )
    return fig


def plot_season_progress(df: pd.DataFrame, teams: Optional[list] = None) -> go.Figure:
    """
    Create a line chart showing points accumulation over the season.

    Args:
        df: DataFrame with match results
        teams: List of teams to plot (default: top 6)

    Returns:
        Plotly figure
    """
    # Calculate cumulative points for each team
    from .features import calculate_standings

    standings = calculate_standings(df)

    # Default to top 6 if no teams specified
    if teams is None:
        teams = standings.head(6)['Team'].tolist()

    fig = go.Figure()

    # For each team, calculate cumulative points
    for team in teams:
        team_matches = df[
            (df['HomeTeam'] == team) | (df['AwayTeam'] == team)
        ].sort_values('Date').copy()

        team_matches['Points'] = team_matches.apply(
            lambda row: (
                3 if ((row['HomeTeam'] == team) & (row['FTR'] == RESULT_HOME_WIN)) or
                      ((row['AwayTeam'] == team) & (row['FTR'] == RESULT_AWAY_WIN))
                else 1 if row['FTR'] == RESULT_DRAW
                else 0
            ),
            axis=1
        )

        team_matches['CumPoints'] = team_matches['Points'].cumsum()
        team_matches['MatchNum'] = range(1, len(team_matches) + 1)

        color = TEAM_COLORS.get(team, '#003399')

        fig.add_trace(go.Scatter(
            x=team_matches['MatchNum'],
            y=team_matches['CumPoints'],
            mode='lines+markers',
            name=team,
            line=dict(color=color, width=3),
            marker=dict(size=6),
            hovertemplate=f'<b>{team}</b><br>Match: %{{x}}<br>Points: %{{y}}<extra></extra>'
        ))

    fig.update_layout(
        title='Season Progress - Points Accumulation',
        xaxis_title='Match Number',
        yaxis_title='Cumulative Points',
        hovermode='x unified',
        template='none',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return apply_theme_settings(fig)


def plot_team_performance_radar(stats: dict, team: str) -> go.Figure:
    """
    Create a radar chart showing team performance metrics.

    Args:
        stats: Dictionary of team statistics
        team: Team name

    Returns:
        Plotly figure
    """
    # Normalize values to 0-100 scale
    categories = ['Goals/Match', 'Shot Accuracy', 'Discipline', 'Clean Sheets', 'Win Rate']

    # Normalize values
    goals_norm = min(stats.get('avg_goals_for', 0) * 20, 100)  # 5 goals = max
    accuracy_norm = min(stats.get('shot_accuracy', 0), 100)
    discipline_norm = max(100 - stats.get('total_yellows', 0) * 2 - stats.get('total_reds', 0) * 10, 0)
    clean_sheets_norm = min(stats.get('clean_sheets', 0) * 10, 100)  # 10 clean sheets = max
    win_rate_norm = stats.get('win_rate', 0)

    values = [goals_norm, accuracy_norm, discipline_norm, clean_sheets_norm, win_rate_norm]

    # Get team color
    team_color = TEAM_COLORS.get(team, '#3498DB')

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=team,
        line_color=team_color,
        fillcolor=team_color,
        opacity=0.3
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(127, 140, 141, 0.3)',
                tickfont=dict(size=10, color='#7F8C8D')
            ),
            angularaxis=dict(
                gridcolor='rgba(127, 140, 141, 0.3)',
                tickfont=dict(size=12, color='#7F8C8D')
            ),
            bgcolor='rgba(0, 0, 0, 0)'
        ),
        showlegend=True,
        title_text=f'{team} - Performance Overview',
        title_font_size=16,
        title_font_color='#7F8C8D',
        height=450,
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='#7F8C8D'),
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


def plot_shot_efficiency(df: pd.DataFrame) -> go.Figure:
    """
    Create a scatter plot showing shot efficiency for all teams.

    Args:
        df: DataFrame with match results

    Returns:
        Plotly figure
    """
    from .features import calculate_standings

    standings = calculate_standings(df)

    teams_data = []

    for team in standings['Team']:
        home = df[df['HomeTeam'] == team]
        away = df[df['AwayTeam'] == team]

        total_shots = home['HS'].sum() + away['AS'].sum()
        shots_on_target = home['HST'].sum() + away['AST'].sum()
        goals = home['FTHG'].sum() + away['FTAG'].sum()

        teams_data.append({
            'Team': team,
            'Total Shots': total_shots,
            'Shots on Target': shots_on_target,
            'Goals': goals,
            'Accuracy': (shots_on_target / total_shots * 100) if total_shots > 0 else 0
        })

    plot_df = pd.DataFrame(teams_data)

    fig = go.Figure()

    for team in plot_df['Team']:
        team_data = plot_df[plot_df['Team'] == team].iloc[0]
        color = TEAM_COLORS.get(team, '#003399')

        fig.add_trace(go.Scatter(
            x=[team_data['Total Shots']],
            y=[team_data['Shots on Target']],
            mode='markers',
            name=team,
            marker=dict(
                size=team_data['Goals'] * 5 + 10,
                color=color,
                line=dict(color='#7F8C8D', width=1),  # Neutral gray border
                opacity=0.7
            ),
            hovertemplate=f'<b>{team}</b><br>Total Shots: {team_data["Total Shots"]}<br>On Target: {team_data["Shots on Target"]}<br>Goals: {team_data["Goals"]}<br>Accuracy: {team_data["Accuracy"]:.1f}%<extra></extra>'
        ))

    # Add diagonal line for reference (45-degree shot accuracy)
    max_shots = plot_df['Total Shots'].max()
    fig.add_trace(go.Scatter(
        x=[0, max_shots],
        y=[0, max_shots * 0.5],  # 50% accuracy reference
        mode='lines',
        name='50% Accuracy Reference',
        line=dict(color='gray', dash='dash'),
        hoverinfo='skip'
    ))

    fig.update_layout(
        title='Shot Efficiency - Bubble Size = Goals Scored',
        xaxis_title='Total Shots',
        yaxis_title='Shots on Target',
        template='none',
        height=500,
        hovermode='closest'
    )

    return apply_theme_settings(fig)


def plot_home_away_comparison(stats_all: dict, stats_home: dict, stats_away: dict, team: str) -> go.Figure:
    """
    Create a grouped bar chart comparing home vs away performance.

    Args:
        stats_all: Overall statistics
        stats_home: Home statistics
        stats_away: Away statistics
        team: Team name

    Returns:
        Plotly figure
    """
    categories = ['Win Rate', 'Goals/Match', 'Points/Match']

    home_values = [
        stats_home.get('win_rate', 0),
        stats_home.get('avg_goals_for', 0),
        (stats_home.get('points', 0) / max(stats_home.get('matches_played', 1), 1)) * 10
    ]

    away_values = [
        stats_away.get('win_rate', 0),
        stats_away.get('avg_goals_for', 0),
        (stats_away.get('points', 0) / max(stats_away.get('matches_played', 1), 1)) * 10
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=categories,
        y=home_values,
        name='Home',
        marker_color='#003399',
        text=[f'{v:.1f}' for v in home_values],
        textposition='auto'
    ))

    fig.add_trace(go.Bar(
        x=categories,
        y=away_values,
        name='Away',
        marker_color='#C8102E',
        text=[f'{v:.1f}' for v in away_values],
        textposition='auto'
    ))

    fig.update_layout(
        title=f'{team} - Home vs Away Performance',
        barmode='group',
        template='none',
        height=400,
        yaxis_title='Value'
    )

    return apply_theme_settings(fig)


def plot_form_timeline(df: pd.DataFrame, team: str, num_matches: int = 5) -> go.Figure:
    """
    Create a visual timeline showing recent match results.

    Args:
        df: DataFrame with match results
        team: Team name
        num_matches: Number of recent matches to show

    Returns:
        Plotly figure
    """
    from .features import calculate_form_for_team

    form = calculate_form_for_team(df, team, num_matches)

    if not form:
        fig = go.Figure()
        fig.update_layout(
            title=f'{team} - Recent Form',
            annotations=[dict(text='No matches played', xref='paper', yref='paper',
                             x=0.5, y=0.5, showarrow=False)]
        )
        return apply_theme_settings(fig)

    # Get actual match details
    home_matches = df[df['HomeTeam'] == team].copy()
    away_matches = df[df['AwayTeam'] == team].copy()

    home_matches['Venue'] = 'Home'
    away_matches['Venue'] = 'Away'

    home_matches['Opponent'] = home_matches['AwayTeam']
    away_matches['Opponent'] = away_matches['HomeTeam']

    home_matches['Score'] = home_matches['FTHG'].astype(str) + '-' + home_matches['FTAG'].astype(str)
    away_matches['Score'] = away_matches['FTAG'].astype(str) + '-' + away_matches['FTHG'].astype(str)

    home_matches['Result'] = home_matches['FTR'].apply(
        lambda x: 'W' if x == RESULT_HOME_WIN else ('D' if x == RESULT_DRAW else 'L')
    )
    away_matches['Result'] = away_matches['FTR'].apply(
        lambda x: 'W' if x == RESULT_AWAY_WIN else ('D' if x == RESULT_DRAW else 'L')
    )

    all_matches = pd.concat([
        home_matches[['Date', 'Venue', 'Opponent', 'Score', 'Result']],
        away_matches[['Date', 'Venue', 'Opponent', 'Score', 'Result']]
    ]).sort_values('Date', ascending=False).head(num_matches)

    # Reverse for display (oldest first)
    all_matches = all_matches.iloc[::-1]

    colors = {'W': '#00CC96', 'D': '#F5F5F5', 'L': '#EF553B'}

    fig = go.Figure()

    for idx, match in all_matches.iterrows():
        result = match['Result']
        color = colors.get(result, '#F5F5F5')

        fig.add_trace(go.Bar(
            x=[match['Opponent']],
            y=[1],
            name=result,
            marker_color=color,
            text=f"{match['Score']}<br>{match['Venue']}",
            textposition='inside',
            insidetextanchor='middle',
            hovertemplate=f"<b>{match['Opponent']}</b><br>Result: {result}<br>Score: {match['Score']}<br>Venue: {match['Venue']}<extra></extra>",
            showlegend=False
        ))

    fig.update_layout(
        title=f'{team} - Last {len(all_matches)} Matches Form',
        barmode='stack',
        template='none',
        height=300,
        xaxis_title='Opponent',
        yaxis_title='',
        yaxis_showticklabels=False
    )

    return apply_theme_settings(fig)


def plot_card_distribution_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Create a heatmap showing card distribution per team per matchweek.

    Args:
        df: DataFrame with match results

    Returns:
        Plotly figure
    """
    from .features import calculate_standings

    standings = calculate_standings(df)
    teams = standings['Team'].tolist()

    # Create team-card matrix
    team_cards = []

    for team in teams:
        home = df[df['HomeTeam'] == team]
        away = df[df['AwayTeam'] == team]

        total_cards = home[[COL_HY, COL_HR]].sum().sum() + away[[COL_AY, COL_AR]].sum().sum()
        avg_cards = total_cards / (len(home) + len(away)) if (len(home) + len(away)) > 0 else 0

        team_cards.append({
            'Team': team,
            'Avg Cards/Match': round(avg_cards, 2)
        })

    plot_df = pd.DataFrame(team_cards).sort_values('Avg Cards/Match', ascending=False)

    fig = go.Figure(data=go.Heatmap(
        z=plot_df['Avg Cards/Match'],
        x=['Avg Cards'],
        y=plot_df['Team'],
        colorscale='Reds',
        colorbar=dict(title='Cards/Match')
    ))

    fig.update_layout(
        title='Average Cards per Match by Team',
        xaxis_title='',
        yaxis_title='',
        height=800,
        template='none'
    )

    return apply_theme_settings(fig)


def plot_odds_movement(df: pd.DataFrame) -> go.Figure:
    """
    Create a line chart showing average odds movement over matchweeks.

    Args:
        df: DataFrame with match results and odds

    Returns:
        Plotly figure
    """
    # Group by date and calculate average odds
    df_with_date = df.copy()
    df_with_date['Matchweek'] = pd.factorize(df_with_date['Date'].dt.strftime('%Y-%m-%d'))[0] + 1

    weekly_odds = df_with_date.groupby('Matchweek').agg({
        'AvgH': 'mean',
        'AvgD': 'mean',
        'AvgA': 'mean'
    }).reset_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=weekly_odds['Matchweek'],
        y=weekly_odds['AvgH'],
        mode='lines+markers',
        name='Home Win Odds',
        line=dict(color='#00CC96', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=weekly_odds['Matchweek'],
        y=weekly_odds['AvgD'],
        mode='lines+markers',
        name='Draw Odds',
        line=dict(color='#F5F5F5', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=weekly_odds['Matchweek'],
        y=weekly_odds['AvgA'],
        mode='lines+markers',
        name='Away Win Odds',
        line=dict(color='#EF553B', width=2)
    ))

    fig.update_layout(
        title='Average Odds Movement by Matchweek',
        xaxis_title='Matchweek',
        yaxis_title='Average Odds',
        template='none',
        height=500,
        hovermode='x unified'
    )

    return apply_theme_settings(fig)


def plot_over_under_analysis(df: pd.DataFrame) -> go.Figure:
    """
    Create a pie chart comparing actual vs predicted over/under 2.5 goals.

    Args:
        df: DataFrame with match results and O/U odds

    Returns:
        Plotly figure
    """
    # Calculate actual over/under
    df['TotalGoals'] = df['FTHG'] + df['FTAG']
    actual_over = len(df[df['TotalGoals'] > 2.5])
    actual_under = len(df[df['TotalGoals'] <= 2.5])

    # Predicted based on odds
    if 'Avg>2.5' in df.columns and 'Avg<2.5' in df.columns:
        # Lower odds = more likely outcome
        predicted_over = len(df[df['Avg>2.5'] < df['Avg<2.5']])
        predicted_under = len(df[df['Avg<2.5'] <= df['Avg>2.5']])
    else:
        predicted_over = actual_over
        predicted_under = actual_under

    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=['Over 2.5', 'Under 2.5'],
        values=[actual_over, actual_under],
        name='Actual Results',
        hole=0.4,
        marker_colors=['#00CC96', '#EF553B']
    ))

    fig.update_layout(
        title=f'Goals Distribution: Over/Under 2.5<br>Actual: Over {actual_over} / Under {actual_under}',
        template='none',
        height=400
    )

    return apply_theme_settings(fig)


def plot_bookmaker_comparison(df: pd.DataFrame, match_idx: int = 0) -> go.Figure:
    """
    Create a box plot comparing odds from different bookmakers.

    Args:
        df: DataFrame with odds data
        match_idx: Index of specific match to analyze (0 for all matches aggregation)

    Returns:
        Plotly figure
    """
    # Get home win odds from different bookmakers
    bookmakers = {
        'Bet365': 'B365H',
        'Bet&Win': 'BWH',
        'Pinnacle': 'PSH',
        'William Hill': 'WHH'
    }

    odds_data = []

    for name, col in bookmakers.items():
        if col in df.columns:
            valid_odds = df[col].dropna()
            if len(valid_odds) > 0:
                odds_data.append({
                    'Bookmaker': name,
                    'Odds': valid_odds.mean()
                })

    if not odds_data:
        fig = go.Figure()
        fig.update_layout(
            title='Bookmaker Odds Comparison',
            annotations=[dict(text='No odds data available', xref='paper', yref='paper',
                             x=0.5, y=0.5, showarrow=False)]
        )
        return apply_theme_settings(fig)

    plot_df = pd.DataFrame(odds_data)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=plot_df['Bookmaker'],
        y=plot_df['Odds'],
        marker_color=plot_df['Odds'].apply(
            lambda x: '#00CC96' if x < plot_df['Odds'].mean() else '#EF553B'
        ),
        text=plot_df['Odds'].round(2),
        textposition='auto'
    ))

    fig.update_layout(
        title='Average Home Win Odds by Bookmaker',
        xaxis_title='Bookmaker',
        yaxis_title='Average Odds',
        template='none',
        height=400
    )

    return apply_theme_settings(fig)


def plot_fouls_vs_points(df: pd.DataFrame) -> go.Figure:
    """
    Create a scatter plot showing the correlation between fouls and points.

    Args:
        df: DataFrame with match results

    Returns:
        Plotly figure
    """
    from .features import calculate_standings, get_team_stats

    standings = calculate_standings(df)

    teams_data = []

    for team in standings['Team']:
        stats = get_team_stats(df, team)
        standings_row = standings[standings['Team'] == team].iloc[0]

        teams_data.append({
            'Team': team,
            'Avg Fouls/Match': stats.get('avg_fouls', 0),
            'Points': standings_row['Pts']
        })

    plot_df = pd.DataFrame(teams_data)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=plot_df['Avg Fouls/Match'],
        y=plot_df['Points'],
        mode='markers+text',
        text=plot_df['Team'],
        textposition='top center',
        marker=dict(
            size=10,
            color=plot_df['Points'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Points', x=1.15)
        ),
        hovertemplate='<b>%{text}</b><br>Fouls/Match: %{x:.2f}<br>Points: %{y}<extra></extra>'
    ))

    # Add trend line
    if len(plot_df) > 1:
        import numpy as np
        z = np.polyfit(plot_df['Avg Fouls/Match'], plot_df['Points'], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=plot_df['Avg Fouls/Match'],
            y=p(plot_df['Avg Fouls/Match']),
            mode='lines',
            name='Trend Line',
            line=dict(color='gray', dash='dash'),
            hoverinfo='skip'
        ))

    fig.update_layout(
        title='Fouls vs Points Correlation',
        xaxis_title='Average Fouls per Match',
        yaxis_title='Total Points',
        template='none',
        height=500
    )

    return apply_theme_settings(fig)


# Import constants for use in plotting
COL_HY = 'HY'
COL_AY = 'AY'
COL_HR = 'HR'
COL_AR = 'AR'
