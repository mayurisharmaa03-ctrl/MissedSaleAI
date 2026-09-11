"""
Top-level runner for MissedSale AI.
Allows running the platform directly from the repository root:
    python run.py
"""

import os
import sys
from pathlib import Path

# Add MissedSaleAI to sys.path and remove root directory to prevent namespace collisions
ROOT_DIR = str(Path(__file__).resolve().parent)
PROJECT_DIR = Path(__file__).resolve().parent / "MissedSaleAI"
sys.argv[0] = str(Path(__file__).resolve())
while ROOT_DIR in sys.path:
    sys.path.remove(ROOT_DIR)
sys.path.insert(0, str(PROJECT_DIR))
os.chdir(str(PROJECT_DIR))

from app import create_app
from config import Config

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n=======================================================")
    print(f"  MissedSale AI – Intelligent Lost-Sales Recovery")
    print(f"  Running on: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG, use_reloader=False)
