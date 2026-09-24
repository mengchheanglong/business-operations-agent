"""
Demo script for AI Small Business Operations Agent.
Runs a complete end-to-end test with sample customer messages.
"""

import os
import sys
import json
from datetime import datetime, timezone

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import AIBusinessAgent


def run_demo():
    """Run a complete demo of the AI agent."""
    print("=" * 70)
    print("  AI SMALL BUSINESS OPERATIONS AGENT - DEMO")
    print("=" * 70)

    # Check configuration
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("\nERROR: DEEPSEEK_API_KEY not set.")
        print("Get your key at https://platform.deepseek.com/")
        return

    agent = AIBusinessAgent()

    # Demo scenarios
    scenarios = [
        {
            "name": "Scenario 1: Normal order (auto-approve)",
            "message": "I want 2 black Basic Shirts",
            "customer": "John Doe",
        },
        {
            "name": "Scenario 2: Large order (escalate to owner)",
            "message": "I need 12 black Basic Shirts",
            "customer": "Jane Smith",
        },
        {
            "name": "Scenario 3: Insufficient stock (suggest alternative)",
            "message": "I want 25 black Basic Shirts",
            "customer": "Bob Wilson",
        },
        {
            "name": "Scenario 4: Unknown product (clarify)",
            "message": "Do you have blue jeans?",
            "customer": "Alice Brown",
        },
    ]

    results = []
    for scenario in scenarios:
        print(f"\n{'-' * 70}")
        print(f"  {scenario['name']}")
        print(f"{'-' * 70}")

        result = agent.process_order(scenario["message"], scenario["customer"])
        results.append({
            "scenario": scenario["name"],
            "message": scenario["message"],
            "result": result,
        })

    # Summary
    print(f"\n{'=' * 70}")
    print("  DEMO SUMMARY")
    print(f"{'=' * 70}")
    for r in results:
        print(f"\n  {r['scenario']}")
        print(f"    Input: {r['message']}")
        print(f"    Output: {r['result']}")

    # Save results to file
    output_file = os.path.join(os.path.dirname(__file__), "demo", "demo-results.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {output_file}")


if __name__ == "__main__":
    run_demo()
