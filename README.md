# AI Small Business Operations Agent

A standalone Python AI agent that automates customer order processing for small businesses. No n8n required.

## Features

- **AI-powered order processing** using Deepseek LLM
- **Google Sheets integration** for inventory, orders, customers, and logs
- **Telegram notifications** for customers and business owners
- **3 AI decision points** with autonomous workflow routing
- **Web interface** for easy testing
- **CLI mode** for command-line usage

## Requirements

- Python 3.10+
- Deepseek API key (https://platform.deepseek.com/)
- Telegram bot token (via @BotFather)
- Google Cloud service account (for Google Sheets API)

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Edit `.env`:
```
DEEPSEEK_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=1701034938
TELEGRAM_OWNER_CHAT_ID=owner_chat_id
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_CREDENTIALS_FILE=credentials.json
```

### 3. Set up Google Sheets
1. Create a Google Sheet with 5 tabs: Products, Orders, Customers, Logs, Business Rules
2. Create a service account in Google Cloud Console
3. Download the JSON key as `credentials.json`
4. Share the sheet with the service account email

### 4. Run the agent

**Interactive CLI mode:**
```bash
python agent.py
```

**Web interface:**
```bash
pip install flask
python web_app.py
# Open http://localhost:5000
```

**Demo mode (runs all test scenarios):**
```bash
python demo.py
```

## How It Works

### Workflow (10 steps)
1. Receive customer message
2. AI extracts order intent (Decision Point 1)
3. Check inventory in Google Sheets
4. AI decides action (Decision Points 2 & 3)
5. Route based on action (autonomous workflow-changing decision)
6. Execute action (update sheets, send notifications)
7. Log the action
8. Return result

### AI Decision Points

| Decision | Input | Output |
|----------|-------|--------|
| 1. Extract intent | Customer message | Product, variant, quantity, intent |
| 2. Fulfillment check | Order + inventory | Can/cannot fulfill |
| 3. Action selection | Rules + context | approve/escalate/suggest/clarify/reject |

### Autonomous Workflow-Changing Decision
The agent autonomously selects one of 5 paths:
- **Approve** — auto-fulfill order
- **Escalate** — notify owner for approval
- **Suggest alternative** — offer substitute products
- **Clarify** — ask customer for more info
- **Reject** — decline the order

## Project Structure
```
business-operations-agent/
├── agent.py              # Main AI agent (CLI)
├── web_app.py            # Web interface (Flask)
├── demo.py                # Demo script
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── credentials.json       # Google service account (you add this)
├── templates/
│   └── index.html         # Web UI
├── docs/
│   └── full-report.md     # Full report
├── workflows/             # n8n workflow (alternative)
└── demo/                  # Demo outputs
```

## Requirements Met

| Requirement | Implementation |
|-------------|---------------|
| LLM for reasoning | Deepseek API (deepseek-chat) |
| 2+ external tools | Google Sheets API, Telegram Bot API |
| 5+ workflow steps | 10 steps |
| 2+ AI decision points | 3 decisions |
| 1+ autonomous decision | 5-way routing |

## License
MIT
