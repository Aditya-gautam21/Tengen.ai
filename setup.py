#!/usr/bin/env python3
"""
Tengen.ai Setup Script
Production-ready installation and configuration
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_backend_dependencies():
    """Install backend Python dependencies"""
    try:
        logger.info("Installing backend dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, cwd="backend")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install backend dependencies: {e}")
        return False

def install_frontend_dependencies():
    """Install frontend Node.js dependencies"""
    try:
        logger.info("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], check=True, cwd="frontend")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install frontend dependencies: {e}")
        return False

def setup_environment():
    """Setup environment files"""
    try:
        backend_env = Path("backend/.env")
        if not backend_env.exists():
            logger.info("Creating backend environment file...")
            with open(backend_env, "w") as f:
                f.write("# Tengen.ai Backend Configuration\n")
                f.write("GOOGLE_API_KEY=your_google_api_key_here\n")
                f.write("HOST=0.0.0.0\n")
                f.write("PORT=8080\n")
                f.write("LOG_LEVEL=INFO\n")
                f.write("ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173\n")
        
        frontend_env = Path("frontend/.env.local")
        if not frontend_env.exists():
            logger.info("Creating frontend environment file...")
            with open(frontend_env, "w") as f:
                f.write("# Tengen.ai Frontend Configuration\n")
                f.write("NEXT_PUBLIC_API_HOST=localhost\n")
                f.write("NEXT_PUBLIC_API_URL=http://localhost:8080\n")
        
        return True
    except Exception as e:
        logger.error(f"Failed to setup environment: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("Setting up Tengen.ai...")
    
    # Install dependencies
    if not install_backend_dependencies():
        sys.exit(1)
    
    if not install_frontend_dependencies():
        logger.warning("Frontend dependencies installation failed. You may need to install Node.js.")
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    logger.info("Setup completed successfully!")
    logger.info("Please edit backend/.env with your Google API key before starting the application.")
    logger.info("Run 'python start.py' to start the application.")

if __name__ == "__main__":
    main()