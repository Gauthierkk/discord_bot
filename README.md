# Discord History Bot

A simple Discord bot that retrieves channel history and analyzes message counts.

## Features

- **First Message**: Retrieves the first message ever sent in a channel
- **Message Counting**: Count messages by all users or specific user using pandas
- **Daily Stats**: View today's message counts by user in a channel
- **Global Daily Stats**: View today's message counts across all channels in the server
- **AI Summarization**: Generate intelligent summaries of conversations using Ollama with flexible time frames (1-7 days or 1-168 hours), including image analysis
- **Guild Detection**: Lists all servers the bot is in on startup

## Commands

- `/firstmessage` - Get the first message ever sent in the current channel
- `/messagecount [user]` - Count messages by user (all users if not specified) in this channel
- `/dailycount` - Show message counts for today by each user in this channel
- `/globaldailycount` - Show message counts for today across all channels in the server
- `/summarize [timeframe] [unit]` - Generate an AI summary of messages using Ollama (gpt-oss:20b-cloud)
  - `timeframe`: Number of hours or days to analyze (default: 1)
  - `unit`: "Hours" or "Days" (default: Days)
  - Max: 7 days or 168 hours

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- A Discord account
- Basic command line knowledge

### 2. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - **MESSAGE CONTENT INTENT** (required for reading messages)
5. Copy the bot token (you'll need this later)

### 3. Install Dependencies

This project uses [uv](https://github.com/astral-sh/uv) for fast dependency management.

```bash
# Clone or download this repository
cd discord-bot

# Install uv if you haven't already
# On macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create a virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the project dependencies
uv pip install -e .
```

**Alternative (using pip):**
```bash
# If you prefer pip over uv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 4. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your bot token
# Replace 'your_bot_token_here' with your actual token
```

### 5. Invite Bot to Server

1. In Discord Developer Portal, go to "OAuth2" > "URL Generator"
2. Select scopes:
   - `bot`
   - `applications.commands`
3. Select bot permissions:
   - `View Channels` (View channels in the server)
   - `Send Messages` (Send messages in text channels)
   - `Embed Links` (Display rich embeds)
   - `Read Message History` (Read past messages in channels - required for `/firstmessage`)
   - `Use Slash Commands` (Use application commands)
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

**Quick Invite URL** (replace `YOUR_CLIENT_ID` with your bot's Application ID):
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=67584&scope=bot%20applications.commands
```

**Required Permissions Summary:**
- **Privileged Intent**: MESSAGE CONTENT INTENT (enabled in Developer Portal)
- **Channel Permissions**: View Channels, Send Messages, Embed Links, Read Message History, Use Slash Commands
- **Permission Integer**: `67584` (includes all required permissions above)

### 6. Set up Ollama (Optional - for AI Summarization)

To use the `/summarize` command with image analysis, you need to install and run Ollama:

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# For Windows, download from https://ollama.com/download

# Pull the required models
ollama pull gpt-oss:20b-cloud  # For text summarization
ollama pull llava               # For image analysis (vision model)

# Start Ollama (it usually runs automatically)
ollama serve
```

**Note**: The bot will automatically detect images in conversations and use the `llava` vision model to analyze them before generating the summary.

### 7. Run the Bot

```bash
# Using Python directly
python bot.py

# Or using Make
make run
```

You should see:
```
[Bot Name] has connected to Discord!
Bot is in X guild(s)
Synced Y command(s) globally
Synced Y command(s) to [Your Server Name]
```

## Project Structure

The bot follows a clean FastAPI-style architecture with clear separation of concerns:

```
discord-bot/
├── bot.py                      # Main entry point - bot initialization & command registration
├── config.py                   # Configuration - env vars, constants, settings
│
├── commands/                   # Command definitions (like FastAPI routers)
│   ├── history.py              # /firstmessage
│   ├── counting.py             # /messagecount, /dailycount, /globaldailycount
│   └── ai.py                   # /summarize
│
├── services/                   # Business logic layer
│   ├── message_service.py      # Message fetching, filtering, formatting
│   ├── ai_service.py           # Ollama integration, prompt building
│   └── analytics_service.py    # Statistics, data processing with pandas
│
├── utils/                      # Utility functions
│   ├── embed_builder.py        # Discord embed creation helpers
│   └── validators.py           # Input validation
│
├── pyproject.toml              # Project dependencies and configuration
├── uv.lock                     # Locked dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## How It Works

1. **Slash Commands**: The bot uses Discord's modern slash command interface
2. **First Message**: Reads all messages in a channel (oldest first) and displays the first one with metadata including author, timestamp, and a jump link
3. **Pandas Processing**: Uses pandas DataFrames for efficient message data processing and analysis
4. **Smart Filtering**: Automatically filters out bot messages and system messages (joins, pins, etc.)
5. **Global Analysis**: Can scan all text channels in a server to provide server-wide statistics
6. **AI Summarization**: Fetches messages with their images, uses llava vision model to analyze images, then sends everything to gpt-oss:20b-cloud for intelligent summarization including image descriptions

## Security Notes

- Never commit your `.env` file or share your bot token
- The token gives full access to your bot
- If your token is exposed, regenerate it immediately in Discord Developer Portal

## Troubleshooting

### Bot doesn't respond to commands
- Ensure slash commands are synced (check bot startup logs for "Synced X command(s)")
- Verify the bot has proper permissions in your server
- Wait a few minutes for Discord to update command cache
- Try kicking and re-inviting the bot with the correct permissions

### Bot shows 0 guilds on startup
- Make sure you invited the bot using the OAuth2 URL with both `bot` and `applications.commands` scopes
- Check that the bot wasn't kicked from the server
- Verify MESSAGE CONTENT INTENT is enabled in Developer Portal

### `/firstmessage` gives permission error
- Ensure the bot has "Read Message History" permission
- Check the channel-specific permissions for the bot role
- The bot needs to be able to view the channel

### `/summarize` command fails
- Make sure Ollama is installed and running (`ollama serve`)
- Verify the gpt-oss:20b-cloud model is installed (`ollama pull gpt-oss:20b-cloud`)
- Check Ollama is accessible at http://localhost:11434
- If the model is not available, you can use other Ollama models by modifying the model name in `bot.py`

## Development

### Tech Stack

This bot uses:
- **discord.py 2.0+**: Modern Discord API wrapper
- **pandas 2.0+**: Data analysis and processing
- **ollama**: Interface with local LLMs for AI summarization
- **aiohttp**: Async HTTP client for downloading images
- **python-dotenv**: Environment variable management
- **ruff**: Fast Python linter and formatter

### Code Quality

The project uses Ruff for code formatting and linting. You can use either Ruff directly or the provided Makefile:

```bash
# Using Make (recommended)
make format       # Format code with ruff
make lint         # Check code for issues
make check        # Check and auto-fix issues

# Using Ruff directly
ruff format .     # Format code
ruff check .      # Check for issues
ruff check . --fix # Auto-fix issues
```

Configuration is in `pyproject.toml` with default settings (88-char line length, PEP 8 compliance).

### Makefile Commands

The project includes a Makefile for common tasks:

```bash
make help         # Show all available commands
make run          # Run the Discord bot
make format       # Format code with ruff
make lint         # Lint code with ruff
make check        # Check and auto-fix code issues
make install      # Install dependencies
make install-dev  # Install dev dependencies (including ruff)
```

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Discord.py documentation: https://discordpy.readthedocs.io/
3. Check Discord Developer Portal for bot configuration
