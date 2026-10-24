"""
Stemations - Single Command Launcher
Starts the FastAPI application server serving both backend APIs and the modern frontend.
"""
import sys
from pathlib import Path
import uvicorn

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    print("=================================================================")
    print("STEMATIONS: Autonomous STEM Video Agent")
    print("Serving modern web application at: http://localhost:8000")
    print("Interactive API documentation at: http://localhost:8000/docs")
    print("=================================================================")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
