"""
Main Runner - Execute all 10 IPL analyses
Run: python run_all.py
"""
import os
import subprocess
import sys
import time
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_datasets():
    """Verify CSV files exist"""
    if not Path('datasets/matches.csv').exists():
        print("[ERROR] datasets/matches.csv not found!")
        print("   Download from: https://www.kaggle.com/datasets/manasgarg/ipl")
        return False

    if not Path('datasets/deliveries.csv').exists():
        print("[ERROR] datasets/deliveries.csv not found!")
        print("   Download from: https://www.kaggle.com/datasets/manasgarg/ipl")
        return False

    print("[OK] datasets/matches.csv found")
    print("[OK] datasets/deliveries.csv found")
    return True

def create_output_dir():
    """Create output directory if it doesn't exist"""
    Path('output').mkdir(exist_ok=True)
    print("[OK] Output directory ready")

def run_analyses():
    """Run all 10 analysis scripts"""

    scripts = [
        'python\\01_top_batsmen.py',
        'python\\02_top_bowlers.py',
        'python\\03_team_batting.py',
        'python\\04_phase_analysis.py',
        'python\\05_boundaries.py',
        'python\\06_extras.py',
        'python\\07_dismissals.py',
        'python\\08_inning_scores.py',
        'python\\09_economy.py',
        'python\\10_head_to_head.py',
    ]

    print("\n" + "="*60)
    print("  IPL Big Data Analytics - Running All Analyses")
    print("="*60 + "\n")

    for i, script in enumerate(scripts, 1):
        try:
            print(f"[{i}/{len(scripts)}] Running {Path(script).name}...")
            result = subprocess.run(
                ['python', script],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(f"  [Done]\n")
            else:
                print(f"  [ERROR]:\n{result.stderr}\n")
                return False

        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT]\n")
            return False
        except Exception as e:
            print(f"  [ERROR]: {e}\n")
            return False

    return True

def show_summary():
    """Show output files summary"""
    output_files = sorted(Path('output').glob('*.csv'))

    print("\n" + "="*60)
    print("  ALL ANALYSES COMPLETE!")
    print("="*60)
    print("\nOutput files created:")
    for f in output_files:
        size = f.stat().st_size
        size_str = f"{size/1024:.1f}KB" if size > 1024 else f"{size}B"
        print(f"  {size_str:>8}  {f.name}")
    print("\nOpen any CSV in VS Code to view results")
    print("(Install 'Rainbow CSV' extension for nice formatting)\n")

if __name__ == "__main__":
    start_time = time.time()

    print("\n" + "="*60)
    print("  IPL Big Data Project")
    print("="*60 + "\n")

    # Check datasets
    if not check_datasets():
        sys.exit(1)

    print()

    # Create output directory
    create_output_dir()

    print()

    # Run all analyses
    if run_analyses():
        elapsed = time.time() - start_time
        show_summary()
        print(f"Total time: {elapsed:.1f} seconds\n")
    else:
        print("\n[ERROR] Some analyses failed. Check errors above.\n")
        sys.exit(1)
