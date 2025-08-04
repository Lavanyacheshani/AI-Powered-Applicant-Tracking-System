#!/usr/bin/env python3
"""
Startup script for the AI-Powered Applicant Tracking System
"""

import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        import torch
        import transformers
        print("✅ Python dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check if Node.js is installed
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js is installed: {result.stdout.strip()}")
        else:
            print("❌ Node.js is not installed")
            return False
    except FileNotFoundError:
        print("❌ Node.js is not installed")
        return False
    
    return True

def start_backend():
    """Start the FastAPI backend."""
    print("🚀 Starting backend server...")
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "backend:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the Next.js frontend."""
    print("🚀 Starting frontend server...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    try:
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=frontend_dir)
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def wait_for_backend():
    """Wait for backend to be ready."""
    import requests
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/")
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"⏳ Waiting for backend... ({i+1}/{max_attempts})")
    
    print("❌ Backend failed to start")
    return False

def wait_for_frontend():
    """Wait for frontend to be ready."""
    import requests
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:3000/")
            if response.status_code == 200:
                print("✅ Frontend is ready!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"⏳ Waiting for frontend... ({i+1}/{max_attempts})")
    
    print("❌ Frontend failed to start")
    return False

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print("\n🛑 Shutting down servers...")
    sys.exit(0)

def main():
    """Main startup function."""
    print("🧠 AI-Powered Applicant Tracking System")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # Wait for backend
    if not wait_for_backend():
        backend_process.terminate()
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    # Wait for frontend
    if not wait_for_frontend():
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 System is ready!")
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all servers")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main() 