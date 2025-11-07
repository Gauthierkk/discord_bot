"""
AI-powered commands using Ollama
"""

import json

import discord
from discord import app_commands

from config import MAX_MESSAGES_FOR_AI, logger
from services.ai_service import generate_summary
from services.analytics_service import create_dataframe, filter_user_messages_df
from services.message_service import (
    extract_message_data,
    fetch_messages_from_channel,
    format_messages_for_ai,
)
from utils.embed_builder import create_ai_summary_embed, create_fallback_summary_embed
from utils.validators import calculate_time_window, validate_timeframe


def setup_commands(tree: app_commands.CommandTree):
    """Register AI commands"""

    @tree.command(
        name="summarize",
        description="Generate an AI summary of messages in this channel",
    )
    @app_commands.describe(timeframe='Enter like "1 hour" or "2 days" (default: 1 day)')
    async def summarize(
        interaction: discord.Interaction,
        timeframe: str = "1 day",
    ):
        """Generate a summary of messages using Ollama"""
        await interaction.response.defer()

        try:
            channel = interaction.channel

            # Parse the timeframe string (e.g., "1 hour", "2 days", "24 hours")
            parts = timeframe.strip().split()

            if len(parts) != 2:
                await interaction.followup.send(
                    'Invalid format! Please use format like "1 hour" or "2 days"'
                )
                return

            try:
                time_value = int(parts[0])
                time_unit = parts[1]
            except ValueError:
                await interaction.followup.send(
                    'Invalid number! Please use format like "1 hour" or "2 days"'
                )
                return

            # Validate timeframe
            is_valid, error_message = validate_timeframe(time_value, time_unit)
            if not is_valid:
                await interaction.followup.send(error_message)
                return

            # Calculate time window
            time_start, time_desc = calculate_time_window(time_value, time_unit)

            # Fetch messages
            logger.info(
                f"Fetching messages from #{channel.name} for the {time_desc}..."
            )
            messages = await fetch_messages_from_channel(channel, after=time_start)

            if not messages:
                await interaction.followup.send(
                    f"No messages found in the {time_desc} in this channel to summarize!"
                )
                return

            # Extract and process data
            messages_data = extract_message_data(messages)
            df = create_dataframe(messages_data)
            df_users = filter_user_messages_df(df)

            if len(df_users) == 0:
                await interaction.followup.send(
                    f"No text messages found in the {time_desc} in this channel to summarize!"
                )
                return

            # Sort by timestamp
            df_users = df_users.sort_values("timestamp")

            # Format messages for AI
            messages_list = df_users.to_dict("records")
            formatted_text = format_messages_for_ai(messages_list, MAX_MESSAGES_FOR_AI)

            if not formatted_text or formatted_text.strip() == "":
                await interaction.followup.send(
                    f"No text messages found in the {time_desc} in this channel to summarize!"
                )
                return

            # Collect image URLs from messages
            image_urls = []
            for msg_data in messages_list:
                if msg_data.get("images"):
                    image_urls.extend(msg_data["images"])

            # Send initial status message
            image_note = (
                f" (including {len(image_urls)} image(s))" if image_urls else ""
            )
            status_msg = await interaction.followup.send(
                f"Generating AI summary{image_note}... This may take a moment."
            )

            # Call AI service
            try:
                from datetime import datetime, timezone

                now = datetime.now(timezone.utc)

                summary_data = await generate_summary(
                    formatted_text, time_desc, image_urls=image_urls
                )

                # Create embed with summary
                embed = create_ai_summary_embed(
                    summary_data,
                    channel_name=channel.name,
                    time_desc=time_desc,
                    messages_analyzed=len(messages_list),
                    unique_users=df_users["user_id"].nunique(),
                    timestamp=now,
                    images_analyzed=len(image_urls),
                )

                # Edit the status message with the summary
                await status_msg.edit(content=None, embed=embed)

            except json.JSONDecodeError as json_error:
                logger.error(f"JSON parsing error: {json_error}")

                # Fallback to simple text display
                from datetime import datetime, timezone

                now = datetime.now(timezone.utc)

                # Get the raw summary from the exception context if available
                summary_text = "Failed to parse AI response"

                embed = create_fallback_summary_embed(
                    summary_text,
                    channel_name=channel.name,
                    time_desc=time_desc,
                    messages_analyzed=len(messages_list),
                    unique_users=df_users["user_id"].nunique(),
                    timestamp=now,
                )

                await status_msg.edit(content=None, embed=embed)

            except Exception as ollama_error:
                logger.error(f"Ollama error: {ollama_error}")
                await status_msg.edit(
                    content=f"Failed to generate summary. Make sure Ollama is running and the gpt-oss:20b-cloud model is installed.\n\nError: {str(ollama_error)}"
                )

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to read message history!"
            )
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            await interaction.followup.send(
                f"An error occurred while generating the summary: {str(e)}"
            )
