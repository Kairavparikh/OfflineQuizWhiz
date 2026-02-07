#!/usr/bin/env python3
"""
Main entry point for the OfflineQuizWhiz API server.

Run this file to start the web server for MCQ generation.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import uvicorn
    from src.web.api import app

    print("\n" + "="*80)
    print("MCQ GENERATION API SERVER")
    print("="*80)
    print("\nStarting server...")
    print("  - Web UI: http://localhost:8000")
    print("  - API docs: http://localhost:8000/docs")
    print("  - API: http://localhost:8000/api")
    print("\nPress Ctrl+C to stop")
    print("="*80 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
