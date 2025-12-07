import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

print("Registered Routes:")
for route in app.routes:
    if hasattr(route, "path"):
        print(f" - {route.path} [{','.join(route.methods)}]")
