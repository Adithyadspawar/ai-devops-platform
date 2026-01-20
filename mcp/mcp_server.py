# mcp/mcp_server.py
"""
MCP Webhook Server - Receives Sentry alerts and generates AI fixes
This is a FREE alternative to paid Cursor/Seer services.

Run with: uvicorn mcp.mcp_server:app --port 5000 --reload
"""

from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
import subprocess
from datetime import datetime

app = FastAPI(title="MCP AI Debugging Server")

# Store for received issues (in production, use a database)
issues_store: List[Dict] = []


class SentryWebhook(BaseModel):
    """Sentry webhook payload structure"""
    action: str
    data: Dict[str, Any]
    actor: Optional[Dict] = None


class AIFixResponse(BaseModel):
    """Response from AI fix generation"""
    issue_id: str
    status: str
    analysis: str
    suggested_fix: Optional[Dict] = None
    pr_url: Optional[str] = None


def analyze_error(error_type: str, error_message: str, stacktrace: str) -> Dict:
    """
    AI-powered error analysis (simulated for free version).
    In production, this would call OpenAI/Anthropic API or local LLM.
    """
    
    # Knowledge base of common fixes
    fix_database = {
        "ZeroDivisionError": {
            "analysis": "Division by zero detected. The code attempts to divide a number by zero.",
            "fix": "Add a check before division: `if divisor != 0:` or use try-except block.",
            "patch": """
-    result = numerator / divisor
+    if divisor != 0:
+        result = numerator / divisor
+    else:
+        result = 0  # or raise custom exception
"""
        },
        "AttributeError": {
            "analysis": "Attempting to access an attribute on a None object (NullPointerException equivalent).",
            "fix": "Add null check before accessing the attribute: `if obj is not None:`",
            "patch": """
-    return {"username": user.name}
+    if user is not None:
+        return {"username": user.name}
+    else:
+        return {"username": "Unknown"}
"""
        },
        "KeyError": {
            "analysis": "Attempting to access a dictionary key that doesn't exist.",
            "fix": "Use .get() method with default value: `dict.get('key', default_value)`",
            "patch": """
-    return {"email": api_response["email"]}
+    return {"email": api_response.get("email", "not_provided@example.com")}
"""
        },
        "ConnectionError": {
            "analysis": "Database or external service connection failed.",
            "fix": "Add retry logic with exponential backoff and connection pooling.",
            "patch": """
+import time
+from functools import wraps
+
+def retry_connection(max_retries=3, delay=1):
+    def decorator(func):
+        @wraps(func)
+        def wrapper(*args, **kwargs):
+            for attempt in range(max_retries):
+                try:
+                    return func(*args, **kwargs)
+                except ConnectionError:
+                    if attempt < max_retries - 1:
+                        time.sleep(delay * (2 ** attempt))
+            raise ConnectionError("Max retries exceeded")
+        return wrapper
+    return decorator
"""
        },
        "TimeoutError": {
            "analysis": "External service request timed out.",
            "fix": "Implement circuit breaker pattern and async requests with timeout handling.",
            "patch": """
+import asyncio
+
+async def call_with_timeout(func, timeout=10):
+    try:
+        return await asyncio.wait_for(func(), timeout=timeout)
+    except asyncio.TimeoutError:
+        return {"error": "Service temporarily unavailable"}
"""
        },
        "ValueError": {
            "analysis": "Invalid value passed to function (e.g., converting non-numeric string to number).",
            "fix": "Add input validation before processing.",
            "patch": """
-    total = float(price) * 1.18
+    try:
+        total = float(price) * 1.18
+    except ValueError:
+        total = 0.0
+        # Log the error for debugging
"""
        },
        "PermissionError": {
            "analysis": "Unauthorized access attempt detected.",
            "fix": "Implement proper authentication middleware and role-based access control.",
            "patch": """
+from functools import wraps
+
+def require_permission(permission):
+    def decorator(func):
+        @wraps(func)
+        def wrapper(user, *args, **kwargs):
+            if permission in user.permissions:
+                return func(user, *args, **kwargs)
+            raise HTTPException(403, "Access denied")
+        return wrapper
+    return decorator
"""
        },
        "FileNotFoundError": {
            "analysis": "Attempting to read a file that doesn't exist.",
            "fix": "Add file existence check and provide fallback configuration.",
            "patch": """
+import os
+
-    with open("/etc/app/missing-config.yaml", "r") as f:
-        return {"config": f.read()}
+    config_path = "/etc/app/missing-config.yaml"
+    if os.path.exists(config_path):
+        with open(config_path, "r") as f:
+            return {"config": f.read()}
+    else:
+        return {"config": "default_configuration"}
"""
        }
    }
    
    # Find matching fix
    for error_key, fix_info in fix_database.items():
        if error_key.lower() in error_type.lower():
            return {
                "error_type": error_type,
                "analysis": fix_info["analysis"],
                "suggested_fix": fix_info["fix"],
                "patch": fix_info["patch"],
                "confidence": 0.85
            }
    
    # Default response for unknown errors
    return {
        "error_type": error_type,
        "analysis": f"Unknown error type: {error_type}. Manual investigation required.",
        "suggested_fix": "Review the stacktrace and add appropriate error handling.",
        "patch": None,
        "confidence": 0.3
    }


def create_github_pr(issue_id: str, fix_info: Dict) -> Optional[str]:
    """
    Creates a GitHub PR with the suggested fix.
    Uses GitHub CLI (gh) if available, otherwise returns instructions.
    """
    # In a real setup, this would use the GitHub API
    # For demo purposes, we'll create a branch and PR instructions
    
    branch_name = f"fix/sentry-issue-{issue_id}"
    
    return {
        "branch_name": branch_name,
        "pr_title": f"[Auto-Fix] {fix_info.get('error_type', 'Unknown Error')}",
        "pr_body": f"""
## 🤖 AI-Generated Fix

**Issue ID:** {issue_id}

### Analysis
{fix_info.get('analysis', 'No analysis available')}

### Suggested Fix
{fix_info.get('suggested_fix', 'No fix suggested')}

### Patch
```diff
{fix_info.get('patch', 'No patch available')}
```

---
*This PR was automatically generated by the MCP AI Debugging System.*
""",
        "instructions": f"""
To apply this fix manually:
1. git checkout -b {branch_name}
2. Apply the patch above to the relevant file
3. git commit -m "fix: {fix_info.get('error_type', 'error')}"
4. git push origin {branch_name}
5. Create PR on GitHub
"""
    }


@app.get("/")
def root():
    return {
        "service": "MCP AI Debugging Server",
        "status": "running",
        "endpoints": {
            "/webhook/sentry": "Receive Sentry alerts",
            "/issues": "List all received issues",
            "/analyze/{issue_id}": "Get AI analysis for an issue",
            "/fix/{issue_id}": "Generate fix and PR"
        }
    }


@app.post("/webhook/sentry")
async def receive_sentry_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receives webhooks from Sentry when an error occurs.
    Configure in Sentry: Settings > Integrations > Webhooks
    """
    try:
        payload = await request.json()
    except:
        payload = {"raw": await request.body()}
    
    issue = {
        "id": f"issue-{len(issues_store) + 1}",
        "received_at": datetime.now().isoformat(),
        "payload": payload,
        "status": "received"
    }
    
    issues_store.append(issue)
    
    print(f"📥 Received Sentry webhook - Issue ID: {issue['id']}")
    
    # Process in background
    background_tasks.add_task(process_issue, issue)
    
    return {"status": "received", "issue_id": issue["id"]}


async def process_issue(issue: Dict):
    """Background task to process an issue"""
    print(f"🔍 Processing issue: {issue['id']}")
    
    # Extract error info from payload
    payload = issue.get("payload", {})
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    
    error_type = data.get("error", {}).get("type", "UnknownError") if isinstance(data, dict) else "UnknownError"
    
    # Generate AI fix
    fix_info = analyze_error(error_type, "", "")
    issue["ai_analysis"] = fix_info
    issue["status"] = "analyzed"
    
    print(f"✅ Issue {issue['id']} analyzed. Fix confidence: {fix_info.get('confidence', 0)}")


@app.get("/issues")
def list_issues():
    """List all received issues"""
    return {
        "total": len(issues_store),
        "issues": issues_store
    }


@app.get("/issues/{issue_id}")
def get_issue(issue_id: str):
    """Get details of a specific issue"""
    for issue in issues_store:
        if issue["id"] == issue_id:
            return issue
    return {"error": "Issue not found"}


@app.post("/analyze")
async def analyze_manual(request: Request):
    """
    Manually submit an error for analysis.
    Useful for testing without Sentry integration.
    """
    data = await request.json()
    
    error_type = data.get("error_type", "UnknownError")
    error_message = data.get("error_message", "")
    stacktrace = data.get("stacktrace", "")
    
    fix_info = analyze_error(error_type, error_message, stacktrace)
    
    # Create PR info
    pr_info = create_github_pr(f"manual-{len(issues_store)}", fix_info)
    
    return {
        "status": "success",
        "analysis": fix_info,
        "pr_info": pr_info
    }


@app.get("/test/{error_type}")
def test_analysis(error_type: str):
    """
    Quick test endpoint to see AI analysis for different error types.
    
    Example: /test/ZeroDivisionError
    """
    fix_info = analyze_error(error_type, "", "")
    pr_info = create_github_pr(f"test-{error_type}", fix_info)
    
    return {
        "error_type": error_type,
        "analysis": fix_info,
        "pr_info": pr_info
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
