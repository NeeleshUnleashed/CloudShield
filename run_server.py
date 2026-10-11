"""
CloudShield Local Server Runner
Usage:
  python run_server.py
"""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"==================================================")
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"AWS_MODE: {settings.AWS_MODE} (Strict Zero-Charge Local Mode)")
    print(f"Open Dashboard: http://127.0.0.1:8000")
    print(f"Interactive API Docs: http://127.0.0.1:8000/docs")
    print(f"==================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
