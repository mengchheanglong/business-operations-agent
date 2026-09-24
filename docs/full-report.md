# AI Small Business Operations Agent — Full Report

## 1. Problem Statement

Small businesses often manage customer orders, inventory, customer messages, and operational decisions **manually**. This causes:

- **Delayed customer responses** — staff must read each message and reply by hand
- **Stock mistakes and overselling** — inventory tracked in spreadsheets gets out of sync
- **Unnecessary manual work** — every order requires human data entry
- **Inconsistent decision-making** — different staff members approve/reject differently

## 2. Proposed AI Agent Solution

An **AI-powered operations agent** that receives customer order requests, understands intent, checks inventory in Google Sheets, makes intelligent decisions using **Deepseek LLM**, and notifies customers and the business owner via **Telegram**. The agent runs on **n8n** workflow orchestration.

## 3. Workflow Diagram

```
Customer sends order/request (Webhook)
            │
            ▼
┌─────────────────────────┐
│  1. AI understands request │  ← Deepseek LLM
│     (Extract intent)       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  2. Check inventory in    │  ← Google Sheets
│     Google Sheets         │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  3. AI decides whether    │  ← Deepseek LLM
│     order can be fulfilled│
│     (3 decision points)   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  4. AI chooses action     │  ← Autonomous routing
│     ├── Approve order     │
│     ├── Suggest alternative│
│     ├── Ask clarification │
│     ├── Require owner     │
│     │   approval          │
│     └── Reject request    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  5. Update inventory &   │  ← Google Sheets
│     order records        │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  6. Notify customer &    │  ← Telegram
│     owner via Telegram   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  7. Log final action     │  ← Google Sheets
└─────────────────────────┘
```

**Total: 10 workflow steps** (requirement: ≥5)

## 4. System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    n8n (Local Server)                      │
│                   http://localhost:5678                   │
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Webhook  │→ │ Deepseek │→ │  Route   │→ │ Google   │ │
│  │ Trigger  │  │ LLM x2  │  │ (5 paths)│  │ Sheets   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│       ↑                                      │    ↑       │
│       │                                      │    │       │
└───────┼──────────────────────────────────────┼────┼───────┘
        │                                      │    │
   Customer                            ┌─────┘    └─────┐
   (POST request)                      │                  │
                                  ┌────┴────┐       ┌─────┴─────┐
                                  │Telegram │       │  Google   │
                                  │  API    │       │  Sheets   │
                                  │(Notify) │       │ (4 tabs)  │
                                  └─────────┘       └───────────┘
```

### Components:
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Orchestration | n8n v2.8.4 | Workflow engine, routing, data flow |
| LLM | Deepseek (deepseek-chat) | Intent extraction + decision making |
| Database | Google Sheets | Products, Orders, Customers, Logs |
| Notifications | Telegram Bot API | Customer + owner messaging |
| Input | HTTP Webhook | Customer order entry point |

## 5. AI Tools, Models, and External Services

### LLM Model: Deepseek
- **Model:** `deepseek-chat` (DeepSeek-V3)
- **Base URL:** `https://api.deepseek.com`
- **OpenAI-compatible** — works with n8n's OpenAI node
- **Cost:** ~$0.14/M input tokens — orders of magnitude cheaper than GPT-4
- **Why Deepseek:** Fast, cheap, strong reasoning, OpenAI-compatible API

### External Services (4 total, requirement: ≥2):
1. **n8n** — Workflow orchestration (local instance)
2. **Google Sheets API** — Inventory, orders, customers, logs database
3. **Telegram Bot API** — Real-time notifications to customers and owner
4. **Deepseek API** — LLM reasoning and decision-making

### n8n Workflow Nodes (17 nodes):
| Node | Type | Purpose |
|------|------|---------|
| Webhook - Customer Order | Webhook | Receive order requests |
| Read Inventory | Google Sheets | Fetch current stock levels |
| AI - Extract Order Intent | Deepseek LLM | Parse product, qty, intent |
| AI - Decide Action | Deepseek LLM | Apply business rules, choose action |
| Route - Approve | IF | Auto-approve path |
| Route - Escalate | IF | Owner approval path |
| Route - Suggest Alternative | IF | Alternative product path |
| Route - Clarify | IF | Ask for more info path |
| Create Order Record | Google Sheets | Add order to Orders sheet |
| Update Stock | Google Sheets | Reduce inventory |
| Log Action | Google Sheets | Audit trail (4 variants) |
| Notify Customer | Telegram | Send response to customer |
| Notify Owner | Telegram | Escalation alert to owner |
| Respond to Customer | RespondToWebhook | Return result to caller |

## 6. AI Decision Points (3 decisions, requirement: ≥2)

### Decision 1 — Can the order be fulfilled?
| Requested | Stock | Decision |
|-----------|-------|----------|
| 5 | 20 | ✅ Approve |
| 15 | 8 | ❌ Cannot fulfill → Search alternative |

### Decision 2 — Does a human need to approve it?
| Order Value | Stock | Decision |
|-------------|-------|----------|
| $20 | Sufficient | 🤖 Agent auto-approves |
| $900 | Sufficient | 👤 Escalate to owner |

### Decision 3 — What happens when stock is insufficient?
| Condition | Action |
|-----------|--------|
| Stock ≥ quantity | Fulfill order |
| Stock < quantity + alternative exists | Suggest substitute |
| No suitable alternative | Inform customer unavailable |

### Autonomous Workflow-Changing Action
The agent **autonomously** selects one of 5 paths based on context — this is the workflow-changing decision the assignment requires.

## 7. Business Rules

| Rule ID | Rule Name | Condition | Action | Priority |
|---------|-----------|-----------|--------|----------|
| R001 | Auto-approve low value | total_value < $100 AND stock ≥ quantity | approve | 1 |
| R002 | Escalate high value | total_value ≥ $100 | escalate | 2 |
| R003 | Suggest alternative | stock < quantity AND alternative exists | suggest_alternative | 3 |
| R004 | Clarify unknown product | product not found | clarify | 4 |
| R005 | Reject no alternative | no suitable product | reject | 5 |

## 8. Google Sheets Database Structure

### Products Tab
| SKU | Product | Variant | Price | Stock | Low_Stock_Threshold |
|-----|---------|---------|-------|-------|---------------------|
| SH-BLK-B | Basic Shirt | Black | $10 | 20 | 5 |
| SH-WHT-B | Basic Shirt | White | $10 | 18 | 5 |
| SH-BLK-P | Premium Shirt | Black | $18 | 5 | 2 |
| SH-WHT-P | Premium Shirt | White | $18 | 8 | 2 |
| SH-RED-B | Basic Shirt | Red | $10 | 15 | 5 |

### Orders Tab
| Order_ID | Customer | Product | Variant | Qty | Total | Status | Timestamp | Notes |
|----------|----------|---------|---------|-----|-------|--------|-----------|-------|

### Customers Tab
| Customer_ID | Name | Phone | Telegram_Chat_ID | Notes |
|-------------|------|-------|------------------|-------|

### Logs Tab (Audit Trail)
| Log_ID | Timestamp | Action | Order_ID | Details | Customer_Notified | Owner_Notified |
|--------|-----------|--------|----------|---------|-------------------|----------------|

## 9. Sample Execution

### Test Input (Webhook POST):
```json
{
  "message": "I want 25 black Basic Shirts"
}
```

### Step-by-step Agent Processing:
1. **AI Extracts Intent:** `{product: "Basic Shirt", variant: "Black", quantity: 25, intent: "order"}`
2. **Checks Inventory:** Black Basic Shirt stock = 20
3. **AI Decides:** Cannot fulfill → Alternative exists (White, 18 in stock)
4. **AI Action:** `suggest_alternative`

### Customer Receives (Telegram):
```
📦 Order Update — ORD-003

We currently have 20 black Basic Shirts available.
We can fulfill your order with:
  • 20 × Basic Shirt (Black) — $200
  • 5 × Basic Shirt (White) — $50

Total: $250

Would you like to continue? Reply YES to confirm.
```

### Inventory NOT changed yet (customer hasn't approved)

### After Customer Replies "Yes":
- ✅ Order recorded in Google Sheets
- ✅ Stock reduced: Black 20→0, White 18→13
- ✅ Owner notified via Telegram
- ✅ Action logged in Logs sheet
- ✅ Customer receives confirmation

## 10. Hosting & Deployment

### Current: Local n8n
- Runs on `http://localhost:5678`
- Webhook accessible at `http://localhost:5678/webhook/order-request`

### Options for Project Submission:

**Option A: Run locally + share workflow file (recommended for grading)**
- Export workflow JSON → submit as project link
- Take screenshots of n8n workflow + execution
- Record screen demo → upload to YouTube (unlisted)

**Option B: Use ngrok for temporary public URL**
```bash
ngrok http 5678
# Gives you https://abc123.ngrok.io → public webhook URL
```

**Option C: n8n Cloud (free tier available)**
- Sign up at n8n.cloud
- Import workflow JSON → hosted instance
- Public URL automatically generated

**Option D: Self-host on a VPS**
- Deploy n8n on any cloud provider (DigitalOcean, AWS, etc.)
- Point domain → your n8n instance

## 11. Deliverables Checklist

| # | Deliverable | Status |
|---|-------------|--------|
| 1 | Problem statement | ✅ Section 1 |
| 2 | Proposed AI agent solution | ✅ Section 2 |
| 3 | Workflow diagram | ✅ Section 3 |
| 4 | System architecture | ✅ Section 4 |
| 5 | AI tools, models, and external services | ✅ Section 5 |
| 6 | Implementation screenshots | 📸 To capture |
| 7 | Sample execution (input and output) | ✅ Section 9 |
| 8 | Video demo link | 🎥 To record |
| 9 | Project link (n8n workflow) | ✅ workflows/order-agent-workflow.json |

## 12. Requirements Verification

| Requirement | Met? | Evidence |
|-------------|------|----------|
| Defined real-world problem | ✅ | Section 1 — small business order management |
| LLM for reasoning/decisions | ✅ | Deepseek LLM (2 nodes: extract + decide) |
| ≥2 external tools/services | ✅ | 4 services: n8n, Google Sheets, Telegram, Deepseek |
| ≥5 workflow steps | ✅ | 10 steps (Section 3) |
| ≥2 AI decision points | ✅ | 3 decisions (Section 6) |
| ≥1 autonomous workflow-changing decision | ✅ | 5-way routing (approve/escalate/suggest/clarify/reject) |
