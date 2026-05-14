"""
IPL Analytics Web Server Starter
Run this to start the web application

Usage: python start_web.py
"""
import sys
import os

# Check if datasets exist
from pathlib import Path

print("\n" + "="*60)
print("  IPL Big Data Analytics - Web Application")
print("="*60 + "\n")

# Check datasets
if not Path('datasets/matches.csv').exists():
    print("[ERROR] datasets/matches.csv not found!")
    print("Please download from: https://www.kaggle.com/datasets/manasgarg/ipl")
    sys.exit(1)

if not Path('datasets/deliveries.csv').exists():
    print("[ERROR] datasets/deliveries.csv not found!")
    sys.exit(1)

print("[OK] Datasets found")
print("[INFO] Starting Flask web server...\n")

# Import and run Flask app
from app import app

print("="*60)
print("  WEB APPLICATION RUNNING")
print("="*60)
print()
print("  Open your browser to: http://localhost:5000")
print()
print("  Visit these pages:")
print("  • Home:      http://localhost:5000")
print("  • Dashboard: http://localhost:5000/dashboard")
print()
print("  API Endpoints:")
print("  • http://localhost:5000/api/summary")
print("  • http://localhost:5000/api/top-batsmen")
print("  • http://localhost:5000/api/top-bowlers")
print("  • http://localhost:5000/api/team-stats")
print("  • http://localhost:5000/api/phase-analysis")
print("  • http://localhost:5000/api/dismissals")
print()
print("  Press Ctrl+C to stop the server")
print()
print("="*60 + "\n")

# Run
app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
