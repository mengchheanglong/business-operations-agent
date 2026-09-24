# n8n Credentials Configuration Guide

## Google Sheets OAuth2 Credential

### Step 1: Create Credential in n8n
1. In n8n (http://localhost:5678), go to **Credentials** → **Add Credential**
2. Search for **Google Sheets OAuth2**
3. Fill in the following:
   - **Client ID:** `your_client_id.apps.googleusercontent.com`
   - **Client Secret:** `your_client_secret`
4. Click **Connect my Google Account**
5. Sign in with the Google account that owns the sheet
6. Grant permission to access Google Sheets

### Step 2: Configure Google Cloud OAuth Consent Screen
If you haven't already:
1. In Google Cloud Console, go to **APIs & Services** → **OAuth consent screen**
2. User type: **External** (or Internal if using Google Workspace)
3. Fill in app name, email, etc.
4. Add scope: `https://www.googleapis.com/auth/spreadsheets`
5. Add your own email as a test user
6. Submit (or leave in testing — works for your account)

### Step 3: Share Your Sheet with Your Account
1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1Q3aTYv-3WpF2pX1QEFlsbhUbSMuis6XI6DrjQQnGR5o/edit
2. Click **Share** → add your own Gmail account as **Editor**
3. The OAuth credential uses YOUR account, not a service account

---

## Telegram Bot Credential

### Step 1: Create Bot
1. On Telegram, message **@BotFather**
2. Send `/newbot`
3. Give it a name (e.g., "Business Ops Agent")
4. Give it a username (e.g., `MyBusinessOpsBot`)
5. Copy the **Bot Token** (looks like `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Chat IDs
1. Send a message to your bot
2. Open this URL in browser (replace YOUR_TOKEN):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
3. Find your chat ID in the response (a number like `123456789`)
4. For the owner chat ID — have the owner message the bot too

### Step 3: Create Telegram Credential in n8n
1. In n8n → **Credentials** → **Add Credential** → **Telegram Bot API**
2. **Access Token:** paste your bot token
3. Save

---

## Deepseek Credential

### Step 1: Get API Key
1. Go to https://platform.deepseek.com/
2. Sign up / log in
3. Go to **API Keys** → **Create API Key**
4. Copy the key

### Step 2: Create Credential in n8n
1. In n8n → **Credentials** → **Add Credential** → **OpenAI Chat Model**
2. **Base URL:** `https://api.deepseek.com`
3. **API Key:** paste your Deepseek API key
4. **Model:** `deepseek-chat`
5. Save

---

## Environment Variables

Create a `.env` file in the project root (`C:\Users\User\Internship\business-operations-agent\.env`):

```
GOOGLE_SHEET_ID=1Q3aTYv-3WpF2pX1QEFlsbhUbSMuis6XI6DrjQQnGR5o
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TELEGRAM_OWNER_CHAT_ID=owner_chat_id_here
DEEPSEEK_API_KEY=your_deepseek_key_here
```

---

## After Setup: Import the Workflow

1. In n8n, go to **Workflows** → **Import from File**
2. Select `C:\Users\User\Internship\business-operations-agent\workflows\order-agent-workflow.json`
3. Update the credential references if needed
4. Toggle the workflow to **Active**
5. Test with:
   ```bash
   curl -X POST http://localhost:5678/webhook/order-request \
     -H "Content-Type: application/json" \
     -d '{"message": "I want 25 black Basic Shirts"}'
   ```
