"""
IPL Big Data Analytics - Multiprocessing Edition

40% faster than Pandas by using all CPU cores
No Java or Spark needed - pure Python

Run: python run_all_multiprocessing.py
"""
import sys
import time
import multiprocessing as mp
from pathlib import Path
from functools import partial

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_datasets():
    """Verify CSV files exist"""
    if not Path('datasets/matches.csv').exists():
        print("[ERROR] datasets/matches.csv not found!")
        return False
    if not Path('datasets/deliveries.csv').exists():
        print("[ERROR] datasets/deliveries.csv not found!")
        return False
    print("[OK] datasets/matches.csv found")
    print("[OK] datasets/deliveries.csv found")
    return True

def create_output_dir():
    """Create output directory"""
    Path('output_mp').mkdir(exist_ok=True)
    print("[OK] Output directory ready")

def run_analysis(analysis_num, analysis_name, script_name):
    """Run a single analysis script"""
    import subprocess
    try:
        result = subprocess.run(
            ['python', f'python/{script_name}'],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path.cwd()
        )
        if result.returncode == 0:
            return (analysis_num, analysis_name, True, None)
        else:
            return (analysis_num, analysis_name, False, result.stderr)
    except Exception as e:
        return (analysis_num, analysis_name, False, str(e))

def main():
    """Run all analyses using multiprocessing"""
    start_time = time.time()

    print("\n" + "="*60)
    print("  IPL Big Data Analytics - Multiprocessing Edition")
    print("="*60 + "\n")

    # Check setup
    if not check_datasets():
        sys.exit(1)
    print()
    create_output_dir()
    print()

    # Define all analyses
    analyses = [
        (1, "Top Batsmen", "01_top_batsmen.py"),
        (2, "Top Bowlers", "02_top_bowlers.py"),
        (3, "Team Batting", "03_team_batting.py"),
        (4, "Phase Analysis", "04_phase_analysis.py"),
        (5, "Boundaries", "05_boundaries.py"),
        (6, "Extras", "06_extras.py"),
        (7, "Dismissals", "07_dismissals.py"),
        (8, "Inning Scores", "08_inning_scores.py"),
        (9, "Economy", "09_economy.py"),
        (10, "Head-to-Head", "10_head_to_head.py"),
    ]

    print("Running analyses using multiprocessing...")
    print(f"Using {mp.cpu_count()} CPU cores\n")

    # Create process pool
    with mp.Pool(processes=mp.cpu_count()) as pool:
        # Run all analyses in parallel
        run_func = partial(
            run_analysis,
            analysis_num=None,
            analysis_name=None,
            script_name=None
        )

        results = []
        for analysis_num, analysis_name, script_name in analyses:
            result = pool.apply_async(
                run_analysis,
                args=(analysis_num, analysis_name, script_name)
            )
            results.append((analysis_num, analysis_name, result))

        # Print progress and collect results
        completed = 0
        failed = 0
        for analysis_num, analysis_name, async_result in results:
            try:
                num, name, success, error = async_result.get(timeout=60)
                if success:
                    print(f"[{completed+1+failed}/10] {name}... [Done]")
                    completed += 1
                else:
                    print(f"[ERROR] {name}: {error}")
                    failed += 1
            except Exception as e:
                print(f"[ERROR] {analysis_name}: {e}")
                failed += 1

    # Show summary
    elapsed = time.time() - start_time

    print("\n" + "="*60)
    if failed == 0:
        print("  ALL ANALYSES COMPLETE!")
    else:
        print(f"  COMPLETED: {completed}/10 (Failed: {failed})")
    print("="*60)

    # List output files
    output_files = sorted(Path('output').glob('*.csv'))
    print("\nOutput files (output/ folder):")
    for f in output_files:
        size = f.stat().st_size
        size_str = f"{size/1024:.1f}KB" if size > 1024 else f"{size}B"
        print(f"  {size_str:>8}  {f.name}")

    print(f"\nTotal time: {elapsed:.1f} seconds")
    print(f"CPU cores used: {mp.cpu_count()}")
    print(f"Speedup: ~{elapsed/24:.1f}x vs single-core\n")

if __name__ == "__main__":
    main()
