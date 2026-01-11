"""
Unit tests for EPL Analytics Dashboard data loader module.

Tests cover:
- CSV loading with BOM handling
- Date parsing
- Data validation
- Odds column cleaning
"""

import pytest
import pandas as pd
import os
import tempfile
from datetime import datetime

from src.data_loader import (
    load_epl_data,
    validate_dataframe,
    clean_odds_columns,
    get_all_teams,
    get_all_referees,
)


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file with sample data including BOM."""
    csv_content = """﻿Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HTR,Referee,HS,AS,HST,AST,HF,AF,HC,AC,HY,AY,HR,AR,B365H,B365D,B365A,AvgH,AvgD,AvgA
E0,16/08/2024,20:00,Man United,Fulham,1,0,H,0,0,D,R Jones,14,10,5,2,12,10,7,8,2,3,0,0,1.6,4.2,5.25,1.57,4.12,5.15
E0,17/08/2024,12:30,Ipswich,Liverpool,0,2,A,0,0,D,T Robinson,7,18,2,5,9,18,2,10,3,1,0,0,8.5,5.5,1.33,8.33,5.39,1.30
E0,17/08/2024,15:00,Arsenal,Wolves,2,0,H,1,0,H,J Gillett,18,9,6,3,17,14,8,2,2,2,0,0,1.18,7.5,13,1.16,7.35,12.74
E0,17/08/2024,15:00,Everton,Brighton,0,3,A,0,1,A,S Hooper,9,10,1,5,8,8,1,5,1,1,1,0,2.63,3.3,2.63,2.58,3.23,2.58
E0,17/08/2024,15:00,Newcastle,Southampton,1,0,H,1,0,H,C Pawson,3,19,1,4,15,16,3,12,2,4,1,0,1.36,5.25,8,1.33,5.15,7.84"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        f.write(csv_content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    data = {
        'Div': ['E0'] * 5,
        'Date': [
            datetime(2024, 8, 16),
            datetime(2024, 8, 17),
            datetime(2024, 8, 24),
            datetime(2024, 8, 31),
            datetime(2024, 9, 14),
        ],
        'HomeTeam': ['Arsenal', 'Liverpool', 'Man City', 'Chelsea', 'Arsenal'],
        'AwayTeam': ['Liverpool', 'Man City', 'Chelsea', 'Arsenal', 'Man City'],
        'FTHG': [2, 1, 3, 0, 1],
        'FTAG': [1, 1, 1, 2, 1],
        'FTR': ['H', 'D', 'H', 'A', 'D'],
        'HTHG': [1, 0, 2, 0, 0],
        'HTAG': [0, 1, 0, 1, 1],
        'HTR': ['H', 'D', 'H', 'A', 'D'],
        'Referee': ['M Oliver', 'P Tierney', 'M Oliver', 'A Taylor', 'C Kavanagh'],
        'HS': [15, 12, 20, 8, 14],
        'AS': [10, 15, 9, 18, 11],
        'HST': [6, 4, 8, 2, 5],
        'AST': [3, 5, 3, 7, 4],
        'HF': [10, 8, 12, 9, 11],
        'AF': [9, 11, 8, 13, 8],
        'HC': [5, 4, 7, 3, 6],
        'AC': [3, 6, 2, 7, 3],
        'HY': [1, 2, 1, 3, 2],
        'AY': [2, 1, 2, 1, 1],
        'HR': [0, 0, 0, 0, 0],
        'AR': [0, 0, 0, 0, 0],
        'B365H': [1.8, 2.5, 1.4, 3.2, 2.1],
        'B365D': [3.5, 3.2, 4.5, 3.4, 3.3],
        'B365A': [4.2, 2.8, 7.5, 2.2, 3.4],
        'AvgH': [1.76, 2.45, 1.37, 3.14, 2.06],
        'AvgD': [3.43, 3.14, 4.41, 3.33, 3.23],
        'AvgA': [4.12, 2.74, 7.35, 2.16, 3.33],
    }

    return pd.DataFrame(data)


class TestLoadEplData:
    """Tests for load_epl_data function."""

    def test_load_file_not_found(self):
        """Test loading a non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_epl_data('nonexistent_file.csv')

    def test_load_csv_with_bom(self, sample_csv_file):
        """Test that BOM character is handled correctly."""
        df = load_epl_data(sample_csv_file)

        # First column should be 'Div', not '﻿Div'
        assert 'Div' in df.columns
        assert '﻿Div' not in df.columns

    def test_load_csv_date_parsing(self, sample_csv_file):
        """Test that dates are parsed correctly."""
        df = load_epl_data(sample_csv_file)

        # Check Date column is datetime
        assert pd.api.types.is_datetime64_any_dtype(df['Date'])

        # Check first date is parsed correctly (16/08/2024)
        first_date = df['Date'].iloc[0]
        assert first_date.year == 2024
        assert first_date.month == 8
        assert first_date.day == 16

    def test_load_csv_returns_dataframe(self, sample_csv_file):
        """Test that loading returns a DataFrame."""
        df = load_epl_data(sample_csv_file)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestValidateDataFrame:
    """Tests for validate_dataframe function."""

    def test_valid_dataframe(self, sample_dataframe):
        """Test validation of a valid DataFrame."""
        is_valid, errors = validate_dataframe(sample_dataframe)

        assert is_valid
        assert len(errors) == 0

    def test_missing_required_columns(self):
        """Test validation with missing columns."""
        incomplete_df = pd.DataFrame({'Col1': [1, 2, 3]})

        is_valid, errors = validate_dataframe(incomplete_df)

        assert not is_valid
        assert len(errors) > 0
        assert any('Missing required columns' in error for error in errors)

    def test_empty_dataframe(self):
        """Test validation of empty DataFrame."""
        empty_df = pd.DataFrame()

        is_valid, errors = validate_dataframe(empty_df)

        assert not is_valid
        assert any('empty' in error.lower() for error in errors)

    def test_negative_values(self, sample_dataframe):
        """Test validation with negative values in numeric columns."""
        sample_dataframe.loc[0, 'FTHG'] = -1

        is_valid, errors = validate_dataframe(sample_dataframe)

        assert not is_valid
        assert any('negative' in error.lower() for error in errors)


class TestCleanOddsColumns:
    """Tests for clean_odds_columns function."""

    def test_clean_odds_converts_to_numeric(self, sample_dataframe):
        """Test that odds columns are converted to numeric."""
        # Introduce some string values
        sample_dataframe.loc[0, 'B365H'] = '1.80'

        cleaned_df = clean_odds_columns(sample_dataframe)

        assert pd.api.types.is_numeric_dtype(cleaned_df['B365H'])

    def test_clean_odds_clips_values(self, sample_dataframe):
        """Test that odds are clipped to valid range."""
        # Add an out-of-range value
        sample_dataframe.loc[0, 'B365H'] = 150.0

        cleaned_df = clean_odds_columns(sample_dataframe)

        # Should be clipped to max of 100
        assert cleaned_df.loc[0, 'B365H'] <= 100.0

    def test_clean_odds_handles_empty_strings(self, sample_dataframe):
        """Test that empty strings in odds columns are handled."""
        # Simulate Betfair Exchange empty odds
        sample_dataframe['BFEH'] = ['1.80', '', '1.40', '3.20', '2.10']

        cleaned_df = clean_odds_columns(sample_dataframe)

        # Empty strings should become NaN
        assert pd.isna(cleaned_df.loc[1, 'BFEH'])


class TestGetAllTeams:
    """Tests for get_all_teams function."""

    def test_get_all_teams_returns_list(self, sample_dataframe):
        """Test that function returns a list."""
        teams = get_all_teams(sample_dataframe)

        assert isinstance(teams, list)

    def test_get_all_teams_content(self, sample_dataframe):
        """Test that all unique teams are returned."""
        teams = get_all_teams(sample_dataframe)

        expected_teams = ['Arsenal', 'Chelsea', 'Liverpool', 'Man City']
        for team in expected_teams:
            assert team in teams

    def test_get_all_teams_sorted(self, sample_dataframe):
        """Test that teams are sorted alphabetically."""
        teams = get_all_teams(sample_dataframe)

        assert teams == sorted(teams)


class TestGetAllReferees:
    """Tests for get_all_referees function."""

    def test_get_all_referees_returns_list(self, sample_dataframe):
        """Test that function returns a list."""
        referees = get_all_referees(sample_dataframe)

        assert isinstance(referees, list)

    def test_get_all_referees_content(self, sample_dataframe):
        """Test that all unique referees are returned."""
        referees = get_all_referees(sample_dataframe)

        assert 'M Oliver' in referees
        assert 'A Taylor' in referees

    def test_get_all_referees_sorted(self, sample_dataframe):
        """Test that referees are sorted alphabetically."""
        referees = get_all_referees(sample_dataframe)

        assert referees == sorted(referees)

    def test_get_all_referees_handles_nan(self):
        """Test that NaN referee values are handled."""
        df = pd.DataFrame({
            'Referee': ['M Oliver', None, 'A Taylor', None]
        })

        referees = get_all_referees(df)

        # Should not include None
        assert None not in referees
        assert len(referees) == 2


class TestEdgeCases:
    """Tests for edge cases in data loading."""

    def test_malformed_csv(self):
        """Test handling of malformed CSV data."""
        csv_content = """﻿Div,Date
E0,16/08/2024,extra_column
E0,17/08/2024"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            # Should still load but may have issues
            df = load_epl_data(temp_path)
            assert len(df) > 0
        finally:
            os.unlink(temp_path)

    def test_csv_with_missing_odds(self):
        """Test CSV where some matches have missing odds."""
        csv_content = """﻿Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,B365H,B365D,B365A
E0,16/08/2024,Arsenal,Liverpool,2,1,H,1.8,3.5,4.2
E0,17/08/2024,Man City,Chelsea,1,0,D,,,,"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name

        try:
            df = load_epl_data(temp_path)
            cleaned_df = clean_odds_columns(df)

            # Missing odds should be NaN
            assert pd.isna(cleaned_df.loc[1, 'B365H'])
        finally:
            os.unlink(temp_path)
