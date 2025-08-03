#!/usr/bin/env python3
"""
Simple startup script for Metabolical Backe        # Configure log level
        if args.debug:
            cmd.extend(["--log-level", "debug"])
        else:
            cmd.extend(["--log-level", "info"])
        
        # Add basic options
        cmd.extend(["--access-log", "--use-colors"]) easy-to-understand project structure
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse
import socket

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "YOUR_IP_ADDRESS"

def main():
    """Start the Metabolical Backend API server"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Start Metabolical Backend API")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with detailed logging")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 8000)), help="Port to bind to (default: 8000)")
    parser.add_argument("--public-url", default=os.getenv("PUBLIC_URL", ""), help="Public URL for the API (e.g., https://yourdomain.com)")
    parser.add_argument("--public", action="store_true", help="Enable public access (bind to 0.0.0.0)")
    args = parser.parse_args()
    
    # Override host for public access
    if args.public:
        args.host = "0.0.0.0"
    
    # Get the directory of this script (project root)
    script_dir = Path(__file__).parent
    app_dir = script_dir / "app"
    
    # Check if app directory exists
    if not app_dir.exists():
        print("❌ Error: 'app' directory not found!")
        print("   Make sure you're running this from the project root directory.")
        return 1
    
    print("🚀 STARTING METABOLICAL BACKEND API")
    print("=" * 50)
    print(f"📍 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"🐛 Debug: {'Enabled' if args.debug else 'Disabled'}")
    
    # Display URLs based on configuration
    if args.public_url:
        print(f"🌐 Public URL: {args.public_url}")
        print(f"📖 Public Docs: {args.public_url}/docs")
        print(f"🔄 Public API: {args.public_url}/api/v1/")
    elif args.public or args.host == "0.0.0.0":
        # Public access mode - show both local and network access info
        local_url = f"http://127.0.0.1:{args.port}"
        local_ip = get_local_ip()
        network_url = f"http://{local_ip}:{args.port}"
        print(f"🏠 Local URL: {local_url}")
        print(f"🌐 Network URL: {network_url}")
        print(f"📖 Local Docs: {local_url}/docs")
        print(f"🌐 Network Docs: {network_url}/docs")
        print(f"🔄 Local API: {local_url}/api/v1/")
        print(f"🌍 Network API: {network_url}/api/v1/")
        print("💡 Network URL is accessible from other devices on the same network")
    else:
        # Local-only URLs
        local_url = f"http://{args.host}:{args.port}"
        print(f"🏠 Local URL: {local_url}")
        print(f"📖 Local Docs: {local_url}/docs")
        print(f"🔄 Local API: {local_url}/api/v1/")
    
    print("📁 Clean project structure active")
    
    try:
        # Start the FastAPI server using uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app",
            "--host", args.host,
            "--port", str(args.port)
        ]
        
        # Add reload only if debug mode is enabled
        if args.debug:
            cmd.append("--reload")
        
        # Configure log level
        if args.debug:
            cmd.extend(["--log-level", "debug"])
        else:
            cmd.extend(["--log-level", "info"])
        
        # Add production-ready options for public deployment
        if not args.debug and args.port in [80, 443]:
            # Production settings for standard web ports
            cmd.extend([
                "--workers", "4",  # Multiple workers for better performance
                "--access-log",
                "--no-use-colors"  # Better for production logs
            ])
        else:
            # Development/local settings
            cmd.extend(["--access-log", "--use-colors"])
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        print("🌟 Starting server... (Press Ctrl+C to stop)")
        print()
        
        # Run the server
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        return 1
    except FileNotFoundError:
        print("❌ Error: Python or uvicorn not found!")
        print("   Please install uvicorn: pip install uvicorn[standard]")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
