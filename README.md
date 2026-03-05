# Study Buddy

Study Buddy is a Python-based background application and Telegram bot designed to help you track your study habits and minimize distractions. It monitors your active windows on Windows, categorizes your activity, and uses a Groq-powered LLM (LLaMA-3) to provide study analytics, feedback, and interactive chat via Telegram.

## Features

- **Activity Tracking**: Runs in the background (Windows only) to track the active window and identify idle time.
- **Smart Categorization**: Automatically categorises your window activities.
- **Telegram Interface**: Interact with your study data directly through a Telegram bot.
- **AI-Powered Insights**: Uses Groq (LLaMA-3.3-70b) to act as a supportive study buddy, analyzing your active time and providing intelligent insights.
- **Local Database**: All activity data is strictly stored locally in an SQLite database (`study_buddy.db`) for your privacy.

## Prerequisites

- **Python 3.8+**
- **Operating System**: Windows (required for the window tracking collector components `pygetwindow` & `pywin32`)
- **API Keys**: 
  - A [Groq API Key](https://console.groq.com/keys)
  - A Telegram Bot Token (from [@BotFather](https://t.me/botfather))

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd Study_buddy
   ```

2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**:
   - Copy the `.env.example` file and rename it to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Open `.env` and fill in your actual API keys and Chat ID:
     ```ini
     GROQ_API_KEY=gsk_your_key_here
     GROQ_MODEL=llama-3.3-70b-versatile
     TELEGRAM_BOT_TOKEN=your_bot_token_here
     TELEGRAM_CHAT_ID=your_chat_id_here
     ```

## Usage

The application is split into two separate background processes. You will need to run both concurrently for full functionality.

1. **Start the Data Collector**:
   This process monitors your active window, tracks idle time, and writes data to the local SQLite database.
   ```bash
   python run_collector.py
   ```

2. **Start the Telegram Bot**:
   This process handles your communication with the bot, fetches data from the database, and uses the Groq API to generate responses.
   Open a new terminal window, activate your virtual environment, and run:
   ```bash
   python run_bot.py
   ```

## Project Structure

- `bot/` - Telegram bot polling loop and message routing logic.
- `collector/` - Windows active window tracking and idle time detection modules.
- `core/` - Core logic, SQLite database operations (`db.py`), rule matching, and Groq LLM integration (`grok_client.py`).
- `notifier/` - Notification utilities for Telegram.
- `run_bot.py` - Entry point to start the Telegram bot.
- `run_collector.py` - Entry point to start the background data collector.
- `config.py` - Global configuration and environment variable loader.

## License

This project is licensed under the terms of the LICENSE file included in the repository.
