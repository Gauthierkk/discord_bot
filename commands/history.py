"""
History commands for retrieving channel message history
"""

import discord
from discord import app_commands

from config import logger
from services.message_service import fetch_messages_from_channel
from utils.embed_builder import create_first_message_embed


def setup_commands(tree: app_commands.CommandTree):
    """Register history commands"""

    @tree.command(
        name="firstmessage", description="Get the first message in this channel"
    )
    async def firstmessage(interaction: discord.Interaction):
        """Fetch and display the first message in the channel"""
        await interaction.response.defer()

        try:
            channel = interaction.channel

            # Fetch all messages (oldest first)
            messages = await fetch_messages_from_channel(channel, oldest_first=True)

            if not messages:
                await interaction.followup.send("No messages found in this channel!")
                return

            first_msg = messages[0]

            # Create embed
            embed = create_first_message_embed(first_msg, len(messages))

            # Send with jump link
            await interaction.followup.send(
                content=f"[Jump to message]({first_msg.jump_url})", embed=embed
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to read message history!"
            )
        except Exception as e:
            logger.error(f"Error fetching first message: {e}")
            await interaction.followup.send(
                "An error occurred while fetching messages."
            )
