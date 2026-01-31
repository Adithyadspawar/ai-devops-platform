import sentry_sdk
import os
import sys

# Get DSN from env
DSN = os.environ.get("SENTRY_DSN")

print(f"1. Checking DSN...")
print(f"   DSN Found: {DSN}")

if not DSN:
    print("❌ ERROR: SENTRY_DSN is not set in environment variables!")
    sys.exit(1)

print("\n2. Initializing Sentry SDK...")
try:
    sentry_sdk.init(dsn=DSN, debug=True)
    print("   ✅ Initialization successful")
except Exception as e:
    print(f"❌ ERROR: Failed to init Sentry: {e}")
    sys.exit(1)

print("\n3. Sending Test Message...")
try:
    event_id = sentry_sdk.capture_message("Manual Connection Test from Docker")
    print(f"   ✅ Message captured. Event ID: {event_id}")
    print("   (This implies the SDK accepted it, but check logs for transmission success)")
except Exception as e:
    print(f"❌ ERROR: Failed to capture message: {e}")

print("\n4. Forcing Flush (Sending data to cloud)...")
try:
    # Flush events to network
    sentry_sdk.flush(timeout=5.0)
    print("   ✅ Flush complete. If no errors appeared above, it was sent.")
except Exception as e:
    print(f"❌ ERROR during flush (Network Issue?): {e}")

print("\nDONE. Please check your Sentry Dashboard for specific message: 'Manual Connection Test from Docker'")
