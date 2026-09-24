# AI Small Business Operations Agent - Workflow Overview

## Workflow Name
AI Small Business Operations Agent

## Trigger
- **Type:** Webhook (POST)
- **Path:** `/webhook/order-request`
- **URL:** `http://localhost:5678/webhook/order-request`

## Node Flow (17 nodes)

```
[Webhook] → [Read Inventory] → [AI: Extract Intent] → [AI: Decide Action]
                                                              │
                    ┌─────────────────────────────────────────┤
                    │                                         │
              [Route: Approve]                          [Route: Escalate]
              TRUE → [Create Order]                     TRUE → [Notify Owner]
              FALSE → [Route: Escalate]                 FALSE → [Route: Suggest]
                    │                                         │
              [Update Stock]                            [Route: Suggest Alt]
                    │                                    TRUE → [Log Suggestion]
              [Log Action]                              FALSE → [Route: Clarify]
                    │                                         │
              [Notify Customer]                         [Route: Clarify]
                    │                                    TRUE → [Log Clarification]
              [Respond]                                 FALSE → [Notify Customer]
```

## Node Details

### 1. Webhook - Customer Order
- Receives POST requests with customer message
- Input: `{"message": "I want 25 black Basic Shirts"}`

### 2. Read Inventory
- Reads all products from Google Sheets "Products" tab
- Provides stock data for AI decision-making

### 3. AI - Extract Order Intent (Deepseek)
- Parses customer message
- Output: `{product, variant, quantity, intent, confidence}`

### 4. AI - Decide Action (Deepseek)
- Applies business rules
- Output: `{action, reason, suggested_items, total_value, customer_message}`
- Actions: approve | escalate | suggest_alternative | clarify | reject

### 5-8. Route Nodes (IF)
- Sequential routing based on action
- Each checks one action type

### 9. Create Order Record
- Appends to "Orders" sheet

### 10. Update Stock
- Reduces stock in "Products" sheet

### 11-14. Log Nodes
- Appends to "Logs" sheet for audit trail

### 15. Notify Customer (Telegram)
- Sends response to customer via Telegram

### 16. Notify Owner (Telegram)
- Sends escalation alert to owner

### 17. Respond to Customer
- Returns JSON result to webhook caller

## Business Rules

| Condition | Action |
|-----------|--------|
| total < $100 AND stock sufficient | Auto-approve |
| total >= $100 | Escalate to owner |
| stock < qty AND alternative exists | Suggest alternative |
| product not found | Ask clarification |
| no suitable product | Reject |

## Required Credentials

1. **Google Sheets OAuth2** — for reading/writing sheets
2. **Telegram Bot API** — for sending notifications
3. **OpenAI-compatible API** — configured for Deepseek

## Environment Variables

```
GOOGLE_SHEET_ID=your_sheet_id
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=customer_chat_id
TELEGRAM_OWNER_CHAT_ID=owner_chat_id
DEEPSEEK_API_KEY=your_deepseek_key
```
