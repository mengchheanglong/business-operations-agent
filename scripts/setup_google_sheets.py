"""
Google Sheets Setup Script for AI Business Operations Agent
Creates the required sheets and sample data.
Requires: pip install gspread google-auth
"""

import json
import os
import sys
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("Installing required packages...")
    os.system("pip install gspread google-auth")
    import gspread
    from google.oauth2.service_account import Credentials

# Google Sheets API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_credentials():
    """Load credentials from service account file."""
    cred_file = os.path.join(os.path.dirname(__file__), "credentials.json")
    if not os.path.exists(cred_file):
        print(f"ERROR: {cred_file} not found.")
        print("Download your service account key from Google Cloud Console.")
        print("Save it as 'credentials.json' in the scripts/ folder.")
        sys.exit(1)
    return Credentials.from_service_account_file(cred_file, scopes=SCOPES)

def setup_sheets(spreadsheet_id):
    """Create all required sheets with headers and sample data."""
    client = gspread.authorize(get_credentials())
    spreadsheet = client.open_by_key(spreadsheet_id)

    # Sheet 1: Products
    products = [
        ["SKU", "Product", "Variant", "Price", "Stock", "Low_Stock_Threshold"],
        ["SH-BLK-B", "Basic Shirt", "Black", 10, 20, 5],
        ["SH-WHT-B", "Basic Shirt", "White", 10, 18, 5],
        ["SH-BLK-P", "Premium Shirt", "Black", 18, 5, 2],
        ["SH-WHT-P", "Premium Shirt", "White", 18, 8, 2],
        ["SH-RED-B", "Basic Shirt", "Red", 10, 15, 5],
    ]

    # Sheet 2: Orders
    orders = [
        ["Order_ID", "Customer", "Product", "Variant", "Quantity", "Total_Value", "Status", "Timestamp", "Notes"],
        ["ORD-001", "John Doe", "Basic Shirt", "Black", 2, 20, "approved", "2026-09-20T10:00:00Z", "Auto-approved"],
        ["ORD-002", "Jane Smith", "Premium Shirt", "Black", 5, 90, "pending", "2026-09-20T10:05:00Z", "Owner approval required"],
    ]

    # Sheet 3: Customers
    customers = [
        ["Customer_ID", "Name", "Phone", "Telegram_Chat_ID", "Notes"],
        ["CUST-001", "John Doe", "+855-12-345-678", "123456789", "Regular customer"],
        ["CUST-002", "Jane Smith", "+855-98-765-432", "987654321", "New customer"],
    ]

    # Sheet 4: Logs
    logs = [
        ["Log_ID", "Timestamp", "Action", "Order_ID", "Details", "Customer_Notified", "Owner_Notified"],
        ["LOG-001", "2026-09-20T10:00:00Z", "order_approved", "ORD-001", "Stock sufficient, value < $100", "yes", "no"],
        ["LOG-002", "2026-09-20T10:05:00Z", "owner_escalation", "ORD-002", "High value order ($90)", "pending", "yes"],
        ["LOG-003", "2026-09-20T10:10:00Z", "alternative_suggested", "ORD-003", "Insufficient stock, offered white variant", "yes", "no"],
        ["LOG-004", "2026-09-20T10:15:00Z", "clarification_requested", "ORD-004", "Product not found in inventory", "yes", "no"],
        ["LOG-005", "2026-09-20T10:20:00Z", "order_rejected", "ORD-005", "No suitable alternative available", "yes", "no"],
    ]

    # Sheet 5: Business Rules
    rules = [
        ["Rule_ID", "Rule_Name", "Condition", "Action", "Priority"],
        ["R001", "Auto-approve low value", "total_value < $100 AND stock >= quantity", "approve", 1],
        ["R002", "Escalate high value", "total_value >= $100", "escalate", 2],
        ["R003", "Suggest alternative", "stock < quantity AND alternative exists", "suggest_alternative", 3],
        ["R004", "Clarify unknown product", "product not found", "clarify", 4],
        ["R005", "Reject no alternative", "no suitable product", "reject", 5],
    ]

    sheets_data = {
        "Products": products,
        "Orders": orders,
        "Customers": customers,
        "Logs": logs,
        "Business Rules": rules,
    }

    for sheet_name, data in sheets_data.items():
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            print(f"  Sheet '{sheet_name}' already exists, updating...")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)
            print(f"  Created sheet '{sheet_name}'")

        worksheet.clear()
        worksheet.update(data)
        print(f"    ✓ {len(data)} rows written")

    print(f"\n✅ All sheets configured successfully!")
    print(f"📊 Spreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

if __name__ == "__main__":
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        sheet_id = input("Enter your Google Sheet ID: ").strip()
    setup_sheets(sheet_id)
