"""
Analytics service for processing message data with pandas
"""

from typing import Dict, List, Tuple

import pandas as pd


def create_dataframe(messages_data: List[Dict]) -> pd.DataFrame:
    """
    Create a pandas DataFrame from message data

    Args:
        messages_data: List of message data dictionaries

    Returns:
        pandas DataFrame
    """
    return pd.DataFrame(messages_data)


def filter_user_messages_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter out bot messages from DataFrame

    Args:
        df: DataFrame with message data

    Returns:
        Filtered DataFrame with only user messages
    """
    return df[~df["is_bot"]]


def count_messages_by_user(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count messages by user and return sorted results

    Args:
        df: DataFrame with message data

    Returns:
        DataFrame with user_id, user_name, and count columns, sorted by count
    """
    user_counts = df.groupby(["user_id", "user_name"]).size().reset_index(name="count")
    return user_counts.sort_values("count", ascending=False)


def get_user_message_count(df: pd.DataFrame, user_id: int) -> int:
    """
    Get message count for a specific user

    Args:
        df: DataFrame with message data
        user_id: Discord user ID

    Returns:
        Count of messages for the user
    """
    user_df = df[df["user_id"] == user_id]
    return len(user_df)


def get_user_percentage(df: pd.DataFrame, user_id: int) -> float:
    """
    Get percentage of total messages for a specific user

    Args:
        df: DataFrame with message data
        user_id: Discord user ID

    Returns:
        Percentage of total messages
    """
    total_messages = len(df)
    if total_messages == 0:
        return 0.0

    user_count = get_user_message_count(df, user_id)
    return (user_count / total_messages) * 100


def get_message_stats(df: pd.DataFrame) -> Dict:
    """
    Get overall message statistics

    Args:
        df: DataFrame with message data

    Returns:
        Dictionary with total_messages and unique_users
    """
    return {"total_messages": len(df), "unique_users": df["user_id"].nunique()}


def get_channel_stats(df: pd.DataFrame) -> Dict:
    """
    Get channel-related statistics

    Args:
        df: DataFrame with message data (must include 'channel_name')

    Returns:
        Dictionary with stats including channels_checked
    """
    stats = get_message_stats(df)
    if "channel_name" in df.columns:
        stats["channels_checked"] = df["channel_name"].nunique()
    return stats


def format_leaderboard(
    user_counts: pd.DataFrame, max_entries: int = None
) -> List[Tuple[int, str, int]]:
    """
    Format leaderboard data for display

    Args:
        user_counts: DataFrame with user counts
        max_entries: Maximum number of entries to return

    Returns:
        List of tuples (rank, user_name, count)
    """
    if max_entries:
        user_counts = user_counts.head(max_entries)

    leaderboard = []
    for idx, row in user_counts.iterrows():
        rank = len(leaderboard) + 1
        leaderboard.append((rank, row["user_name"], row["count"]))

    return leaderboard
