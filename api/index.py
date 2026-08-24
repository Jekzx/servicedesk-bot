"""Vercel Serverless Function Entry Point."""
import os
import sys
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Set VERCEL environment flag if not present
os.environ.setdefault("VERCEL", "1")

from app.main import app

# Vercel ASGI entrypoint
# app is the FastAPI instance
