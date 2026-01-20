#!/usr/bin/env python3
"""
MCP Demo Script - Demonstrates the full AI debugging workflow
Run this to see how errors are analyzed and fixes are generated

Usage: python mcp/mcp_demo.py
"""

import requests
import json
import time

MCP_SERVER = "http://localhost:5000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def demo_health_check():
    """Check if MCP server is running"""
    print_section("1. MCP Server Health Check")
    
    try:
        resp = requests.get(f"{MCP_SERVER}/", timeout=5)
        print("✅ MCP Server is running!")
        print(json.dumps(resp.json(), indent=2))
        return True
    except requests.ConnectionError:
        print("❌ MCP Server is not running!")
        print("   Start it with: uvicorn mcp.mcp_server:app --port 5000")
        return False

def demo_analyze_errors():
    """Demonstrate AI analysis of different error types"""
    print_section("2. AI Error Analysis Demo")
    
    error_types = [
        "ZeroDivisionError",
        "AttributeError",
        "KeyError",
        "ConnectionError",
        "TimeoutError",
        "ValueError",
        "PermissionError",
        "FileNotFoundError"
    ]
    
    for error_type in error_types:
        print(f"\n📍 Analyzing: {error_type}")
        print("-" * 40)
        
        resp = requests.get(f"{MCP_SERVER}/test/{error_type}")
        data = resp.json()
        
        analysis = data.get("analysis", {})
        print(f"   Analysis: {analysis.get('analysis', 'N/A')}")
        print(f"   Fix: {analysis.get('suggested_fix', 'N/A')}")
        print(f"   Confidence: {analysis.get('confidence', 0) * 100:.0f}%")
        
        time.sleep(0.2)  # Small delay for readability

def demo_manual_submission():
    """Submit an error manually for analysis"""
    print_section("3. Manual Error Submission")
    
    # Simulate a real error from your app
    error_payload = {
        "error_type": "AttributeError",
        "error_message": "'NoneType' object has no attribute 'name'",
        "stacktrace": """
Traceback (most recent call last):
  File "/app/main.py", line 85, in simulate_null_pointer
    return {"username": user.name}
AttributeError: 'NoneType' object has no attribute 'name'
        """
    }
    
    print("📤 Submitting error for analysis...")
    print(f"   Error: {error_payload['error_type']}")
    
    resp = requests.post(f"{MCP_SERVER}/analyze", json=error_payload)
    data = resp.json()
    
    print("\n📥 AI Response:")
    print(json.dumps(data, indent=2))

def demo_webhook_simulation():
    """Simulate a Sentry webhook"""
    print_section("4. Sentry Webhook Simulation")
    
    # This simulates what Sentry would send
    webhook_payload = {
        "action": "created",
        "data": {
            "event": {
                "event_id": "abc123",
                "project": "mini-orders-api",
                "timestamp": "2024-01-20T12:00:00Z"
            },
            "error": {
                "type": "ZeroDivisionError",
                "value": "division by zero",
                "mechanism": {
                    "type": "generic",
                    "handled": False
                }
            },
            "contexts": {
                "runtime": {
                    "name": "Python",
                    "version": "3.11"
                }
            }
        },
        "actor": {
            "type": "application",
            "id": "sentry-webhook"
        }
    }
    
    print("📤 Sending simulated Sentry webhook...")
    
    resp = requests.post(f"{MCP_SERVER}/webhook/sentry", json=webhook_payload)
    data = resp.json()
    
    print(f"   Response: {data}")
    
    # Wait a moment for background processing
    time.sleep(1)
    
    # Check the issues list
    print("\n📋 Checking received issues...")
    resp = requests.get(f"{MCP_SERVER}/issues")
    issues = resp.json()
    
    print(f"   Total issues received: {issues['total']}")
    
    if issues['total'] > 0:
        latest_issue = issues['issues'][-1]
        print(f"   Latest issue ID: {latest_issue['id']}")
        print(f"   Status: {latest_issue.get('status', 'unknown')}")

def demo_pr_preview():
    """Show what an auto-generated PR would look like"""
    print_section("5. Auto-PR Preview")
    
    resp = requests.get(f"{MCP_SERVER}/test/ZeroDivisionError")
    data = resp.json()
    
    pr_info = data.get("pr_info", {})
    
    print("📝 Auto-Generated PR:")
    print(f"   Branch: {pr_info.get('branch_name', 'N/A')}")
    print(f"   Title: {pr_info.get('pr_title', 'N/A')}")
    print("\n   PR Body Preview:")
    print("   " + "-" * 50)
    
    body = pr_info.get("pr_body", "")
    for line in body.split("\n")[:15]:  # First 15 lines
        print(f"   {line}")
    print("   ...")

def run_full_demo():
    """Run the complete demo"""
    print("\n" + "🤖" * 30)
    print("\n   MCP AI DEBUGGING SYSTEM - DEMO")
    print("\n" + "🤖" * 30)
    
    if not demo_health_check():
        return
    
    demo_analyze_errors()
    demo_manual_submission()
    demo_webhook_simulation()
    demo_pr_preview()
    
    print_section("DEMO COMPLETE")
    print("✅ The MCP AI Debugging System is fully functional!")
    print("\n🎯 Next Steps:")
    print("   1. Configure Sentry webhook to point to /webhook/sentry")
    print("   2. Trigger errors in your app")
    print("   3. Watch AI generate fixes automatically!")
    print("\n🔗 For real AI integration, set up:")
    print("   - OpenAI API key for smarter analysis")
    print("   - GitHub token for actual PR creation")

if __name__ == "__main__":
    run_full_demo()
