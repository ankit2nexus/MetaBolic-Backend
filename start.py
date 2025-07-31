#!/usr/bin/env python3
"""
Simple startup script for Metabolical Backend API
Clean and easy-to-understand project structure
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the Metabolical Backend API server"""
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    app_dir = script_dir / "app"
    
    # Check if app directory exists
    if not app_dir.exists():
        print("❌ Error: 'app' directory not found!")
        print("   Make sure you're running this from the project root directory.")
        return 1
    
    # Change to the app directory
    os.chdir(app_dir)
    
    # Print startup information
    print("🚀 Starting Metabolical Backend API...")
    print("📁 Clean project structure active")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("-" * 60)
    
    # Start uvicorn server with verbose logging
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000", 
        "--reload",
        "--reload-dir", str(app_dir),
        "--log-level", "info",
        "--access-log",
        "--use-colors"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        return 1
    except FileNotFoundError:
        print("❌ Error: Python or uvicorn not found!")
        print("   Please install uvicorn: pip install uvicorn[standard]")
        return 1

if __name__ == "__main__":
    exit(main())
