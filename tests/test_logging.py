#!/usr/bin/env python3
"""
Test logging configuration
"""

import sys
import os
from pathlib import Path

# Add app directory to path
script_dir = Path(__file__).parent
app_dir = script_dir / "app"
sys.path.insert(0, str(app_dir))

# Test logging
print("🧪 Testing logging configuration...")

try:
    # Import the main app
    from main import app, logger
    
    print("✅ Successfully imported main app and logger")
    
    # Test logging levels
    logger.debug("🐛 DEBUG level test")
    logger.info("ℹ️ INFO level test")
    logger.warning("⚠️ WARNING level test") 
    logger.error("❌ ERROR level test")
    
    print("✅ Logging test completed")
    print("📊 If you see the colored emojis above, logging is working!")
    
except Exception as e:
    print(f"❌ Error testing logging: {e}")
    import traceback
    traceback.print_exc()
