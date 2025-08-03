#!/usr/bin/env python3
"""
Production deployment script for Metabolical Backend
Optimized for Render.com deployment
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the production server"""
    
    # Get environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 2))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print("🚀 STARTING METABOLICAL BACKEND (PRODUCTION)")
    print("=" * 50)
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"👥 Workers: {workers}")
    print(f"📊 Log Level: {log_level}")
    print(f"🌐 Environment: {'Production (Render)' if os.getenv('RENDER') else 'Local Production'}")
    
    try:
        # Production command with uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", host,
            "--port", str(port),
            "--workers", str(workers),
            "--log-level", log_level,
            "--access-log",
            "--no-use-colors"  # Better for production logs
        ]
        
        print(f"🔧 Running: {' '.join(cmd)}")
        print("🌟 Starting production server...")
        print()
        
        # Run the server
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
