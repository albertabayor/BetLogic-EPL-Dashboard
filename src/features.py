"""
Feature Engineering module for EPL Analytics Dashboard

This module contains all functions for calculating derived metrics
from the raw match data.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple

from .constants import (
    COL_DATE,
    COL_HOME_TEAM,
    COL_AWAY_TEAM,
    COL_FTHG,
    COL_FTAG,
    COL_FTR,
    COL_HTHG,
    COL_HTAG,
    COL_HS,
    COL_AS,
    COL_HST,
    COL_AST,
    COL_HF,
    COL_AF,
    COL_HC,
    COL_AC,
    COL_HY,
    COL_AY,
    COL_HR,
    COL_AR,
    RESULT_HOME_WIN,
    RESULT_DRAW,
    RESULT_AWAY_WIN,
    POINTS_WIN,
    POINTS_DRAW,
    POINTS_LOSS,
    MIN_MATCHES_FOR_FORM,
)


def calculate_standings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate league standings table from match data.

    Args:
        df: DataFrame with match results

    Returns:
        DataFrame with standings: Position, Team, P, W, D, L, GF, GA, GD, Pts, Form
    """
    # Get all unique teams
    home_teams = df[COL_HOME_TEAM].unique()
    away_teams = df[COL_AWAY_TEAM].unique()
    all_teams = sorted(set(home_teams) | set(away_teams))

    standings_data = []

    for team in all_teams:
        # Get all matches for this team (both home and away)
        home_matches = df[df[COL_HOME_TEAM] == team]
        away_matches = df[df[COL_AWAY_TEAM] == team]

        # Calculate stats
        played = len(home_matches) + len(away_matches)

        # Home stats
        home_wins = len(home_matches[home_matches[COL_FTR] == RESULT_HOME_WIN])
        home_draws = len(home_matches[home_matches[COL_FTR] == RESULT_DRAW])
        home_losses = len(home_matches[home_matches[COL_FTR] == RESULT_AWAY_WIN])
        home_goals_for = home_matches[COL_FTHG].sum()
        home_goals_against = home_matches[COL_FTAG].sum()

        # Away stats
        away_wins = len(away_matches[away_matches[COL_FTR] == RESULT_AWAY_WIN])
        away_draws = len(away_matches[away_matches[COL_FTR] == RESULT_DRAW])
        away_losses = len(away_matches[away_matches[COL_FTR] == RESULT_HOME_WIN])
        away_goals_for = away_matches[COL_FTAG].sum()
        away_goals_against = away_matches[COL_FTHG].sum()

        # Total stats
        wins = home_wins + away_wins
        draws = home_draws + away_draws
        losses = home_losses + away_losses
        goals_for = int(home_goals_for + away_goals_for)
        goals_against = int(home_goals_against + away_goals_against)
        goal_diff = goals_for - goals_against
        points = wins * POINTS_WIN + draws * POINTS_DRAW

        # Calculate form string
        form = calculate_form_for_team(df, team)

        standings_data.append({
            'Team': team,
            'P': played,
            'W': wins,
            'D': draws,
            'L': losses,
            'GF': goals_for,
            'GA': goals_against,
            'GD': goal_diff,
            'Pts': points,
            'Form': form,
        })

    standings_df = pd.DataFrame(standings_data)

    # Sort by points, then goal difference, then goals for
    standings_df = standings_df.sort_values(
        by=['Pts', 'GD', 'GF'],
        ascending=[False, False, False]
    ).reset_index(drop=True)

    # Add position
    standings_df.insert(0, 'Pos', range(1, len(standings_df) + 1))

    return standings_df


def calculate_form_for_team(df: pd.DataFrame, team: str, num_matches: int = 5) -> str:
    """
    Calculate form string for a team based on their last N matches.

    Args:
        df: DataFrame with match results
        team: Team name
        num_matches: Number of recent matches to consider

    Returns:
        Form string like "WWDLW" or partial if less matches available
    """
    # Get all matches for this team, sorted by date
    home_matches = df[df[COL_HOME_TEAM] == team].copy()
    away_matches = df[df[COL_AWAY_TEAM] == team].copy()

    # Add result column for both home and away
    home_matches['TeamResult'] = home_matches[COL_FTR].apply(
        lambda x: 'W' if x == RESULT_HOME_WIN else ('D' if x == RESULT_DRAW else 'L')
    )
    away_matches['TeamResult'] = away_matches[COL_FTR].apply(
        lambda x: 'W' if x == RESULT_AWAY_WIN else ('D' if x == RESULT_DRAW else 'L')
    )

    # Combine and sort by date
    all_matches = pd.concat([
        home_matches[[COL_DATE, 'TeamResult']],
        away_matches[[COL_DATE, 'TeamResult']]
    ]).sort_values(COL_DATE, ascending=False)

    # Get last N results
    recent_results = all_matches.head(num_matches)['TeamResult'].tolist()

    return ''.join(recent_results)


def calculate_momentum_score(df: pd.DataFrame, team: str, num_matches: int = 5) -> float:
    """
    Calculate momentum score based on weighted recent results.

    Most recent match has highest weight.

    Args:
        df: DataFrame with match results
        team: Team name
        num_matches: Number of matches to consider

    Returns:
        Momentum score between 0 and 15 (max if all wins)
    """
    # Get form results
    form = calculate_form_for_team(df, team, num_matches)

    if not form:
        return 0.0

    # Weight decreases with age (most recent = highest weight)
    weights = [1.5, 1.3, 1.1, 1.0, 0.8][:len(form)]

    score = 0.0
    for i, result in enumerate(form):
        points = POINTS_WIN if result == 'W' else (POINTS_DRAW if result == 'D' else POINTS_LOSS)
        score += points * weights[i]

    return round(score, 2)


def get_head_to_head_stats(df: pd.DataFrame, team_a: str, team_b: str) -> dict:
    """
    Calculate head-to-head statistics between two teams.

    Args:
        df: DataFrame with match results
        team_a: First team name
        team_b: Second team name

    Returns:
        Dictionary with H2H stats
    """
    # Filter matches between these two teams
    h2h_matches = df[
        ((df[COL_HOME_TEAM] == team_a) & (df[COL_AWAY_TEAM] == team_b)) |
        ((df[COL_HOME_TEAM] == team_b) & (df[COL_AWAY_TEAM] == team_a))
    ].copy()

    if len(h2h_matches) == 0:
        return {
            'total_matches': 0,
            'team_a_wins': 0,
            'team_b_wins': 0,
            'draws': 0,
            'team_a_goals': 0,
            'team_b_goals': 0,
            'matches': h2h_matches,
        }

    # Calculate results
    team_a_wins = 0
    team_b_wins = 0
    draws = 0
    team_a_goals = 0
    team_b_goals = 0

    for _, match in h2h_matches.iterrows():
        is_a_home = match[COL_HOME_TEAM] == team_a

        if match[COL_FTR] == RESULT_HOME_WIN:
            if is_a_home:
                team_a_wins += 1
            else:
                team_b_wins += 1
        elif match[COL_FTR] == RESULT_AWAY_WIN:
            if is_a_home:
                team_b_wins += 1
            else:
                team_a_wins += 1
        else:
            draws += 1

        if is_a_home:
            team_a_goals += match[COL_FTHG]
            team_b_goals += match[COL_FTAG]
        else:
            team_a_goals += match[COL_FTAG]
            team_b_goals += match[COL_FTHG]

    return {
        'total_matches': len(h2h_matches),
        'team_a_wins': team_a_wins,
        'team_b_wins': team_b_wins,
        'draws': draws,
        'team_a_goals': team_a_goals,
        'team_b_goals': team_b_goals,
        'matches': h2h_matches,
    }


def get_team_stats(df: pd.DataFrame, team: str, venue: Optional[str] = None) -> dict:
    """
    Get detailed statistics for a specific team.

    Args:
        df: DataFrame with match data
        team: Team name
        venue: 'home', 'away', or None for all matches

    Returns:
        Dictionary with team statistics
    """
    if venue == 'home':
        matches = df[df[COL_HOME_TEAM] == team].copy()
        goals_for_col = COL_FTHG
        goals_against_col = COL_FTAG
        shots_col = COL_HS
        shots_target_col = COL_HST
        fouls_col = COL_HF
        corners_col = COL_HC
        yellows_col = COL_HY
        reds_col = COL_HR
    elif venue == 'away':
        matches = df[df[COL_AWAY_TEAM] == team].copy()
        goals_for_col = COL_FTAG
        goals_against_col = COL_FTHG
        shots_col = COL_AS
        shots_target_col = COL_AST
        fouls_col = COL_AF
        corners_col = COL_AC
        yellows_col = COL_AY
        reds_col = COL_AR
    else:
        # Get all matches
        home = df[df[COL_HOME_TEAM] == team].copy()
        away = df[df[COL_AWAY_TEAM] == team].copy()

        home_stats = get_team_stats(df, team, 'home')
        away_stats = get_team_stats(df, team, 'away')

        total_matches = len(home) + len(away)

        if total_matches == 0:
            return {
                'matches_played': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_for': 0,
                'goals_against': 0,
                'goal_difference': 0,
                'points': 0,
                'win_rate': 0,
                'clean_sheets': 0,
                'avg_goals_for': 0,
                'avg_goals_against': 0,
                'avg_shots': 0,
                'shot_accuracy': 0,
                'avg_fouls': 0,
                'avg_corners': 0,
                'total_yellows': 0,
                'total_reds': 0,
            }

        return {
            'matches_played': total_matches,
            'wins': home_stats['wins'] + away_stats['wins'],
            'draws': home_stats['draws'] + away_stats['draws'],
            'losses': home_stats['losses'] + away_stats['losses'],
            'goals_for': home_stats['goals_for'] + away_stats['goals_for'],
            'goals_against': home_stats['goals_against'] + away_stats['goals_against'],
            'goal_difference': (home_stats['goal_difference'] + away_stats['goal_difference']),
            'points': home_stats['points'] + away_stats['points'],
            'win_rate': round((home_stats['wins'] + away_stats['wins']) / total_matches * 100, 1),
            'clean_sheets': home_stats['clean_sheets'] + away_stats['clean_sheets'],
            'avg_goals_for': round((home_stats['goals_for'] + away_stats['goals_for']) / total_matches, 2),
            'avg_goals_against': round((home_stats['goals_against'] + away_stats['goals_against']) / total_matches, 2),
            'avg_shots': round((home_stats['total_shots'] + away_stats['total_shots']) / total_matches, 2),
            'shot_accuracy': round((home_stats['shots_on_target'] + away_stats['shots_on_target']) /
                                   (home_stats['total_shots'] + away_stats['total_shots']) * 100, 1) if (home_stats['total_shots'] + away_stats['total_shots']) > 0 else 0,
            'avg_fouls': round((home_stats['total_fouls'] + away_stats['total_fouls']) / total_matches, 2),
            'avg_corners': round((home_stats['total_corners'] + away_stats['total_corners']) / total_matches, 2),
            'total_yellows': home_stats['total_yellows'] + away_stats['total_yellows'],
            'total_reds': home_stats['total_reds'] + away_stats['total_reds'],
            'total_shots': home_stats['total_shots'] + away_stats['total_shots'],
            'shots_on_target': home_stats['shots_on_target'] + away_stats['shots_on_target'],
            'total_fouls': home_stats['total_fouls'] + away_stats['total_fouls'],
            'total_corners': home_stats['total_corners'] + away_stats['total_corners'],
        }

    matches = matches.copy()

    if len(matches) == 0:
        return {
            'matches_played': 0,
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_for': 0,
            'goals_against': 0,
            'goal_difference': 0,
            'points': 0,
            'win_rate': 0,
            'clean_sheets': 0,
        }

    # Calculate results
    if venue == 'home':
        wins = len(matches[matches[COL_FTR] == RESULT_HOME_WIN])
        draws = len(matches[matches[COL_FTR] == RESULT_DRAW])
        losses = len(matches[matches[COL_FTR] == RESULT_AWAY_WIN])
    else:  # away
        wins = len(matches[matches[COL_FTR] == RESULT_AWAY_WIN])
        draws = len(matches[matches[COL_FTR] == RESULT_DRAW])
        losses = len(matches[matches[COL_FTR] == RESULT_HOME_WIN])

    goals_for = matches[goals_for_col].sum()
    goals_against = matches[goals_against_col].sum()
    clean_sheets = len(matches[matches[goals_against_col] == 0])

    total_shots = matches[shots_col].sum() if shots_col in matches.columns else 0
    shots_on_target = matches[shots_target_col].sum() if shots_target_col in matches.columns else 0
    total_fouls = matches[fouls_col].sum() if fouls_col in matches.columns else 0
    total_corners = matches[corners_col].sum() if corners_col in matches.columns else 0
    total_yellows = matches[yellows_col].sum() if yellows_col in matches.columns else 0
    total_reds = matches[reds_col].sum() if reds_col in matches.columns else 0

    return {
        'matches_played': len(matches),
        'wins': wins,
        'draws': draws,
        'losses': losses,
        'goals_for': int(goals_for),
        'goals_against': int(goals_against),
        'goal_difference': int(goals_for - goals_against),
        'points': wins * POINTS_WIN + draws * POINTS_DRAW,
        'win_rate': round(wins / len(matches) * 100, 1),
        'clean_sheets': clean_sheets,
        'avg_goals_for': round(goals_for / len(matches), 2),
        'avg_goals_against': round(goals_against / len(matches), 2),
        'avg_shots': round(total_shots / len(matches), 2) if len(matches) > 0 else 0,
        'shot_accuracy': round(shots_on_target / total_shots * 100, 1) if total_shots > 0 else 0,
        'avg_fouls': round(total_fouls / len(matches), 2) if len(matches) > 0 else 0,
        'avg_corners': round(total_corners / len(matches), 2) if len(matches) > 0 else 0,
        'total_yellows': int(total_yellows),
        'total_reds': int(total_reds),
        'total_shots': int(total_shots),
        'shots_on_target': int(shots_on_target),
        'total_fouls': int(total_fouls),
        'total_corners': int(total_corners),
    }


def calculate_win_probability(
    df: pd.DataFrame,
    team_a: str,
    team_b: str,
    home_team: str
) -> dict:
    """
    Calculate win probability using a weighted formula.

    Weights:
    - Recent form (40%)
    - H2H history (30%)
    - Home advantage (15%)
    - Current standings (15%)

    Args:
        df: DataFrame with match results
        team_a: First team
        team_b: Second team
        home_team: Which team is playing at home

    Returns:
        Dictionary with probabilities for home_win, draw, away_win
    """
    # Get standings
    standings = calculate_standings(df)

    # Get team positions
    team_a_pos = standings[standings['Team'] == team_a]['Pos'].values[0] if len(standings[standings['Team'] == team_a]) > 0 else 10
    team_b_pos = standings[standings['Team'] == team_b]['Pos'].values[0] if len(standings[standings['Team'] == team_b]) > 0 else 10

    # Momentum scores (40% weight)
    momentum_a = calculate_momentum_score(df, team_a)
    momentum_b = calculate_momentum_score(df, team_b)
    total_momentum = momentum_a + momentum_b
    momentum_prob_a = momentum_a / total_momentum if total_momentum > 0 else 0.5
    momentum_prob_b = momentum_b / total_momentum if total_momentum > 0 else 0.5

    # H2H history (30% weight)
    h2h = get_head_to_head_stats(df, team_a, team_b)
    if h2h['total_matches'] > 0:
        h2h_prob_a = (h2h['team_a_wins'] + h2h['draws'] * 0.5) / h2h['total_matches']
        h2h_prob_b = (h2h['team_b_wins'] + h2h['draws'] * 0.5) / h2h['total_matches']
    else:
        h2h_prob_a = 0.5
        h2h_prob_b = 0.5

    # Home advantage (15% weight)
    if home_team == team_a:
        home_adv_a = 0.6
        home_adv_b = 0.4
    elif home_team == team_b:
        home_adv_a = 0.4
        home_adv_b = 0.6
    else:
        home_adv_a = 0.5
        home_adv_b = 0.5

    # Current standings (15% weight) - inverse (lower position = better)
    standing_prob_a = 1 / (1 + team_a_pos * 0.1)
    standing_prob_b = 1 / (1 + team_b_pos * 0.1)

    # Combine with weights
    prob_a = (
        momentum_prob_a * 0.40 +
        h2h_prob_a * 0.30 +
        home_adv_a * 0.15 +
        standing_prob_a * 0.15
    )
    prob_b = (
        momentum_prob_b * 0.40 +
        h2h_prob_b * 0.30 +
        home_adv_b * 0.15 +
        standing_prob_b * 0.15
    )

    # Normalize
    total = prob_a + prob_b
    prob_a = prob_a / total
    prob_b = prob_b / total

    # Draw probability (typically 25-30% in football)
    draw_prob = 0.25
    prob_a = prob_a * (1 - draw_prob)
    prob_b = prob_b * (1 - draw_prob)

    # Determine which is home/away for return
    if home_team == team_a:
        home_win = prob_a
        away_win = prob_b
    elif home_team == team_b:
        home_win = prob_b
        away_win = prob_a
    else:
        # Neutral venue (unlikely in EPL)
        home_win = prob_a
        away_win = prob_b

    return {
        'home_win': round(home_win * 100, 1),
        'draw': round(draw_prob * 100, 1),
        'away_win': round(away_win * 100, 1),
        'confidence': 'High' if h2h['total_matches'] >= 3 else ('Medium' if h2h['total_matches'] >= 1 else 'Low'),
    }


def get_referee_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate statistics for each referee.

    Args:
        df: DataFrame with match data

    Returns:
        DataFrame with referee statistics
    """
    refs = df['Referee'].dropna().unique()

    ref_stats = []

    for ref in refs:
        ref_matches = df[df['Referee'] == ref]

        total_yellows = ref_matches[[COL_HY, COL_AY]].sum().sum() if all(c in df.columns for c in [COL_HY, COL_AY]) else 0
        total_reds = ref_matches[[COL_HR, COL_AR]].sum().sum() if all(c in df.columns for c in [COL_HR, COL_AR]) else 0
        total_fouls = ref_matches[[COL_HF, COL_AF]].sum().sum() if all(c in df.columns for c in [COL_HF, COL_AF]) else 0

        ref_stats.append({
            'Referee': ref,
            'Matches': len(ref_matches),
            'Yellow Cards': int(total_yellows),
            'Red Cards': int(total_reds),
            'Cards/Match': round((total_yellows + total_reds) / len(ref_matches), 2) if len(ref_matches) > 0 else 0,
            'Fouls/Match': round(total_fouls / len(ref_matches), 2) if len(ref_matches) > 0 else 0,
        })

    return pd.DataFrame(ref_stats).sort_values('Matches', ascending=False)
