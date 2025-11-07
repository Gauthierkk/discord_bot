"""
Humour commands
"""

import discord
from discord import app_commands


def setup_commands(tree: app_commands.CommandTree):
    """Register humour commands"""

    @tree.command(
        name="listen-to-hank",
        description="Listen to Hank?",
    )
    async def listen_to_hank(interaction: discord.Interaction):
        """Should you listen to Hank?"""
        await interaction.response.send_message("no")
