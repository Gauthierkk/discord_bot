"""
Message service for fetching and filtering Discord messages
"""

from datetime import datetime
from typing import Dict, List

import discord

from config import logger


async def fetch_messages_from_channel(
    channel: discord.TextChannel,
    after: datetime = None,
    limit: int = None,
    oldest_first: bool = False,
) -> List[discord.Message]:
    """
    Fetch messages from a channel with optional filters

    Args:
        channel: Discord channel to fetch from
        after: Only fetch messages after this datetime
        limit: Maximum number of messages to fetch
        oldest_first: Whether to fetch oldest messages first

    Returns:
        List of Discord messages
    """
    messages = []
    try:
        async for message in channel.history(
            limit=limit, after=after, oldest_first=oldest_first
        ):
            messages.append(message)
        return messages
    except discord.Forbidden:
        logger.error(f"No permission to read history in #{channel.name}")
        raise
    except Exception as e:
        logger.error(f"Error fetching messages from #{channel.name}: {e}")
        raise


async def fetch_messages_from_guild(
    guild: discord.Guild, after: datetime = None, limit: int = None
) -> List[Dict]:
    """
    Fetch messages from all text channels in a guild

    Args:
        guild: Discord guild to fetch from
        after: Only fetch messages after this datetime
        limit: Maximum number of messages to fetch per channel

    Returns:
        List of message data dictionaries
    """
    messages_data = []

    for channel in guild.text_channels:
        try:
            # Check if bot has permission to read the channel
            permissions = channel.permissions_for(guild.me)
            if not permissions.read_message_history:
                logger.warning(f"No permission to read history in #{channel.name}")
                continue

            async for message in channel.history(limit=limit, after=after):
                # Skip system messages
                if message.type != discord.MessageType.default:
                    continue

                messages_data.append(
                    {
                        "user_id": message.author.id,
                        "user_name": message.author.display_name,
                        "is_bot": message.author.bot,
                        "channel_name": channel.name,
                        "content": message.content,
                        "timestamp": message.created_at,
                    }
                )
        except discord.Forbidden:
            logger.warning(f"Forbidden to read #{channel.name}")
            continue
        except Exception as e:
            logger.error(f"Error reading #{channel.name}: {e}")
            continue

    return messages_data


def filter_user_messages(messages: List[discord.Message]) -> List[discord.Message]:
    """
    Filter out bot messages and system messages

    Args:
        messages: List of Discord messages

    Returns:
        Filtered list of user messages only
    """
    return [
        msg
        for msg in messages
        if not msg.author.bot and msg.type == discord.MessageType.default
    ]


def extract_message_data(messages: List[discord.Message]) -> List[Dict]:
    """
    Extract relevant data from Discord messages

    Args:
        messages: List of Discord messages

    Returns:
        List of message data dictionaries
    """
    message_data = []
    for msg in messages:
        # Extract image URLs from attachments
        images = []
        for attachment in msg.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                images.append(attachment.url)

        message_data.append(
            {
                "user_id": msg.author.id,
                "user_name": msg.author.display_name,
                "is_bot": msg.author.bot,
                "content": msg.content,
                "timestamp": msg.created_at,
                "images": images,
            }
        )

    return message_data


def format_messages_for_ai(messages: List[Dict], max_messages: int = None) -> str:
    """
    Format messages for AI consumption

    Args:
        messages: List of message data dictionaries
        max_messages: Maximum number of messages to include

    Returns:
        Formatted string of messages
    """
    formatted = []

    for msg_data in messages:
        if msg_data.get("content"):
            formatted.append(f"{msg_data['user_name']}: {msg_data['content']}")

    if max_messages and len(formatted) > max_messages:
        formatted = formatted[-max_messages:]
        return f"[Showing last {max_messages} messages]\n\n" + "\n".join(formatted)

    return "\n".join(formatted)
