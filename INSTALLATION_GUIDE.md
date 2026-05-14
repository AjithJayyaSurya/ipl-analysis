# IPL Big Data Project - Installation & Setup Guide

## Status: COMPLETE ✓

All 10 analyses have been successfully converted to Python and are ready to run in VS Code.

---

## What's Included

### Python Analysis Scripts (10 total)
- ✓ `01_top_batsmen.py` - Top 20 batsmen by runs & strike rate
- ✓ `02_top_bowlers.py` - Top 20 bowlers by wickets
- ✓ `03_team_batting.py` - Team batting statistics
- ✓ `04_phase_analysis.py` - Powerplay/Middle/Death phase analysis
- ✓ `05_boundaries.py` - Top boundaries (4s & 6s)
- ✓ `06_extras.py` - Bowling discipline analysis
- ✓ `07_dismissals.py` - Dismissal types & top fielders
- ✓ `08_inning_scores.py` - Inning score statistics
- ✓ `09_economy.py` - Economy rates (min 100 overs)
- ✓ `10_head_to_head.py` - Head-to-head team comparisons

### Utilities
- ✓ `run_all.py` - Run all 10 analyses sequentially
- ✓ `setup.py` - Setup and verify environment
- ✓ `requirements.txt` - Python dependencies (pandas, numpy)
- ✓ `PYTHON_README.md` - Complete Python edition documentation

---

## Installation (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Download Datasets
- Visit: https://www.kaggle.com/datasets/manasgarg/ipl
- Download ZIP file
- Extract: `matches.csv` and `deliveries.csv`
- Create: `datasets/` folder
- Place both CSV files in `datasets/`

### Step 3: Run Project
```bash
python run_all.py
```

---

## Verification

### Check Installation
```bash
python setup.py
```

### Run One Analysis (Test)
```bash
python python/01_top_batsmen.py
```

### Run all Analyses
```bash
python run_all.py
```

---

## Expected Output

```
============================================================
  IPL Big Data Project
============================================================

[OK] datasets/matches.csv found
[OK] datasets/deliveries.csv found
[OK] Output directory ready

============================================================
  IPL Big Data Analytics - Running All Analyses
============================================================

[1/10] Running 01_top_batsmen.py...
  [Done]

[2/10] Running 02_top_bowlers.py...
  [Done]

... (continues for all 10 analyses)

============================================================
  ALL ANALYSES COMPLETE!
============================================================

Output files created:
  1.2KB  01_top_batsmen.csv
  0.8KB  02_top_bowlers.csv
  ...
  (12 total output files)

Open any CSV in VS Code to view results
(Install 'Rainbow CSV' extension for nice formatting)

Total time: 45.3 seconds
```

---

## Output Files (12 total)

| File | Description |
|---|---|
| `01_top_batsmen.csv` | Top 20 batsmen by total runs |
| `02_top_bowlers.csv` | Top 20 bowlers by wickets |
| `03_team_batting.csv` | Team batting statistics |
| `04_phase_analysis.csv` | Phase-wise performance |
| `05_boundaries.csv` | Top boundaries (4s & 6s) |
| `06_extras.csv` | Extras conceded by teams |
| `07_dismissals.csv` | Dismissal types distribution |
| `07_top_fielders.csv` | Top fielders by catches |
| `08_inning_scores.csv` | Inning score statistics |
| `08_highest_innings.csv` | Top 10 highest innings |
| `09_economy.csv` | Economy rates (min 100 overs) |
| `10_head_to_head_*.csv` | Head-to-head comparisons (3 files) |

---

## System Requirements

- **Python:** 3.8 or higher
- **OS:** Windows, macOS, or Linux
- **RAM:** 2GB minimum
- **Disk:** 500MB for datasets + outputs
- **Network:** Internet (to download datasets from Kaggle)

---

## Installed Packages

```
pandas             3.0.3    ✓
numpy              2.4.4    ✓
python-dateutil    2.9.0    ✓
tzdata             2026.2   ✓
```

---

## Differences from Hive Version

| Aspect | Original (Hive) | Python Version |
|---|---|---|
| Runtime | Hadoop/HDFS | Local Python |
| Setup | Complex (Linux/WSL) | Simple (pip install) |
| IDE Support | Terminal only | Full VS Code support |
| Performance | Distributed | Single machine |
| Learning | Big data (Hadoop) | Python data science (Pandas) |

---

## Troubleshooting

### Dataset not found
```
[ERROR] datasets/matches.csv not found!
```
→ Download from Kaggle and place in `datasets/` folder

### Pandas import error
```
ModuleNotFoundError: No module named 'pandas'
```
→ Run: `pip install -r requirements.txt`

### Permission denied
```
PermissionError: [Errno 13] Permission denied
```
→ Run VS Code as Administrator (if on Windows)

---

## Next Steps

1. **Download datasets** from Kaggle
2. **Run setup.py** to verify installation
3. **Run run_all.py** to start analysis
4. **Open CSV files** in VS Code with Rainbow CSV extension
5. **Analyze results** and create visualizations

---

## Documentation

- **PYTHON_README.md** - Complete Python guide
- **README.md** - Original Hive project documentation
- **Hive folder** - Original HiveQL scripts (reference)

---

## Support

For issues or questions:
1. Check PYTHON_README.md
2. Verify datasets are in `datasets/` folder
3. Ensure Python 3.8+ is installed
4. Try running individual scripts: `python python/01_top_batsmen.py`

---

## Summary

✓ Project fully converted to Python
✓ All 10 analyses implemented
✓ Dependencies installed
✓ Ready to run in VS Code
✓ No Hadoop/Hive/Linux needed

**Next action:** Download datasets and run `python run_all.py`

