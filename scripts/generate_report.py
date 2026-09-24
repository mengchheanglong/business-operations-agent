from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

output_path = r"C:\Users\User\Internship\business-operations-agent\docs\AI_Business_Operations_Agent_Report.pdf"
doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Title_Custom', fontSize=24, leading=30, alignment=TA_CENTER, spaceAfter=20, textColor=colors.HexColor('#1e40af')))
styles.add(ParagraphStyle(name='Heading1_Custom', fontSize=16, leading=20, spaceAfter=12, textColor=colors.HexColor('#1e40af')))
styles.add(ParagraphStyle(name='Heading2_Custom', fontSize=13, leading=16, spaceAfter=8, textColor=colors.HexColor('#374151')))
styles.add(ParagraphStyle(name='Body_Custom', fontSize=10, leading=14, spaceAfter=6))
styles.add(ParagraphStyle(name='Code_Custom', fontSize=9, leading=12, backColor=colors.HexColor('#f3f4f6'), borderPadding=6, spaceAfter=8))

story = []

story.append(Paragraph("AI Small Business Operations Agent", styles['Title_Custom']))
story.append(Paragraph("Assignment 2 - AI Agent Project", styles['Heading2_Custom']))
story.append(Spacer(1, 20))

story.append(Paragraph("1. Problem Statement", styles['Heading1_Custom']))
story.append(Paragraph(
    "Small businesses often manage customer orders, inventory, customer messages, and operational decisions "
    "<b>manually</b>. This causes delayed customer responses, stock mistakes and overselling, unnecessary manual "
    "work, and inconsistent decision-making. There is no affordable AI-powered solution that can automatically process "
    "orders, check inventory, make intelligent decisions, and notify both customers and business owners in real time.",
    styles['Body_Custom']
))
story.append(Spacer(1, 12))

story.append(Paragraph("2. Proposed AI Agent Solution", styles['Heading1_Custom']))
story.append(Paragraph(
    "An AI-powered operations agent that receives customer order requests, understands intent using Deepseek LLM, "
    "checks inventory in Google Sheets, makes intelligent decisions based on business rules, and notifies customers "
    "and the business owner via Telegram. The agent autonomously routes orders through 5 different paths based on "
    "context: approve, escalate, suggest alternative, clarify, or reject.",
    styles['Body_Custom']
))
story.append(Spacer(1, 12))

story.append(Paragraph("3. Workflow Diagram", styles['Heading1_Custom']))
story.append(Paragraph(
    "Customer sends order/request → AI extracts intent (Decision 1) → Check inventory in Google Sheets → "
    "AI decides action (Decisions 2 & 3) → Route based on action (autonomous workflow-changing decision) → "
    "Execute action (update sheets, send notifications) → Log the action → Return result",
    styles['Body_Custom']
))
story.append(Spacer(1, 8))

workflow_data = [
    ["Step", "Action", "Tool/Service"],
    ["1", "Receive customer message", "Webhook / CLI / Web"],
    ["2", "AI extracts order intent", "Deepseek LLM (Decision 1)"],
    ["3", "Check inventory", "Google Sheets API"],
    ["4", "AI decides action", "Deepseek LLM (Decisions 2 & 3)"],
    ["5", "Route based on action", "Autonomous routing (5 paths)"],
    ["6", "Update inventory & orders", "Google Sheets API"],
    ["7", "Notify customer", "Telegram Bot API"],
    ["8", "Notify owner (if escalated)", "Telegram Bot API"],
    ["9", "Log the action", "Google Sheets API"],
    ["10", "Return result", "Webhook response"],
]
workflow_table = Table(workflow_data, colWidths=[0.5*inch, 2.5*inch, 2.5*inch])
workflow_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('TOPPADDING', (0, 0), (-1, 0), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
]))
story.append(workflow_table)
story.append(Spacer(1, 12))

story.append(Paragraph("4. System Architecture", styles['Heading1_Custom']))
story.append(Paragraph(
    "The system consists of a Python application (agent.py) that orchestrates the workflow. It connects to "
    "three external services: Deepseek API for LLM reasoning, Google Sheets API for data storage, and "
    "Telegram Bot API for notifications. The agent can be run in CLI mode, web mode (Flask), or demo mode.",
    styles['Body_Custom']
))
story.append(Spacer(1, 8))

arch_data = [
    ["Component", "Technology", "Purpose"],
    ["Orchestration", "Python (agent.py)", "Workflow engine, routing, data flow"],
    ["LLM", "Deepseek (deepseek-chat)", "Intent extraction + decision making"],
    ["Database", "Google Sheets", "Products, Orders, Customers, Logs"],
    ["Notifications", "Telegram Bot API", "Customer + owner messaging"],
    ["Input", "CLI / Web / Webhook", "Customer order entry point"],
]
arch_table = Table(arch_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
arch_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('TOPPADDING', (0, 0), (-1, 0), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
]))
story.append(arch_table)
story.append(Spacer(1, 12))

story.append(Paragraph("5. AI Tools, Models, and External Services", styles['Heading1_Custom']))

tools_data = [
    ["Service", "Type", "Purpose"],
    ["Deepseek API", "LLM (deepseek-chat)", "Intent extraction, decision making, customer responses"],
    ["Google Sheets API", "External Tool", "Inventory management, order records, customer data, audit logs"],
    ["Telegram Bot API", "External Tool", "Real-time notifications to customers and business owner"],
    ["Python (agent.py)", "Framework", "Workflow orchestration, routing, data processing"],
    ["Flask (web_app.py)", "Web Framework", "Web interface for testing and demo"],
]
tools_table = Table(tools_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
tools_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('TOPPADDING', (0, 0), (-1, 0), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
]))
story.append(tools_table)
story.append(Spacer(1, 12))

story.append(Paragraph("6. AI Decision Points", styles['Heading1_Custom']))
story.append(Paragraph("<b>Decision 1 — Extract Order Intent:</b> The LLM parses the customer message to identify product, variant, quantity, and intent.", styles['Body_Custom']))
story.append(Paragraph("<b>Decision 2 — Can the order be fulfilled?</b> The LLM compares requested quantity against available stock.", styles['Body_Custom']))
story.append(Paragraph("<b>Decision 3 — What action should be taken?</b> The LLM applies business rules to select the best action.", styles['Body_Custom']))
story.append(Spacer(1, 8))

decision_data = [
    ["Decision", "Input", "Output"],
    ["1. Extract Intent", "Customer message", "Product, variant, quantity, intent"],
    ["2. Fulfillment Check", "Order + inventory", "Can/cannot fulfill"],
    ["3. Action Selection", "Rules + context", "approve / escalate / suggest / clarify / reject"],
]
decision_table = Table(decision_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
decision_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('TOPPADDING', (0, 0), (-1, 0), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
]))
story.append(decision_table)
story.append(Spacer(1, 12))

story.append(Paragraph("7. Autonomous Workflow-Changing Decision", styles['Heading1_Custom']))
story.append(Paragraph(
    "The agent autonomously selects one of 5 paths based on the AI decision. This is the workflow-changing "
    "decision that demonstrates the agent's autonomy:",
    styles['Body_Custom']
))
story.append(Paragraph("• <b>Approve:</b> Auto-fulfill order, update stock, notify customer", styles['Body_Custom']))
story.append(Paragraph("• <b>Escalate:</b> Notify owner for manual approval", styles['Body_Custom']))
story.append(Paragraph("• <b>Suggest Alternative:</b> Offer substitute products", styles['Body_Custom']))
story.append(Paragraph("• <b>Clarify:</b> Ask customer for more information", styles['Body_Custom']))
story.append(Paragraph("• <b>Reject:</b> Decline the order", styles['Body_Custom']))
story.append(Spacer(1, 12))

story.append(Paragraph("8. Sample Execution", styles['Heading1_Custom']))
story.append(Paragraph("<b>Input:</b> \"I want 2 black Basic Shirts\"", styles['Body_Custom']))
story.append(Paragraph("<b>Output:</b>", styles['Body_Custom']))
story.append(Paragraph(
    '{"status": "approved", "order_id": "ORD-2CED1883", "total": 20}',
    styles['Code_Custom']
))
story.append(Paragraph(
    "The agent extracted the intent (Basic Shirt, Black, qty 2), checked inventory (20 in stock), "
    "decided to auto-approve (total $20 < $100), updated stock (20→18), created an order record, "
    "notified the customer via Telegram, and logged the action.",
    styles['Body_Custom']
))
story.append(Spacer(1, 12))

story.append(Paragraph("9. Requirements Verification", styles['Heading1_Custom']))

req_data = [
    ["Requirement", "Status", "Evidence"],
    ["Defined real-world problem", "Met", "Small business order management"],
    ["LLM for reasoning/decisions", "Met", "Deepseek API (deepseek-chat)"],
    ["≥2 external tools/services", "Met", "Google Sheets API, Telegram Bot API"],
    ["≥5 workflow steps", "Met", "10 steps"],
    ["≥2 AI decision points", "Met", "3 decisions"],
    ["≥1 autonomous decision", "Met", "5-way routing"],
]
req_table = Table(req_data, colWidths=[2*inch, 0.8*inch, 3.2*inch])
req_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
    ('TOPPADDING', (0, 0), (-1, 0), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
]))
story.append(req_table)
story.append(Spacer(1, 12))

story.append(Paragraph("10. Project Link", styles['Heading1_Custom']))
story.append(Paragraph(
    "The project is a standalone Python application. The main agent is in <b>agent.py</b>. "
    "The web interface is in <b>web_app.py</b>. The demo script is <b>demo.py</b>. "
    "All configuration is in <b>.env</b>.",
    styles['Body_Custom']
))
story.append(Spacer(1, 8))
story.append(Paragraph("<b>How to run:</b>", styles['Body_Custom']))
story.append(Paragraph("python agent.py &nbsp;&nbsp;&nbsp;&nbsp;# Interactive CLI mode", styles['Code_Custom']))
story.append(Paragraph("python web_app.py &nbsp;&nbsp;&nbsp;&nbsp;# Web interface (http://localhost:5000)", styles['Code_Custom']))
story.append(Paragraph("python demo.py &nbsp;&nbsp;&nbsp;&nbsp;# Run all test scenarios", styles['Code_Custom']))

doc.build(story)
print(f"PDF report created: {output_path}")
