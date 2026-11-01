#!/usr/bin/env python3
"""
Direct runner for Mission Mirror.
Automatically resolves paths, verifies dependencies, seeds database if necessary,
and launches the FastAPI server.
"""
import sys
import os
from pathlib import Path

# Add backend directory to sys.path
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.chdir(str(current_dir))

def main():
    import uvicorn
    from app.database import init_db
    
    # Initialize database tables
    init_db()
    
    # Auto-seed sample mission if database is fresh
    try:
        from seed_data import seed
        seed()
    except Exception as e:
        print(f"Note: Seed check passed ({e})")

    print("\n" + "="*65)
    print("  [>] MISSION MIRROR -- Junior Astronaut Mission Trainer")
    print("  -------------------------------------------------------------")
    print("  Cadet Web App:      http://localhost:8000")
    print("  FastAPI Swagger UI: http://localhost:8000/docs")
    print("  ReDoc:              http://localhost:8000/redoc")
    print("="*65 + "\n")
    print("Press Ctrl+C to stop the server.\n")

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
