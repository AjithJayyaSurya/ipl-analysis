# IPL Big Data Analytics - Python Edition

> Converted from Apache Hive/Hadoop to Pure Python - Run in VS Code

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Dataset
- Visit: https://www.kaggle.com/datasets/manasgarg/ipl
- Download the ZIP file
- Extract both CSV files:
  - `matches.csv`
  - `deliveries.csv`
- Create `datasets/` folder in project root
- Place both CSV files there

### 3. Run Setup (Optional)
```bash
python setup.py
```
This creates necessary directories and shows dataset status.

### 4. Run All Analyses
```bash
python run_all.py
```

All 10 analyses will run sequentially, and results will be saved to `output/` folder.

---

## Project Structure

```
ipl_big_data_project/
├── python/                    # All analysis scripts
│   ├── 01_top_batsmen.py
│   ├── 02_top_bowlers.py
│   ├── 03_team_batting.py
│   ├── 04_phase_analysis.py
│   ├── 05_boundaries.py
│   ├── 06_extras.py
│   ├── 07_dismissals.py
│   ├── 08_inning_scores.py
│   ├── 09_economy.py
│   └── 10_head_to_head.py
│
├── datasets/                  # Download CSV files here
│   ├── matches.csv           (from Kaggle)
│   └── deliveries.csv        (from Kaggle)
│
├── output/                    # Results generated here
│   ├── 01_top_batsmen.csv
│   ├── 02_top_bowlers.csv
│   ├── 03_team_batting.csv
│   ├── 04_phase_analysis.csv
│   ├── 05_boundaries.csv
│   ├── 06_extras.csv
│   ├── 07_dismissals.csv
│   ├── 07_top_fielders.csv
│   ├── 08_inning_scores.csv
│   ├── 08_highest_innings.csv
│   ├── 09_economy.csv
│   ├── 10_head_to_head_runs.csv
│   ├── 10_head_to_head_wins.csv
│   └── 10_season_wins.csv
│
├── run_all.py                 # Main runner script
├── setup.py                   # Setup helper
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Analyses Included

| # | Analysis | File | Output |
|---|---|---|---|
| 1 | Top 20 Batsmen (runs + strike rate) | 01_top_batsmen.py | 01_top_batsmen.csv |
| 2 | Top 20 Bowlers (wickets) | 02_top_bowlers.py | 02_top_bowlers.csv |
| 3 | Team Batting Stats | 03_team_batting.py | 03_team_batting.csv |
| 4 | Phase Analysis (Powerplay/Middle/Death) | 04_phase_analysis.py | 04_phase_analysis.csv |
| 5 | Boundaries (4s & 6s) | 05_boundaries.py | 05_boundaries.csv |
| 6 | Extras - Bowling Discipline | 06_extras.py | 06_extras.csv |
| 7 | Dismissal Types Distribution | 07_dismissals.py | 07_dismissals.csv + 07_top_fielders.csv |
| 8 | Inning Scores (Avg/Max/Min) | 08_inning_scores.py | 08_inning_scores.csv + 08_highest_innings.csv |
| 9 | Economy Rates (min 100 overs) | 09_economy.py | 09_economy.csv |
| 10 | Head-to-Head Team Comparison | 10_head_to_head.py | 10_head_to_head_runs.csv + 10_head_to_head_wins.csv + 10_season_wins.csv |

---

## Running Individual Analyses

You can run individual analysis scripts without running all 10:

```bash
# Run just top batsmen analysis
python python/01_top_batsmen.py

# Run just top bowlers
python python/02_top_bowlers.py

# ... and so on for any analysis
```

Each script is **self-contained** and will load data from `datasets/` CSV files.

---

## Data Source

**IPL Datasets from Kaggle:**
- https://www.kaggle.com/datasets/manasgarg/ipl

**Dataset Contents:**
- `matches.csv`: One row per IPL match (2008 onwards)
  - Match ID, season, city, date, teams, toss, result, winner, etc.

- `deliveries.csv`: Ball-by-ball data
  - Match ID, inning, teams, batsman, bowler, runs, dismissals, etc.

---

## Requirements

- **Python 3.8+**
- **pandas** (2.1.0+) - Data manipulation
- **numpy** (1.26.0+) - Numerical computing
- **VS Code** (optional, but recommended)

---

## Installation

### Step 1: Clone/Download Project
```bash
cd your_project_directory
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/Scripts/activate    # Windows
# or
source venv/bin/activate        # macOS/Linux
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Download Datasets
See "Quick Start" section above.

### Step 5: Run
```bash
python run_all.py
```

---

## Output Files

All CSV files are saved to `output/` folder and can be opened directly in VS Code.

**Recommended:** Install "Rainbow CSV" VS Code extension for nice CSV formatting
- https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv

---

## Example Output

```
=== Top 20 Batsmen ===
        batsman  total_runs  balls_faced  strike_rate
0   Virat Kohli        5000         3800        131.58
1   Suresh Raina        4900         3900        125.64
...
```

---

## Troubleshooting

### Dataset files not found
```
[ERROR] datasets/matches.csv not found!
```
**Solution:** Download CSV files from Kaggle and place them in `datasets/` folder.

### Import error (pandas not found)
```
ModuleNotFoundError: No module named 'pandas'
```
**Solution:** Run `pip install -r requirements.txt`

### Script timeout
If a script takes >60 seconds, it may timeout. Increase timeout in `run_all.py` line 59:
```python
timeout=120  # Change to 120 seconds
```

---

## Performance

Typical runtime on modern machine:
- Each script: 2-5 seconds
- All 10 scripts: 30-60 seconds total

---

## Dataset Statistics

**Typical dataset size:**
- matches.csv: ~700 matches (2008-2024)
- deliveries.csv: ~190,000+ deliveries

Total data: ~5-10MB

---

## Conversion Notes

This project was originally built with:
- Apache Hadoop (distributed file system)
- Apache Hive (SQL-on-Hadoop)
- HiveQL queries

**Converted to pure Python using:**
- Pandas (dataframe operations)
- NumPy (numerical computing)
- Plain Python (logic)

**Benefits of Python version:**
- ✓ No Hadoop/Hive/Linux installation needed
- ✓ Runs directly in VS Code
- ✓ Faster for small-medium datasets
- ✓ Easy to modify and extend
- ✓ Cross-platform (Windows/Mac/Linux)

---

## Author

IPL Big Data Project - Python Edition
Created: 2024

Original Hive queries converted to Python for ease of use.

---

## License

Feel free to use for learning and analysis purposes.

