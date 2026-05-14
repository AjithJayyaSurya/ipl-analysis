"""
IPL Big Data Analytics - Using Apache Spark (PySpark)
Auto-installs Spark if not present
Run: python install_spark.py
"""
import subprocess
import sys
import os

def install_spark():
    """Install PySpark and dependencies"""
    print("\n" + "="*60)
    print("  Installing Apache Spark (PySpark)")
    print("="*60 + "\n")

    packages = [
        'pyspark>=3.5.0',
        'pandas>=2.1.0',
        'numpy>=1.26.0',
    ]

    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"  ✓ {package} installed\n")

    print("="*60)
    print("  ✓ ALL PACKAGES INSTALLED")
    print("="*60)
    print("\nNext step: Run 'python run_all_spark.py'\n")

if __name__ == "__main__":
    try:
        install_spark()
    except Exception as e:
        print(f"\n[ERROR] Installation failed: {e}")
        sys.exit(1)
