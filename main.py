"""Root entrypoint for Vercel FastAPI Framework Preset and local execution."""
import os
import sys
from pathlib import Path

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.main import app

# Expose app for Vercel FastAPI detector and ASGI servers
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
