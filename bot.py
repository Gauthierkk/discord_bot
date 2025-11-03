"""
Discord History Bot - Main Entry Point
A bot that retrieves channel history and analyzes message counts
"""

import discord
from discord import app_commands

# Import command modules
from commands import ai, counting, history

# Import configuration
from config import TOKEN, logger

# Create bot instance with required intents
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    """Called when the bot is ready and connected"""
    logger.info(f"{bot.user} has connected to Discord!")
    logger.info(f"Bot is in {len(bot.guilds)} guild(s)")

    # List all guilds
    if bot.guilds:
        logger.info("Guilds:")
        for guild in bot.guilds:
            logger.info(
                f"  - {guild.name} (ID: {guild.id}) - {guild.member_count} members"
            )
    else:
        logger.warning("Bot is not in any guilds!")

    # Sync slash commands
    try:
        synced = await tree.sync()
        logger.info(f"Synced {len(synced)} command(s) globally")

        # For faster testing, also sync to each guild
        for guild in bot.guilds:
            try:
                guild_synced = await tree.sync(guild=guild)
                logger.info(f"Synced {len(guild_synced)} command(s) to {guild.name}")
            except Exception as guild_error:
                logger.error(f"Failed to sync to {guild.name}: {guild_error}")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")


# Register commands from modules
history.setup_commands(tree)
counting.setup_commands(tree)
ai.setup_commands(tree)


# Run the bot
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
