"""
Setup Helper - Guide for downloading IPL dataset
Run: python setup.py
"""
import os
import sys
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def setup():
    print("\n" + "="*60)
    print("  IPL Big Data Project - Setup")
    print("="*60 + "\n")

    # Create directories
    Path('datasets').mkdir(exist_ok=True)
    Path('output').mkdir(exist_ok=True)
    print("[OK] Created directories: datasets/, output/")

    # Check if datasets exist
    matches_exists = Path('datasets/matches.csv').exists()
    deliveries_exists = Path('datasets/deliveries.csv').exists()

    print("\nDataset Status:")
    print(f"  matches.csv:    {'[Found]' if matches_exists else '[Missing]'}")
    print(f"  deliveries.csv: {'[Found]' if deliveries_exists else '[Missing]'}")

    if not (matches_exists and deliveries_exists):
        print("\nTo download datasets:")
        print("  1. Visit: https://www.kaggle.com/datasets/manasgarg/ipl")
        print("  2. Click 'Download'")
        print("  3. Extract the ZIP file")
        print("  4. Copy matches.csv and deliveries.csv")
        print("  5. Paste into: ./datasets/")
        print("\n   If you don't have Kaggle account, create one (it's free)")

    else:
        print("\n[OK] All datasets ready!")
        print("\nNext steps:")
        print("  Run: python run_all.py")

if __name__ == "__main__":
    setup()
