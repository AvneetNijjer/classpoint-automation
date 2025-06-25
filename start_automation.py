
#!/usr/bin/env python3
"""
ClassPoint Automation Startup Script
This script manages both the Python backend and provides instructions for the React frontend.
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def install_requirements():
    """Install Python requirements"""
    print("🔧 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Python dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def check_chrome_driver():
    """Check if Chrome is available"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("✅ Chrome WebDriver is working!")
        return True
    except Exception as e:
        print(f"❌ Chrome WebDriver issue: {e}")
        print("Please ensure Chrome browser is installed and accessible.")
        return False

def start_backend():
    """Start the Python Flask backend"""
    print("🚀 Starting Python backend server...")
    try:
        subprocess.run([sys.executable, 'automation_backend.py'])
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped by user")
    except Exception as e:
        print(f"❌ Backend server error: {e}")

def print_instructions():
    """Print instructions for running the full system"""
    print("\n" + "="*60)
    print("📋 CLASSPOINT AUTOMATION SETUP INSTRUCTIONS")
    print("="*60)
    print()
    print("1. 🐍 PYTHON BACKEND (Already starting...):")
    print("   - The Flask API server is starting on http://127.0.0.1:5000")
    print("   - This handles the browser automation logic")
    print()
    print("2. ⚛️  REACT FRONTEND:")
    print("   - Open a new terminal window/tab")
    print("   - Run: npm run dev")
    print("   - Open http://localhost:8080 in your browser")
    print()
    print("3. 🎯 USAGE:")
    print("   - Configure your class code and name in the web interface")
    print("   - Set your preferred answer strategy")
    print("   - Click 'Start Automation' to begin")
    print("   - The system will automatically join ClassPoint and answer polls")
    print()
    print("4. ⏰ SCHEDULING:")
    print("   - Enable scheduled start for automatic execution at 9:02 AM")
    print("   - Fallback time set to 9:10 AM if first attempt fails")
    print()
    print("5. 🔍 MONITORING:")
    print("   - Watch the status panel for real-time updates")
    print("   - View poll answer count and current status")
    print("   - Check error messages if issues occur")
    print()
    print("📝 LOGS: Check 'classpoint_automation.log' for detailed logs")
    print("🛑 STOP: Use Ctrl+C to stop the backend, or use the web interface")
    print()
    print("="*60)
    print()

def main():
    print("🎓 ClassPoint Automation System")
    print("Starting up...")
    print()
    
    # Check and install dependencies
    if not install_requirements():
        print("❌ Failed to set up Python environment. Exiting.")
        return
    
    # Check Chrome WebDriver
    if not check_chrome_driver():
        print("❌ Chrome WebDriver not available. Please install Chrome browser.")
        return
    
    # Print instructions
    print_instructions()
    
    # Start backend server
    try:
        start_backend()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
