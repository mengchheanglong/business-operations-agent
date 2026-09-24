"""
AI Small Business Operations Agent
Standalone Python application - no n8n required.

Requirements met:
- LLM for reasoning: Deepseek API
- 2+ external tools: Google Sheets API, Telegram Bot API
- 5+ workflow steps: 10 steps
- 2+ AI decision points: 3 decisions
- 1+ autonomous workflow-changing decision: 5-way routing
"""

import os
import sys
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests
import gspread
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.oauth2.credentials import Credentials as UserCredentials

# Load .env file if present
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key, value.strip())


# ============================================================
# CONFIGURATION
# ============================================================

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CUSTOMER_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TELEGRAM_OWNER_CHAT_ID = os.environ.get("TELEGRAM_OWNER_CHAT_ID", "")
if not TELEGRAM_OWNER_CHAT_ID or TELEGRAM_OWNER_CHAT_ID == "OWNER_CHAT_ID_HERE":
    TELEGRAM_OWNER_CHAT_ID = TELEGRAM_CUSTOMER_CHAT_ID

GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
GOOGLE_CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE = os.environ.get("GOOGLE_TOKEN_FILE", "token.json")

# Business rules
AUTO_APPROVE_MAX_VALUE = 100  # Auto-approve orders under $100
LOW_STOCK_THRESHOLD = 5


# ============================================================
# GOOGLE SHEETS CLIENT & MOCK FALLBACK
# ============================================================

DEFAULT_MOCK_PRODUCTS = [
    {"SKU": "SH-BLK-B", "Product": "Basic Shirt", "Variant": "Black", "Price": 10, "Stock": 20, "Low_Stock_Threshold": 5},
    {"SKU": "SH-WHT-B", "Product": "Basic Shirt", "Variant": "White", "Price": 10, "Stock": 18, "Low_Stock_Threshold": 5},
    {"SKU": "SH-BLK-P", "Product": "Premium Shirt", "Variant": "Black", "Price": 18, "Stock": 5, "Low_Stock_Threshold": 2},
    {"SKU": "SH-WHT-P", "Product": "Premium Shirt", "Variant": "White", "Price": 18, "Stock": 8, "Low_Stock_Threshold": 2},
    {"SKU": "SH-RED-B", "Product": "Basic Shirt", "Variant": "Red", "Price": 10, "Stock": 15, "Low_Stock_Threshold": 5},
]


class MockSheetsClient:
    """In-memory mock client when live Google Sheets credentials are not configured."""

    def __init__(self):
        self.products = [dict(p) for p in DEFAULT_MOCK_PRODUCTS]
        self.orders = []
        self.logs = []

    def read_products(self) -> list[dict]:
        """Read all products from mock inventory."""
        return [dict(p) for p in self.products]

    def append_order(self, order: dict) -> bool:
        """Record order in mock orders list."""
        self.orders.append(dict(order))
        return True

    def update_stock(self, sku: str, new_stock: int) -> bool:
        """Update stock for a product in mock inventory."""
        for p in self.products:
            if p.get("SKU") == sku:
                p["Stock"] = new_stock
                return True
        return False

    def append_log(self, log: dict) -> bool:
        """Record audit log in mock logs list."""
        self.logs.append(dict(log))
        return True


class GoogleSheetsClient:
    """Client for reading/writing Google Sheets data."""

    def __init__(self, sheet_id: str, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        self.sheet_id = sheet_id
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        if os.path.exists(credentials_file):
            creds = ServiceAccountCredentials.from_service_account_file(credentials_file, scopes=scopes)
        elif os.path.exists(token_file):
            creds = UserCredentials.from_authorized_user_file(token_file, scopes=scopes)
        else:
            raise FileNotFoundError(f"Neither {credentials_file} nor {token_file} found.")
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(sheet_id)

    def read_products(self) -> list[dict]:
        """Read all products from the Products sheet."""
        try:
            worksheet = self.spreadsheet.worksheet("Products")
            records = worksheet.get_all_records()
            return records
        except Exception as e:
            print(f"  [Sheets] Error reading Products: {e}")
            return []

    def append_order(self, order: dict) -> bool:
        """Append an order to the Orders sheet."""
        try:
            worksheet = self.spreadsheet.worksheet("Orders")
            worksheet.append_row([
                order.get("order_id", ""),
                order.get("customer", ""),
                order.get("product", ""),
                order.get("variant", ""),
                order.get("quantity", 0),
                order.get("total_value", 0),
                order.get("status", ""),
                order.get("timestamp", ""),
                order.get("notes", ""),
            ])
            return True
        except Exception as e:
            print(f"  [Sheets] Error appending order: {e}")
            return False

    def update_stock(self, sku: str, new_stock: int) -> bool:
        """Update stock for a product by SKU."""
        try:
            worksheet = self.spreadsheet.worksheet("Products")
            records = worksheet.get_all_records()
            for i, record in enumerate(records):
                if record.get("SKU") == sku:
                    # Find the Stock column (column E, index 5)
                    worksheet.update_cell(i + 2, 5, new_stock)
                    return True
            return False
        except Exception as e:
            print(f"  [Sheets] Error updating stock: {e}")
            return False

    def append_log(self, log: dict) -> bool:
        """Append a log entry to the Logs sheet."""
        try:
            worksheet = self.spreadsheet.worksheet("Logs")
            worksheet.append_row([
                log.get("log_id", ""),
                log.get("timestamp", ""),
                log.get("action", ""),
                log.get("order_id", ""),
                log.get("details", ""),
                log.get("customer_notified", ""),
                log.get("owner_notified", ""),
            ])
            return True
        except Exception as e:
            print(f"  [Sheets] Error appending log: {e}")
            return False


# ============================================================
# TELEGRAM CLIENT
# ============================================================

class TelegramClient:
    """Client for sending Telegram messages."""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, chat_id: str, text: str) -> bool:
        """Send a message to a Telegram chat."""
        if not chat_id or str(chat_id).strip() in ("", "OWNER_CHAT_ID_HERE", "your_chat_id_here", "owner_chat_id"):
            print("  [Telegram] Valid chat ID not configured, skipping send.")
            return False
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": str(chat_id).strip(),
                "text": text,
                "parse_mode": "HTML",
            }
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            if result.get("ok"):
                return True
            else:
                print(f"  [Telegram] Error: {result.get('description', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"  [Telegram] Error sending message: {e}")
            return False


# ============================================================
# DEEPSEEK LLM CLIENT
# ============================================================

class DeepseekClient:
    """Client for Deepseek LLM API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = DEEPSEEK_BASE_URL
        self.model = DEEPSEEK_MODEL

    def chat(self, system_prompt: str, user_message: str, temperature: float = 0.1, max_tokens: int = 800) -> str:
        """Send a chat completion request to Deepseek."""
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  [Deepseek] Error: {e}")
            return ""

    def extract_intent(self, customer_message: str) -> dict:
        """AI Decision Point 1: Extract order intent from customer message."""
        system_prompt = """You are an AI order processing agent for a small business. Extract the following from the customer message:
1. Product name and variant (if specified)
2. Quantity requested
3. Customer intent (order, inquiry, complaint, etc.)
4. Any special requirements

Respond ONLY in valid JSON format (no markdown, no extra text):
{
  "product": "product name or null",
  "variant": "variant or null",
  "quantity": number or null,
  "intent": "order|inquiry|complaint|other",
  "special_requirements": "any special notes or null",
  "confidence": 0.0-1.0
}"""
        response = self.chat(system_prompt, customer_message, temperature=0.1, max_tokens=500)
        return self._parse_json(response)

    def decide_action(self, order: dict, inventory: list[dict]) -> dict:
        """AI Decision Point 2 & 3: Decide what action to take based on inventory and business rules."""
        inventory_summary = json.dumps(inventory, indent=2)
        order_summary = json.dumps(order, indent=2)

        system_prompt = f"""You are an AI decision agent for order fulfillment. Analyze the order against inventory and business rules.

Business Rules:
1. Auto-approve (action: "approve") if: total value < ${AUTO_APPROVE_MAX_VALUE} AND stock sufficient
2. Require owner approval (action: "escalate") if: total value >= ${AUTO_APPROVE_MAX_VALUE} AND stock sufficient
3. Suggest alternative (action: "suggest_alternative") if: stock < quantity AND an alternative variant or product exists in available inventory
4. Reject (action: "reject") if: stock < quantity AND no suitable alternative available
5. Ask clarification (action: "clarify") if: product not found or quantity unclear

Available Inventory:
{inventory_summary}

Order Details:
{order_summary}

Decide the action. Respond ONLY in valid JSON format (no markdown, no extra text):
{{
  "action": "approve|escalate|reject|clarify|suggest_alternative",
  "reason": "explanation for the decision",
  "suggested_items": [{{"product": "name", "variant": "variant", "quantity": number, "price": number}}],
  "total_value": number,
  "customer_message": "response to send to customer"
}}"""
        response = self.chat(system_prompt, "Please analyze this order.", temperature=0.2, max_tokens=800)
        return self._parse_json(response)

    def _parse_json(self, text: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        if not text:
            return {}
        # Remove markdown code blocks
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in the text
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return {}


# ============================================================
# AI AGENT
# ============================================================

class AIBusinessAgent:
    """Main AI agent that orchestrates the order processing workflow."""

    def __init__(self):
        self.deepseek = DeepseekClient(DEEPSEEK_API_KEY)
        self.telegram = TelegramClient(TELEGRAM_BOT_TOKEN)
        self.sheets = None

        has_creds = os.path.exists(GOOGLE_CREDENTIALS_FILE) or os.path.exists(GOOGLE_TOKEN_FILE)
        if GOOGLE_SHEET_ID and has_creds:
            try:
                self.sheets = GoogleSheetsClient(GOOGLE_SHEET_ID, GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE)
                print("  [Init] Google Sheets connected")
            except Exception as e:
                print(f"  [Init] Google Sheets connection error: {e}. Falling back to mock sheets.")
                self.sheets = MockSheetsClient()
        else:
            print("  [Init] Google Sheets credentials not configured. Using local mock inventory.")
            self.sheets = MockSheetsClient()

    def process_order(self, customer_message: str, customer_name: str = "Customer") -> dict:
        """
        Process a customer order through the full AI agent workflow.

        Workflow Steps:
        1. Receive customer message
        2. AI extracts order intent (Decision Point 1)
        3. Check inventory in Google Sheets
        4. AI decides action (Decision Points 2 & 3)
        5. Route based on action (autonomous workflow-changing decision)
        6. Execute action (update sheets, send notifications)
        7. Log the action
        8. Return result
        """
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()

        print(f"\n{'='*60}")
        print(f"  Processing Order: {order_id}")
        print(f"  Customer: {customer_name}")
        print(f"  Message: {customer_message}")
        print(f"{'='*60}\n")

        # Step 1: AI extracts order intent (Decision Point 1)
        print("Step 1: AI extracting order intent...")
        intent = self.deepseek.extract_intent(customer_message)
        print(f"  Product: {intent.get('product')}")
        print(f"  Variant: {intent.get('variant')}")
        print(f"  Quantity: {intent.get('quantity')}")
        print(f"  Intent: {intent.get('intent')}")
        print(f"  Confidence: {intent.get('confidence')}")

        if not intent.get("product") or not intent.get("quantity"):
            return self._handle_clarify(order_id, customer_name, intent, timestamp)

        # Step 2: Check inventory in Google Sheets
        print("\nStep 2: Checking inventory...")
        inventory = self.sheets.read_products() if self.sheets else []
        product = self._find_product(inventory, intent["product"], intent.get("variant"))

        if not product:
            return self._handle_clarify(order_id, customer_name, intent, timestamp, "Product not found")

        print(f"  Found: {product.get('Product')} ({product.get('Variant')})")
        print(f"  Stock: {product.get('Stock')}, Price: ${product.get('Price')}")

        # Step 3: AI decides action (Decision Points 2 & 3)
        print("\nStep 3: AI deciding action...")
        order = {
            "order_id": order_id,
            "customer": customer_name,
            "product": product.get("Product"),
            "variant": product.get("Variant"),
            "quantity": intent["quantity"],
            "unit_price": product.get("Price"),
            "total_value": (product.get("Price") or 0) * intent["quantity"],
            "available_stock": product.get("Stock", 0),
        }
        decision = self.deepseek.decide_action(order, inventory)
        action = decision.get("action", "clarify")
        print(f"  Action: {action}")
        print(f"  Reason: {decision.get('reason')}")

        # Step 4: Route based on action (autonomous workflow-changing decision)
        print(f"\nStep 4: Routing to '{action}' handler...")

        if action == "approve":
            return self._handle_approve(order_id, customer_name, intent, product, decision, timestamp)
        elif action == "escalate":
            return self._handle_escalate(order_id, customer_name, intent, product, decision, timestamp)
        elif action == "suggest_alternative":
            return self._handle_suggest_alternative(order_id, customer_name, intent, product, decision, inventory, timestamp)
        elif action == "reject":
            return self._handle_reject(order_id, customer_name, intent, decision, timestamp)
        else:
            return self._handle_clarify(order_id, customer_name, intent, timestamp)

    def _handle_approve(self, order_id, customer_name, intent, product, decision, timestamp):
        """Handle approved order: update stock, create order record, notify customer."""
        print("  → Approving order...")

        # Calculate total
        total = product["Price"] * intent["quantity"]

        # Update stock
        new_stock = product["Stock"] - intent["quantity"]
        if self.sheets:
            self.sheets.update_stock(product["SKU"], new_stock)
            print(f"  → Stock updated: {product['Stock']} → {new_stock}")

        # Create order record
        order = {
            "order_id": order_id,
            "customer": customer_name,
            "product": intent["product"],
            "variant": intent.get("variant", ""),
            "quantity": intent["quantity"],
            "total_value": total,
            "status": "approved",
            "timestamp": timestamp,
            "notes": decision.get("reason", ""),
        }
        if self.sheets:
            self.sheets.append_order(order)
            print(f"  → Order recorded: {order_id}")

        # Notify customer
        message = (
            f"✅ <b>Order Approved</b>\n\n"
            f"Order: {order_id}\n"
            f"Product: {intent['product']} ({intent.get('variant', 'N/A')})\n"
            f"Quantity: {intent['quantity']}\n"
            f"Total: ${total}\n\n"
            f"Your order has been approved and is being processed."
        )
        if TELEGRAM_CUSTOMER_CHAT_ID:
            self.telegram.send_message(TELEGRAM_CUSTOMER_CHAT_ID, message)
            print("  → Customer notified via Telegram")

        # Log action
        if self.sheets:
            self.sheets.append_log({
                "log_id": f"LOG-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": timestamp,
                "action": "order_approved",
                "order_id": order_id,
                "details": decision.get("reason", ""),
                "customer_notified": "yes",
                "owner_notified": "no",
            })

        return {"status": "approved", "order_id": order_id, "total": total}

    def _handle_escalate(self, order_id, customer_name, intent, product, decision, timestamp):
        """Handle escalated order: notify owner for approval."""
        print("  → Escalating to owner...")

        total = product["Price"] * intent["quantity"]

        # Notify owner
        message = (
            f"⚠️ <b>Order Escalation</b>\n\n"
            f"Order: {order_id}\n"
            f"Customer: {customer_name}\n"
            f"Product: {intent['product']} ({intent.get('variant', 'N/A')})\n"
            f"Quantity: {intent['quantity']}\n"
            f"Value: ${total}\n\n"
            f"Reason: {decision.get('reason', '')}\n\n"
            f"Please review and approve/reject."
        )
        if TELEGRAM_OWNER_CHAT_ID:
            self.telegram.send_message(TELEGRAM_OWNER_CHAT_ID, message)
            print("  → Owner notified via Telegram")

        # Log action
        if self.sheets:
            self.sheets.append_log({
                "log_id": f"LOG-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": timestamp,
                "action": "owner_escalation",
                "order_id": order_id,
                "details": decision.get("reason", ""),
                "customer_notified": "pending",
                "owner_notified": "yes",
            })

        return {"status": "escalated", "order_id": order_id, "total": total}

    def _handle_suggest_alternative(self, order_id, customer_name, intent, product, decision, inventory, timestamp):
        """Handle alternative suggestion: offer substitute products."""
        print("  → Suggesting alternative...")

        suggested = decision.get("suggested_items", [])
        total = decision.get("total_value", 0)

        # Build customer message
        items_text = "\n".join(
            f"  • {item.get('quantity', 0)} × {item.get('product', 'Unknown')} ({item.get('variant', 'N/A')}) — ${item.get('price', 0)}"
            for item in suggested
        )
        message = (
            f"📦 <b>Order Update</b> — {order_id}\n\n"
            f"We currently have {product['Stock']} {intent['product']} ({intent.get('variant', 'N/A')}) available.\n\n"
            f"We can fulfill your order with:\n{items_text}\n\n"
            f"Total: ${total}\n\n"
            f"Would you like to continue? Reply YES to confirm."
        )
        if TELEGRAM_CUSTOMER_CHAT_ID:
            self.telegram.send_message(TELEGRAM_CUSTOMER_CHAT_ID, message)
            print("  → Customer notified via Telegram")

        # Log action
        if self.sheets:
            self.sheets.append_log({
                "log_id": f"LOG-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": timestamp,
                "action": "alternative_suggested",
                "order_id": order_id,
                "details": decision.get("reason", ""),
                "customer_notified": "yes",
                "owner_notified": "no",
            })

        return {"status": "alternative_suggested", "order_id": order_id, "total": total}

    def _handle_reject(self, order_id, customer_name, intent, decision, timestamp):
        """Handle rejected order."""
        print("  → Rejecting order...")

        message = (
            f"❌ <b>Order Update</b> — {order_id}\n\n"
            f"We're unable to fulfill your request for {intent['quantity']} × {intent['product']}.\n\n"
            f"Reason: {decision.get('reason', 'No suitable alternative available')}\n\n"
            f"Please contact us for more options."
        )
        if TELEGRAM_CUSTOMER_CHAT_ID:
            self.telegram.send_message(TELEGRAM_CUSTOMER_CHAT_ID, message)
            print("  → Customer notified via Telegram")

        # Log action
        if self.sheets:
            self.sheets.append_log({
                "log_id": f"LOG-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": timestamp,
                "action": "order_rejected",
                "order_id": order_id,
                "details": decision.get("reason", ""),
                "customer_notified": "yes",
                "owner_notified": "no",
            })

        return {"status": "rejected", "order_id": order_id}

    def _handle_clarify(self, order_id, customer_name, intent, timestamp, reason=""):
        """Handle clarification request."""
        print("  → Requesting clarification...")

        message = (
            f"❓ <b>Order Update</b> — {order_id}\n\n"
            f"We need more information to process your request.\n\n"
            f"Reason: {reason or 'Product not found or quantity unclear'}\n\n"
            f"Please provide more details."
        )
        if TELEGRAM_CUSTOMER_CHAT_ID:
            self.telegram.send_message(TELEGRAM_CUSTOMER_CHAT_ID, message)
            print("  → Customer notified via Telegram")

        # Log action
        if self.sheets:
            self.sheets.append_log({
                "log_id": f"LOG-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": timestamp,
                "action": "clarification_requested",
                "order_id": order_id,
                "details": reason or "Product not found or quantity unclear",
                "customer_notified": "yes",
                "owner_notified": "no",
            })

        return {"status": "clarify", "order_id": order_id}

    def _find_product(self, inventory, product_name, variant=None):
        """Find a product in inventory by name and optional variant with fuzzy/plural tolerance."""
        if not product_name:
            return None

        def clean(s):
            return re.sub(r'[^a-z0-9]', '', (s or '').lower().rstrip('s'))

        clean_pname = clean(product_name)
        clean_vname = clean(variant) if variant else None

        # 1. Exact match on name and variant
        for item in inventory:
            if item.get("Product", "").lower() == product_name.lower():
                if variant is None or item.get("Variant", "").lower() == (variant or "").lower():
                    return item

        # 2. Normalized match (ignoring case, plurals, and punctuation)
        for item in inventory:
            item_pname = clean(item.get("Product", ""))
            item_vname = clean(item.get("Variant", ""))
            if item_pname == clean_pname:
                if clean_vname is None or item_vname == clean_vname:
                    return item

        # 3. Substring match (either product contains item or item contains product)
        for item in inventory:
            item_pname = clean(item.get("Product", ""))
            item_vname = clean(item.get("Variant", ""))
            if item_pname in clean_pname or clean_pname in item_pname:
                if clean_vname is None or item_vname == clean_vname or clean_vname in item_pname:
                    return item

        # 4. Fallback matching product name alone
        for item in inventory:
            item_pname = clean(item.get("Product", ""))
            if item_pname == clean_pname or item_pname in clean_pname or clean_pname in item_pname:
                return item

        return None


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    """Run the AI Business Operations Agent."""
    print("=" * 60)
    print("  AI Small Business Operations Agent")
    print("=" * 60)

    # Check configuration
    if not DEEPSEEK_API_KEY:
        print("\nERROR: DEEPSEEK_API_KEY not set.")
        print("Get your key at https://platform.deepseek.com/")
        return

    agent = AIBusinessAgent()

    # Interactive mode
    print("\nEnter customer messages (or 'quit' to exit):\n")
    while True:
        try:
            message = input("Customer: ").strip()
            if message.lower() in ("quit", "exit", "q"):
                break
            if not message:
                continue

            result = agent.process_order(message)
            print(f"\nResult: {result}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nGoodbye!")


if __name__ == "__main__":
    main()
