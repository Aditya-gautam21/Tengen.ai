#!/usr/bin/env python3
"""
Tengen.ai Production Startup Script
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Check if environment is properly configured"""
    required_env_vars = ['GOOGLE_API_KEY']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set these variables in backend/.env file")
        return False
    
    return True

def start_backend():
    """Start the backend server"""
    try:
        backend_dir = Path(__file__).parent / "backend"
        os.chdir(backend_dir)
        
        logger.info("Starting Tengen.ai backend server...")
        subprocess.run([sys.executable, "main.py"], check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start backend: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    logger.info("Starting Tengen.ai Production Server...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Start backend
    if not start_backend():
        sys.exit(1)
    
    logger.info("Tengen.ai started successfully!")

if __name__ == "__main__":
    main()