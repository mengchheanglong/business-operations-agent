# Google Sheets Structure

## Sheet 1: Products

| SKU | Product | Variant | Price | Stock | Low_Stock_Threshold |
|-----|---------|---------|-------|-------|---------------------|
| SH-BLK-B | Basic Shirt | Black | 10 | 20 | 5 |
| SH-WHT-B | Basic Shirt | White | 10 | 18 | 5 |
| SH-BLK-P | Premium Shirt | Black | 18 | 5 | 2 |
| SH-WHT-P | Premium Shirt | White | 18 | 8 | 2 |
| SH-RED-B | Basic Shirt | Red | 10 | 15 | 5 |

## Sheet 2: Orders

| Order_ID | Customer | Product | Variant | Quantity | Total_Value | Status | Timestamp | Notes |
|----------|----------|---------|---------|----------|-------------|--------|-----------|-------|
| ORD-001 | John Doe | Basic Shirt | Black | 2 | 20 | approved | 2026-09-20T10:00:00Z | Auto-approved |
| ORD-002 | Jane Smith | Premium Shirt | Black | 5 | 90 | pending | 2026-09-20T10:05:00Z | Owner approval required |

## Sheet 3: Customers

| Customer_ID | Name | Phone | Telegram_Chat_ID | Notes |
|-------------|------|-------|------------------|-------|
| CUST-001 | John Doe | +855-12-345-678 | 123456789 | Regular customer |
| CUST-002 | Jane Smith | +855-98-765-432 | 987654321 | New customer |

## Sheet 4: Logs

| Log_ID | Timestamp | Action | Order_ID | Details | Customer_Notified | Owner_Notified |
|--------|-----------|--------|----------|---------|-------------------|----------------|
| LOG-001 | 2026-09-20T10:00:00Z | order_approved | ORD-001 | Stock sufficient, value < $100 | yes | no |
| LOG-002 | 2026-09-20T10:05:00Z | owner_escalation | ORD-002 | High value order ($90) | pending | yes |
| LOG-003 | 2026-09-20T10:10:00Z | alternative_suggested | ORD-003 | Insufficient stock, offered white variant | yes | no |
| LOG-004 | 2026-09-20T10:15:00Z | clarification_requested | ORD-004 | Product not found in inventory | yes | no |
| LOG-005 | 2026-09-20T10:20:00Z | order_rejected | ORD-005 | No suitable alternative available | yes | no |

## Sheet 5: Business Rules (Optional - for reference)

| Rule_ID | Rule_Name | Condition | Action | Priority |
|---------|-----------|-----------|--------|----------|
| R001 | Auto-approve low value | total_value < $100 AND stock >= quantity | approve | 1 |
| R002 | Escalate high value | total_value >= $100 | escalate | 2 |
| R003 | Suggest alternative | stock < quantity AND alternative exists | suggest_alternative | 3 |
| R004 | Clarify unknown product | product not found | clarify | 4 |
| R005 | Reject no alternative | no suitable product | reject | 5 |
