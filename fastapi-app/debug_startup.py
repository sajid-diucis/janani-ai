import sys
import traceback

print("Attempting to import main...")
try:
    from main import app
    print("SUCCESS: main imported successfully.")
except Exception:
    traceback.print_exc()
except ImportError:
    traceback.print_exc()
