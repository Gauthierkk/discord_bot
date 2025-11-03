"""
Message counting commands
"""

from datetime import datetime, timezone

import discord
from discord import app_commands

from config import logger
from services.analytics_service import (
    count_messages_by_user,
    create_dataframe,
    filter_user_messages_df,
    format_leaderboard,
    get_channel_stats,
    get_message_stats,
    get_user_message_count,
    get_user_percentage,
)
from services.message_service import (
    extract_message_data,
    fetch_messages_from_channel,
    fetch_messages_from_guild,
)
from utils.embed_builder import (
    create_global_leaderboard_embed,
    create_leaderboard_embed,
    create_user_count_embed,
)


def setup_commands(tree: app_commands.CommandTree):
    """Register counting commands"""

    @tree.command(
        name="messagecount", description="Count messages by user in this channel"
    )
    @app_commands.describe(user="Optional: specific user to check")
    async def messagecount(
        interaction: discord.Interaction, user: discord.Member = None
    ):
        """Count messages sent by users in the channel using pandas"""
        await interaction.response.defer()

        try:
            channel = interaction.channel

            # Fetch all messages
            logger.info(f"Fetching messages from #{channel.name}...")
            messages = await fetch_messages_from_channel(channel)

            if not messages:
                await interaction.followup.send("No messages found in this channel!")
                return

            # Extract and process data
            messages_data = extract_message_data(messages)
            df = create_dataframe(messages_data)
            df_users = filter_user_messages_df(df)

            if len(df_users) == 0:
                await interaction.followup.send(
                    "No user messages found in this channel!"
                )
                return

            if user:
                # Show stats for specific user
                count = get_user_message_count(df_users, user.id)
                percentage = get_user_percentage(df_users, user.id)

                embed = create_user_count_embed(user, count, percentage)
                await interaction.followup.send(embed=embed)
            else:
                # Show all users
                user_counts = count_messages_by_user(df_users)
                leaderboard = format_leaderboard(user_counts)
                stats = get_message_stats(df_users)

                embed = create_leaderboard_embed(
                    leaderboard,
                    title=f"Message Counts in #{channel.name}",
                    total_messages=stats["total_messages"],
                    unique_users=stats["unique_users"],
                )

                await interaction.followup.send(embed=embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to read message history!"
            )
        except Exception as e:
            logger.error(f"Error counting messages: {e}")
            await interaction.followup.send(
                f"An error occurred while counting messages: {str(e)}"
            )

    @tree.command(
        name="dailycount",
        description="Count messages sent today by each user in this channel",
    )
    async def dailycount(interaction: discord.Interaction):
        """Count messages sent today by users in the channel using pandas"""
        await interaction.response.defer()

        try:
            channel = interaction.channel

            # Get the start of today in UTC
            now = datetime.now(timezone.utc)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            # Fetch messages from today
            logger.info(
                f"Fetching messages from #{channel.name} since {today_start}..."
            )
            messages = await fetch_messages_from_channel(channel, after=today_start)

            if not messages:
                await interaction.followup.send(
                    "No messages found today in this channel!"
                )
                return

            # Extract and process data
            messages_data = extract_message_data(messages)
            df = create_dataframe(messages_data)
            df_users = filter_user_messages_df(df)

            if len(df_users) == 0:
                await interaction.followup.send(
                    "No user messages found today in this channel!"
                )
                return

            # Count messages by user
            user_counts = count_messages_by_user(df_users)
            leaderboard = format_leaderboard(user_counts)
            stats = get_message_stats(df_users)

            embed = create_leaderboard_embed(
                leaderboard,
                title=f"Today's Messages in #{channel.name}",
                total_messages=stats["total_messages"],
                unique_users=stats["unique_users"],
                color=discord.Color.green(),
            )

            await interaction.followup.send(embed=embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to read message history!"
            )
        except Exception as e:
            logger.error(f"Error counting daily messages: {e}")
            await interaction.followup.send(
                f"An error occurred while counting messages: {str(e)}"
            )

    @tree.command(
        name="globaldailycount",
        description="Count messages sent today across all channels in the server",
    )
    async def globaldailycount(interaction: discord.Interaction):
        """Count messages sent today by users across all channels in the server"""
        await interaction.response.defer()

        try:
            guild = interaction.guild

            # Get the start of today in UTC
            now = datetime.now(timezone.utc)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            # Fetch messages from all channels
            logger.info(
                f"Fetching messages from all channels in {guild.name} since {today_start}..."
            )
            messages_data = await fetch_messages_from_guild(guild, after=today_start)

            if not messages_data:
                await interaction.followup.send(
                    "No messages found today in this server!"
                )
                return

            # Process data
            df = create_dataframe(messages_data)
            df_users = filter_user_messages_df(df)

            if len(df_users) == 0:
                await interaction.followup.send(
                    "No user messages found today in this server!"
                )
                return

            # Count messages by user
            user_counts = count_messages_by_user(df_users)
            leaderboard = format_leaderboard(user_counts)
            stats = get_channel_stats(df_users)

            embed = create_global_leaderboard_embed(
                leaderboard,
                guild_name=guild.name,
                total_messages=stats["total_messages"],
                unique_users=stats["unique_users"],
                channels_checked=stats.get("channels_checked", 0),
                timestamp=now,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Error counting global daily messages: {e}")
            await interaction.followup.send(
                f"An error occurred while counting messages: {str(e)}"
            )
