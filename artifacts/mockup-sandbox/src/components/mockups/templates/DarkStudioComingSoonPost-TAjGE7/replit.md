# Botilon Chatbot

## Overview

Botilon is a Python chatbot with a web-based chat interface. It runs as a Flask web app where users can chat with Botilon through a modern, dark-themed chat UI in their browser. The bot greets users, checks their mood, offers activities (games, reading, learning), runs a Data Detective Dashboard, and wraps up with personalized questions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

- **Language**: Python with Flask web framework
- **Entry Point**: `app.py` — Flask server running on port 5000 (webview)
- **Templates**: `templates/index.html` — chat UI served by Flask
- **Static Assets**: `static/botilon.png` — Botilon logo (also at `/logo` route)
- **Console Version**: `main.py` — original terminal-based chatbot (kept for reference)

### Conversation State Machine (`app.py`)

The conversation is managed as a Flask session-based state machine. States include:

- `greeting` → `ask_mood` → `activity` (main loop)
- From `activity`: `play_what` → `play_game_name` / `ask_rps` / `rps_play` / `rps_again` / `play_soccer`
- From `activity`: `read_what`
- From `activity`: `learn_what` → `guessing` → `guess_again`
- From `activity`: `magic8` → `magic8_again`
- `continue_activity` — asks user if they want to do more, loops back or goes to dashboard
- `dashboard` — Data Detective Dashboard (main menu 1-4)
  - `stats_collecting` — collects 5 numbers for mean/median stats
  - `budget_amount` → `budget_tax_rate` → `budget_discount_rate` → `budget_price` → `budget_bill` → `budget_tip_rate`
- `final_subject` → `final_color` → `done`

### Web UI (`templates/index.html`)

- Dark purple/indigo gradient background
- Glass-morphism chat container with rounded corners
- Botilon logo in header with "Online" status indicator
- Bot messages on the left with logo avatar; user messages on the right in purple
- Animated typing indicator (three bouncing dots) between messages
- Enter key or send button to submit messages
- Messages delivered one-by-one with simulated typing delay

## Features

1. **Mood Detection** — Responds to happy/sad/nervous/excited
2. **Play** — Game name responses (Roblox, Minecraft, Fortnite, Chess), Rock Paper Scissors (with replay), Soccer/football/sports
3. **Read** — Responds to any book the user mentions
4. **Learn** — Number Guessing Game (1–100, with replay)
5. **Magic 8 Ball** — Random fortune responses (triggered by "idk")
6. **Data Detective Dashboard** — Data table, statistics (mean/median), budget calculator (tax/discount/tip)
7. **Personalized Goodbye** — Favorite subject, favorite color, personalized farewell

## Workflow

- **Name**: Run Botilon
- **Command**: `python app.py`
- **Output**: webview (port 5000)

## External Dependencies

- **Flask** — Web framework for serving the chat UI and handling API requests
- No databases, third-party APIs, or other external services used
