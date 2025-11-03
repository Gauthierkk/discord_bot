"""
Discord embed builder utilities
"""

from datetime import datetime
from typing import Dict, List, Tuple

import discord


def create_first_message_embed(
    message: discord.Message, total_messages: int
) -> discord.Embed:
    """Create embed for the first message in a channel"""
    embed = discord.Embed(
        description=message.content or "*No text content*",
        color=discord.Color.blue(),
        timestamp=message.created_at,
    )
    embed.set_author(
        name=message.author.display_name, icon_url=message.author.display_avatar.url
    )
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Total Messages", value=str(total_messages), inline=True)
    embed.set_footer(text=f"Message ID: {message.id}")

    return embed


def create_user_count_embed(
    user: discord.User, count: int, percentage: float = None
) -> discord.Embed:
    """Create embed for a specific user's message count"""
    embed = discord.Embed(
        title=f"Message Count for {user.display_name}", color=discord.Color.blue()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="Messages", value=f"{count:,}", inline=True)

    if percentage is not None:
        embed.add_field(name="Percentage", value=f"{percentage:.1f}%", inline=True)

    return embed


def create_leaderboard_embed(
    leaderboard: List[Tuple[int, str, int]],
    title: str,
    total_messages: int,
    unique_users: int,
    color: discord.Color = discord.Color.gold(),
) -> discord.Embed:
    """Create embed for message leaderboard"""
    description_lines = []

    for rank, user_name, count in leaderboard:
        medal = ""
        if rank == 1:
            medal = "[1st] "
        elif rank == 2:
            medal = "[2nd] "
        elif rank == 3:
            medal = "[3rd] "

        description_lines.append(
            f"{medal}**{rank}.** {user_name} - **{count:,}** messages"
        )

    # Discord has a 4096 character limit for embed descriptions
    description = "\n".join(description_lines)
    if len(description) > 4000:
        description = "\n".join(description_lines[:50]) + "\n\n*... and more*"

    embed = discord.Embed(title=title, description=description, color=color)

    embed.set_footer(
        text=f"Total: {total_messages:,} messages from {unique_users} users"
    )

    return embed


def create_global_leaderboard_embed(
    leaderboard: List[Tuple[int, str, int]],
    guild_name: str,
    total_messages: int,
    unique_users: int,
    channels_checked: int,
    timestamp: datetime,
) -> discord.Embed:
    """Create embed for global (server-wide) leaderboard"""
    description_lines = []

    for rank, user_name, count in leaderboard:
        medal = ""
        if rank == 1:
            medal = "[1st] "
        elif rank == 2:
            medal = "[2nd] "
        elif rank == 3:
            medal = "[3rd] "

        description_lines.append(
            f"{medal}**{rank}.** {user_name} - **{count:,}** messages"
        )

    description = "\n".join(description_lines)
    if len(description) > 4000:
        description = "\n".join(description_lines[:50]) + "\n\n*... and more*"

    embed = discord.Embed(
        title=f"Today's Messages Across {guild_name}",
        description=description,
        color=discord.Color.purple(),
        timestamp=timestamp,
    )

    embed.set_footer(
        text=f"Total today: {total_messages:,} messages from {unique_users} users across {channels_checked} channels"
    )

    return embed


def create_ai_summary_embed(
    summary_data: Dict,
    channel_name: str,
    time_desc: str,
    messages_analyzed: int,
    unique_users: int,
    timestamp: datetime,
    images_analyzed: int = 0,
) -> discord.Embed:
    """Create embed for AI-generated summary"""
    embed = discord.Embed(
        title=f"AI Summary - #{channel_name} ({time_desc.capitalize()})",
        description=summary_data.get("overview", "No overview available"),
        color=discord.Color.blue(),
        timestamp=timestamp,
    )

    # Add main topics
    if summary_data.get("main_topics"):
        topics = "\n".join([f"- {topic}" for topic in summary_data["main_topics"][:5]])
        embed.add_field(name="Main Topics", value=topics, inline=False)

    # Add key points
    if summary_data.get("key_points"):
        points = "\n".join([f"- {point}" for point in summary_data["key_points"][:5]])
        embed.add_field(name="Key Points", value=points, inline=False)

    # Add sentiment
    sentiment = summary_data.get("sentiment", "neutral").lower()

    embed.add_field(name="Sentiment", value=sentiment.capitalize(), inline=True)

    # Add stats
    embed.add_field(name="Messages", value=f"{messages_analyzed:,}", inline=True)
    embed.add_field(name="Users", value=f"{unique_users}", inline=True)

    # Add notable moments if available
    if summary_data.get("notable_moments"):
        embed.add_field(
            name="Notable Moments", value=summary_data["notable_moments"], inline=False
        )

    # Footer with model info and image analysis info
    footer_text = "Generated by gpt-oss:20b-cloud via Ollama"
    if images_analyzed > 0:
        footer_text += f" | {images_analyzed} image(s) analyzed"
    embed.set_footer(text=footer_text)

    return embed


def create_fallback_summary_embed(
    summary_text: str,
    channel_name: str,
    time_desc: str,
    messages_analyzed: int,
    unique_users: int,
    timestamp: datetime,
) -> discord.Embed:
    """Create fallback embed when JSON parsing fails"""
    embed = discord.Embed(
        title=f"AI Summary - #{channel_name} ({time_desc.capitalize()})",
        description=summary_text[:4000],  # Discord limit
        color=discord.Color.blue(),
        timestamp=timestamp,
    )
    embed.add_field(
        name="Messages Analyzed", value=f"{messages_analyzed:,}", inline=True
    )
    embed.add_field(name="Unique Users", value=f"{unique_users}", inline=True)
    embed.set_footer(text="Generated by gpt-oss:20b-cloud via Ollama (fallback format)")

    return embed
