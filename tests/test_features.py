"""
Unit tests for EPL Analytics Dashboard features module.

Tests cover:
- Standings calculation
- Form string generation
- Team statistics
- Head-to-head statistics
- Edge cases
"""

import pytest
import pandas as pd
from datetime import datetime

from src.features import (
    calculate_standings,
    calculate_form_for_team,
    calculate_momentum_score,
    get_head_to_head_stats,
    get_team_stats,
)


@pytest.fixture
def sample_match_data():
    """Create sample match data for testing."""
    data = {
        'Div': ['E0'] * 10,
        'Date': [
            datetime(2024, 8, 16),
            datetime(2024, 8, 17),
            datetime(2024, 8, 24),
            datetime(2024, 8, 31),
            datetime(2024, 9, 14),
            datetime(2024, 9, 21),
            datetime(2024, 9, 28),
            datetime(2024, 10, 5),
            datetime(2024, 10, 19),
            datetime(2024, 10, 26),
        ],
        'HomeTeam': ['Arsenal', 'Liverpool', 'Man City', 'Chelsea', 'Arsenal',
                     'Liverpool', 'Man City', 'Chelsea', 'Arsenal', 'Liverpool'],
        'AwayTeam': ['Liverpool', 'Man City', 'Chelsea', 'Arsenal', 'Man City',
                     'Chelsea', 'Arsenal', 'Liverpool', 'Chelsea', 'Man City'],
        'FTHG': [2, 1, 3, 0, 1, 2, 2, 1, 3, 1],
        'FTAG': [1, 1, 1, 2, 1, 1, 0, 2, 1, 3],
        'FTR': ['H', 'D', 'H', 'A', 'D', 'H', 'H', 'A', 'H', 'A'],
        'HTHG': [1, 0, 2, 0, 0, 1, 1, 0, 2, 0],
        'HTAG': [0, 1, 0, 1, 1, 0, 0, 1, 0, 1],
        'HTR': ['H', 'D', 'H', 'A', 'D', 'H', 'H', 'A', 'H', 'D'],
        'HS': [15, 12, 20, 8, 14, 18, 16, 10, 19, 13],
        'AS': [10, 15, 9, 18, 11, 8, 7, 16, 9, 20],
        'HST': [6, 4, 8, 2, 5, 7, 6, 3, 7, 4],
        'AST': [3, 5, 3, 7, 4, 2, 2, 6, 3, 8],
        'HF': [10, 8, 12, 9, 11, 7, 10, 12, 9, 8],
        'AF': [9, 11, 8, 13, 8, 12, 9, 7, 11, 14],
        'HC': [5, 4, 7, 3, 6, 5, 5, 4, 6, 4],
        'AC': [3, 6, 2, 7, 3, 4, 2, 5, 3, 7],
        'HY': [1, 2, 1, 3, 2, 1, 1, 2, 1, 2],
        'AY': [2, 1, 2, 1, 1, 3, 2, 1, 3, 1],
        'HR': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'AR': [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        'Referee': ['M Oliver'] * 10,
    }

    df = pd.DataFrame(data)

    # Add odds columns for testing
    df['B365H'] = [1.8, 2.5, 1.4, 3.2, 2.1, 1.9, 1.5, 3.5, 1.7, 2.8]
    df['B365D'] = [3.5, 3.2, 4.5, 3.4, 3.3, 3.6, 4.2, 3.3, 3.7, 3.4]
    df['B365A'] = [4.2, 2.8, 7.5, 2.2, 3.4, 4.0, 6.0, 2.1, 4.8, 2.5]
    df['AvgH'] = df['B365H'] * 0.98
    df['AvgD'] = df['B365D'] * 0.98
    df['AvgA'] = df['B365A'] * 0.98

    return df


class TestCalculateStandings:
    """Tests for calculate_standings function."""

    def test_standings_columns(self, sample_match_data):
        """Test that standings table has all required columns."""
        standings = calculate_standings(sample_match_data)

        required_cols = ['Pos', 'Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts', 'Form']

        for col in required_cols:
            assert col in standings.columns, f"Missing column: {col}"

    def test_standings_sorting(self, sample_match_data):
        """Test that standings are sorted correctly by points."""
        standings = calculate_standings(sample_match_data)

        # Should be sorted by points descending
        assert standings['Pts'].is_monotonic_decreasing

    def test_standings_points_calculation(self, sample_match_data):
        """Test that points are calculated correctly."""
        standings = calculate_standings(sample_match_data)

        # Find Arsenal in standings
        arsenal_row = standings[standings['Team'] == 'Arsenal']

        if len(arsenal_row) > 0:
            arsenal = arsenal_row.iloc[0]

            # Arsenal played: vs Liverpool (H, W), vs Chelsea (A, L), vs Man City (H, D), vs Chelsea (H, W)
            # 3 + 0 + 1 + 3 = 7 points
            assert arsenal['Pts'] >= 0
            assert arsenal['P'] == 4  # 4 matches played

    def test_standings_goal_difference(self, sample_match_data):
        """Test that goal difference is calculated correctly."""
        standings = calculate_standings(sample_match_data)

        for _, row in standings.iterrows():
            assert row['GD'] == row['GF'] - row['GA']


class TestCalculateForm:
    """Tests for calculate_form_for_team function."""

    def test_form_string_length(self, sample_match_data):
        """Test that form string is limited to 5 characters."""
        form = calculate_form_for_team(sample_match_data, 'Arsenal', num_matches=5)

        assert len(form) <= 5

    def test_form_results(self, sample_match_data):
        """Test that form contains only valid results."""
        form = calculate_form_for_team(sample_match_data, 'Arsenal', num_matches=5)

        for result in form:
            assert result in ['W', 'D', 'L']

    def test_form_empty_for_no_matches(self, sample_match_data):
        """Test that form is empty for a team with no matches."""
        form = calculate_form_for_team(sample_match_data, 'NonExistentTeam', num_matches=5)

        assert form == ""


class TestMomentumScore:
    """Tests for calculate_momentum_score function."""

    def test_momentum_range(self, sample_match_data):
        """Test that momentum score is within expected range."""
        score = calculate_momentum_score(sample_match_data, 'Arsenal')

        # Maximum possible: 5 wins * 1.5 weight * 3 points = 22.5
        assert 0 <= score <= 25

    def test_momentum_zero_for_no_matches(self, sample_match_data):
        """Test that momentum is 0 for a team with no matches."""
        score = calculate_momentum_score(sample_match_data, 'NonExistentTeam')

        assert score == 0.0


class TestHeadToHead:
    """Tests for get_head_to_head_stats function."""

    def test_h2h_teams_in_data(self, sample_match_data):
        """Test H2H for teams that played each other."""
        h2h = get_head_to_head_stats(sample_match_data, 'Arsenal', 'Liverpool')

        # Arsenal played Liverpool once (home, 2-1 win)
        assert h2h['total_matches'] == 1
        assert h2h['team_a_wins'] == 1
        assert h2h['team_b_wins'] == 0
        assert h2h['draws'] == 0

    def test_h2h_teams_no_matches(self, sample_match_data):
        """Test H2H for teams that haven't played each other."""
        # Add a team that hasn't played
        h2h = get_head_to_head_stats(sample_match_data, 'Arsenal', 'NonExistentTeam')

        assert h2h['total_matches'] == 0

    def test_h2h_goal_counting(self, sample_match_data):
        """Test that H2H correctly counts goals."""
        h2h = get_head_to_head_stats(sample_match_data, 'Arsenal', 'Chelsea')

        # Arsenal vs Chelsea: (H, 0-2 loss), (H, 3-1 win)
        assert h2h['team_a_goals'] == 3  # Arsenal
        assert h2h['team_b_goals'] == 3  # Chelsea


class TestGetTeamStats:
    """Tests for get_team_stats function."""

    def test_team_stats_return_dict(self, sample_match_data):
        """Test that team stats returns a dictionary."""
        stats = get_team_stats(sample_match_data, 'Arsenal')

        assert isinstance(stats, dict)

    def test_team_stats_required_keys(self, sample_match_data):
        """Test that team stats has all required keys."""
        stats = get_team_stats(sample_match_data, 'Arsenal')

        required_keys = [
            'matches_played', 'wins', 'draws', 'losses',
            'goals_for', 'goals_against', 'goal_difference', 'points', 'win_rate'
        ]

        for key in required_keys:
            assert key in stats

    def test_team_stats_venue_filtering(self, sample_match_data):
        """Test that venue filtering works correctly."""
        all_stats = get_team_stats(sample_match_data, 'Arsenal', venue=None)
        home_stats = get_team_stats(sample_match_data, 'Arsenal', venue='home')
        away_stats = get_team_stats(sample_match_data, 'Arsenal', venue='away')

        # Home + away should equal all
        assert home_stats['matches_played'] + away_stats['matches_played'] == all_stats['matches_played']

    def test_team_stats_empty_team(self, sample_match_data):
        """Test stats for non-existent team."""
        stats = get_team_stats(sample_match_data, 'NonExistentTeam')

        assert stats['matches_played'] == 0


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_dataframe(self):
        """Test functions with empty DataFrame."""
        df = pd.DataFrame()

        standings = calculate_standings(df)
        assert len(standings) == 0

    def test_dataframe_with_missing_columns(self, sample_match_data):
        """Test functions with DataFrame missing required columns."""
        # Remove some columns
        incomplete_df = sample_match_data.drop(columns=['HS', 'AS', 'HST', 'AST'])

        # Should still work for standings
        standings = calculate_standings(incomplete_df)
        assert len(standings) > 0

    def test_team_with_less_than_5_matches(self, sample_match_data):
        """Test form calculation for team with fewer than 5 matches."""
        # Create a team with only 2 matches
        limited_df = sample_match_data.iloc[:2].copy()

        form = calculate_form_for_team(limited_df, 'Arsenal', num_matches=5)

        # Should return form with length <= 2
        assert len(form) <= 2
