#!/usr/bin/env python3
"""
Debug startup script for Metabolical Backend API
Shows detailed logging and debugging information
"""

import subprocess
import sys
import os
from pathlib import Path
import logging

def main():
    """Start the Metabolical Backend API server with detailed logging"""
    
    # Configure detailed logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    
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
    print("🚀 Starting Metabolical Backend API (DEBUG MODE)...")
    print("📁 Clean project structure active")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Debug logging enabled")
    print("-" * 60)
    
    # Start uvicorn server with maximum verbosity
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000", 
        "--reload",
        "--reload-dir", str(app_dir),
        "--log-level", "debug",
        "--access-log",
        "--use-colors"
    ]
    
    logger.info(f"Starting server with command: {' '.join(cmd)}")
    
    try:
        # Use subprocess.Popen instead of run to get real-time output
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line.strip())
            
        process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        if 'process' in locals():
            process.terminate()
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
