"""
Data Loader module for EPL Analytics Dashboard

This module handles loading and initial validation of the EPL dataset.
Key features:
- BOM character handling for UTF-8 files
- Date parsing for DD/MM/YYYY format
- Basic validation and cleaning
"""

import pandas as pd
import streamlit as st
from typing import Optional
import os

from .constants import (
    CSV_ENCODING,
    CSV_DAYFIRST,
    CACHE_TTL_SECONDS,
    ODDS_THRESHOLD_MIN,
    ODDS_THRESHOLD_MAX,
)


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_epl_data(filepath: str) -> pd.DataFrame:
    """
    Load EPL data from CSV with proper handling of BOM character and date format.

    CRITICAL: The dataset has a BOM (Byte Order Mark) character at the start.
    We use encoding='utf-8-sig' to automatically handle this.

    Args:
        filepath: Path to the CSV file

    Returns:
        Cleaned and validated DataFrame

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If required columns are missing
    """
    # Check if file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")

    try:
        # Read CSV with utf-8-sig encoding to handle BOM character
        df = pd.read_csv(
            filepath,
            encoding=CSV_ENCODING,  # 'utf-8-sig' handles BOM automatically
            dayfirst=CSV_DAYFIRST,   # Parse DD/MM/YYYY correctly
        )

        # Clean column names: strip whitespace, remove any remaining BOM artifacts
        df.columns = df.columns.str.strip()

        # Convert Date column to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')

        return df

    except Exception as e:
        raise ValueError(f"Error loading CSV file: {str(e)}")


def validate_dataframe(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """
    Validate that the DataFrame has all required columns and valid data.

    Args:
        df: DataFrame to validate

    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []

    # Check required columns
    required_cols = [
        'Div', 'Date', 'HomeTeam', 'AwayTeam',
        'FTHG', 'FTAG', 'FTR',  # Full-time results
        'HTHG', 'HTAG', 'HTR',  # Half-time results
        'HS', 'AS', 'HST', 'AST',  # Shots
        'HF', 'AF', 'HC', 'AC',  # Fouls and corners
        'HY', 'AY', 'HR', 'AR',  # Cards
        'Referee',
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")

    # Check for impossible values
    if df.empty:
        errors.append("DataFrame is empty")

    # Check for negative values in numeric columns
    numeric_cols = ['FTHG', 'FTAG', 'HTHG', 'HTAG', 'HS', 'AS', 'HST', 'AST']
    for col in numeric_cols:
        if col in df.columns:
            if (df[col] < 0).any():
                errors.append(f"Column {col} contains negative values")

    # Validate odds columns (check if they exist and are in valid range)
    odds_cols = [c for c in df.columns if c.startswith(('B365', 'Avg', 'Max'))]
    if not odds_cols:
        errors.append("No odds columns found in dataset")

    return (len(errors) == 0, errors)


def clean_odds_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean odds columns by handling empty strings and converting to numeric.

    Some Betfair Exchange (BFE*) columns may have empty strings instead of NaN.

    Args:
        df: Raw DataFrame

    Returns:
        DataFrame with cleaned odds columns
    """
    # Identify odds columns (columns with odd-related names)
    odds_patterns = ['B365', 'BW', 'BF', 'BFE', 'PS', 'WH', '1XB', 'Max', 'Avg']
    odds_cols = [col for col in df.columns
                 if any(pattern in col for pattern in odds_patterns)]

    # Convert to numeric, replace empty strings with NaN
    for col in odds_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Clip odds to valid range
    for col in odds_cols:
        if col in df.columns:
            df[col] = df[col].clip(lower=ODDS_THRESHOLD_MIN, upper=ODDS_THRESHOLD_MAX)

    return df


def get_season_matchweeks(df: pd.DataFrame) -> list[int]:
    """
    Extract unique matchweeks from the dataset.

    Note: The dataset doesn't have a 'Matchweek' column,
    so we calculate it based on the date order.

    Args:
        df: DataFrame with Date column

    Returns:
        List of unique matchweeks
    """
    if 'Date' not in df.columns:
        return []

    # Sort by date and assign matchweek
    df_sorted = df.sort_values('Date')

    # Group by date (approximately 10 matches per matchweek)
    unique_dates = df_sorted['Date'].unique()

    # Assign matchweek (each group of dates is a matchweek)
    matchweeks = list(range(1, len(unique_dates) + 1))

    return matchweeks


def get_all_teams(df: pd.DataFrame) -> list[str]:
    """
    Get list of all unique teams in the dataset.

    Args:
        df: DataFrame with HomeTeam and AwayTeam columns

    Returns:
        Sorted list of unique team names
    """
    if 'HomeTeam' not in df.columns or 'AwayTeam' not in df.columns:
        return []

    home_teams = df['HomeTeam'].unique()
    away_teams = df['AwayTeam'].unique()
    all_teams = sorted(set(home_teams) | set(away_teams))

    return all_teams


def get_all_referees(df: pd.DataFrame) -> list[str]:
    """
    Get list of all referees in the dataset.

    Args:
        df: DataFrame with Referee column

    Returns:
        Sorted list of referee names
    """
    if 'Referee' not in df.columns:
        return []

    referees = sorted(df['Referee'].dropna().unique())
    return referees


def display_data_info(df: pd.DataFrame):
    """
    Display information about the loaded dataset in Streamlit.

    Args:
        df: DataFrame to display info for
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Matches", len(df))

    with col2:
        unique_teams = len(get_all_teams(df))
        st.metric("Teams", unique_teams)

    with col3:
        if 'Date' in df.columns:
            date_range = f"{df['Date'].min().strftime('%d %b')} - {df['Date'].max().strftime('%d %b')}"
            st.metric("Date Range", date_range)

    with col4:
        if 'Date' in df.columns:
            matchweeks = len(df['Date'].unique())
            st.metric("Matchweeks", matchweeks)
