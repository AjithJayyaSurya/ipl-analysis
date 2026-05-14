# 🏏 IPL Big Data Analytics Pro

**Status:** ✅ Complete & Production-Ready &nbsp;|&nbsp; **Data Coverage:** 2008–2017 &nbsp;|&nbsp; **Last Updated:** May 2026

A full-stack cricket intelligence platform that processes ball-by-ball IPL data across 10 seasons. It combines batch data processing (Pandas, Multiprocessing, Apache Spark), a REST API backend (Flask), and an interactive single-page web dashboard with 30+ analytics features.

---

## 📊 Dataset at a Glance

| Metric | Value |
|---|---|
| Matches | 636 |
| Deliveries | 150,460 |
| Players | 461 |
| Teams | 14 |
| Seasons | 10 (2008–2017) |

**Source:** [Kaggle IPL Dataset](https://www.kaggle.com/datasets/manasgarg/ipl) — place `matches.csv` and `deliveries.csv` in the `datasets/` folder.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements_web.txt

# 2. Start the web server
python app.py

# 3. Open browser
# http://localhost:5000
```

To run batch analysis only (generates 14 CSV files):

```bash
python run_all_multiprocessing.py   # fastest — 7 sec, uses all CPU cores
python run_all.py                   # simple  — 24 sec, single-threaded
python run_all_spark.py             # advanced — requires Java JDK 11+
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| Web Framework | Flask 3.x |
| Data Processing | Pandas, NumPy |
| Parallel Processing | Python Multiprocessing (3.3× speedup) |
| Big Data (optional) | Apache Spark (PySpark) |
| Query Engine (optional) | Apache Hive (HQL) |
| Data Pipeline (optional) | Apache Pig |
| Visualization | Plotly.js |
| Frontend | Vanilla HTML / CSS / JavaScript (SPA) |

---

## 📁 Project Structure

```
ipl_big_data_project/
│
├── app.py                        # Flask web server — all routes & API endpoints
├── analytics_api.py              # 15 advanced analytics functions
├── requirements.txt              # Core dependencies (pandas, numpy)
├── requirements_web.txt          # Web dependencies (flask, plotly, pandas, numpy)
│
├── datasets/                     # ← Place Kaggle CSVs here
│   ├── matches.csv               # 636 match records
│   └── deliveries.csv            # 150,460 ball-by-ball records
│
├── data/                         # Pre-generated metadata (JSON)
│   ├── player_metadata.json      # Career stats for 461 players
│   ├── ipl_champions.json        # Season champions 2008–2017
│   ├── seasonal_rankings.json    # Top 10 batsmen/bowlers per season
│   └── player_records.json       # All-time IPL records
│
├── python/                       # 10 standalone batch analysis scripts
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
├── output/                       # 14 pre-generated CSV result files
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
├── templates/
│   └── index.html                # Single-page web app (33 KB)
│
├── static/
│   └── app.js                    # All frontend logic (37 KB)
│
├── hive/                         # 11 HQL scripts (Apache Hive reference)
├── pig/                          # 2 Pig scripts (Apache Pig reference)
│
├── run_all.py                    # Sequential batch runner
├── run_all_multiprocessing.py    # Parallel batch runner ⭐ recommended
├── run_all_spark.py              # Spark batch runner
│
├── generate_player_metadata.py   # Regenerate player_metadata.json
├── generate_ipl_champions.py     # Regenerate ipl_champions.json
├── generate_seasonal_rankings.py # Regenerate seasonal_rankings.json
├── generate_player_records.py    # Regenerate player_records.json
│
└── docs/
    └── project_report.md         # Academic project report
```

---

## 🌐 Web Dashboard

Single-page app at **http://localhost:5000** with 8 top-level tabs and dark/light mode toggle.

### 📊 Dashboard
Six inner tabs with interactive Plotly charts and sortable tables:
- Top 20 Batsmen — runs, balls faced, strike rate
- Top 20 Bowlers — wickets
- Team Run Rate — all seasons
- Phase Analysis — Powerplay / Middle / Death run rate per team
- Dismissal Types — donut chart with percentages
- Top Fielders — catches taken

### 🔬 Advanced Analytics (12 sub-tabs)
| Sub-tab | What it shows |
|---|---|
| Playoff Scorers | Top run scorers in knockout stages |
| Batsman Consistency | Std dev, 30+/50+ frequency, consistency score |
| Bowler Consistency | Economy variance, wickets/game |
| Partnerships | Best batting pairs by total runs |
| Phase Specialists | PP / Middle / Death × Bat / Bowl (6 views) |
| Spinner vs Fast | Split wicket leaderboards |
| Age Curves | Strike rate and economy vs age |
| MVP / Season | Weighted MVP formula per season |
| Par Score Evolution | Avg vs winning 1st innings score 2008–2017 |
| Venue Dominance | Batting / Bowling / Neutral ground classification |
| Toss Impact | Toss win → match win % by venue and decision |
| Chase vs Defend | Win % per team in each scenario |

### ⚖️ Compare Players
Live autocomplete search, side-by-side stat cards with green highlight on better metric, grouped bar chart.

### 📅 Season Rankings
Season dropdown (2008–2017), top 10 batsmen and bowlers side by side.

### ⭐ Records
Hero tiles for highest score, most centuries, most wickets. Six record tables: centuries, wickets, sixes, catches, fifties, fours.

### 🏆 Champions History
Trophy banner, stat tiles, full season-wise table with colour-coded badges.

### 🥇 Best XI
Algorithm-generated all-time XI (min 10 matches, weighted formula), card grid with role badges.

### 🛡 Teams
Chase vs Defend chart, Toss Impact breakdown, Venue stats.

---

## 🔌 API Reference

### Core Analytics
| Endpoint | Returns |
|---|---|
| `GET /api/summary` | Total matches, deliveries, teams, batsmen, bowlers |
| `GET /api/top-batsmen` | Top 20 by runs — name, runs, balls, SR |
| `GET /api/top-bowlers` | Top 20 by wickets |
| `GET /api/team-stats` | Run rate per team |
| `GET /api/phase-analysis` | PP/Middle/Death run rate per team |
| `GET /api/dismissals` | Dismissal type distribution |
| `GET /api/top-fielders` | Top 15 catchers |

### Advanced Analytics
| Endpoint | Returns |
|---|---|
| `GET /api/playoff-scorers` | Top run scorers in last 4 matches/season |
| `GET /api/batsman-consistency` | Std dev, 30+/50+ frequency, score |
| `GET /api/bowler-consistency` | Economy variance, wickets/game |
| `GET /api/partnership-analysis` | Best batting pairs |
| `GET /api/powerplay-batsmen` | Top batsmen overs 1–6 |
| `GET /api/powerplay-bowlers` | Top bowlers overs 1–6 |
| `GET /api/middle-batsmen` | Top batsmen overs 7–15 |
| `GET /api/middle-bowlers` | Top bowlers overs 7–15 |
| `GET /api/death-batsmen` | Top batsmen overs 16–20 |
| `GET /api/death-bowlers` | Top bowlers overs 16–20 |
| `GET /api/spinner-vs-fast` | Split wicket leaderboard |
| `GET /api/age-vs-sr` | Age vs average strike rate |
| `GET /api/age-vs-economy` | Age vs average economy rate |
| `GET /api/mvp-per-season` | Weighted MVP per season |
| `GET /api/par-score-evolution` | Avg and winning score per season |
| `GET /api/venue-dominance` | Ground batting/bowling classification |
| `GET /api/toss-impact` | Toss win → match win % |
| `GET /api/chasing-defending` | Chase vs defend win % per team |
| `GET /api/best-xi` | Algorithm-generated all-time XI |

### Player & Historical
| Endpoint | Returns |
|---|---|
| `GET /api/player/<name>` | Full career stats |
| `GET /api/player-search?q=` | Autocomplete search |
| `GET /api/ipl-champions` | Season-wise champions |
| `GET /api/seasonal-rankings?season=` | Top 10 per season |
| `GET /api/player-records` | All-time records |
| `GET /api/venue-stats` | Avg score per venue |

### Export
| Endpoint | Returns |
|---|---|
| `GET /export/player/<name>/json` | Player data as JSON |
| `GET /export/player/<name>/csv` | Player data as CSV |
| `GET /export/season-rankings/json` | All rankings as JSON |
| `GET /export/top-records/json` | All records as JSON |

---

## ⚡ Batch Processing Performance

| Engine | Time | Cores | Setup |
|---|---|---|---|
| Pandas | 24 sec | 1 | None |
| Multiprocessing ⭐ | 7.3 sec | All | None |
| Apache Spark | ~18 sec | All | Java JDK 11+ |

---

## 📐 Key Analytics Formulas

**Consistency Score (Batsman):** `max(0, 100 − (std_dev / avg) × 50)`

**Consistency Score (Bowler):** `max(0, 100 − economy_std_dev × 15)`

**MVP Points:** `(runs / 10) + max(0, SR − 100) / 20 + (wickets × 20) − (economy × 2)`

**Phase classification:** Overs 1–6 = Powerplay · 7–15 = Middle · 16–20 = Death

**Venue dominance:** Batting if avg score > overall avg × 1.05 · Bowling if < 0.95 · else Neutral

---

## 🔧 Installation

```bash
# Clone / navigate to project
cd "e:\resume projects work\ipl_big_data_project\ipl_big_data_project"

# (Optional) Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements_web.txt

# Download datasets from Kaggle and place in datasets/
# https://www.kaggle.com/datasets/manasgarg/ipl

# Start web server
python app.py
```

To regenerate the JSON metadata files from scratch:

```bash
python generate_ipl_champions.py
python generate_player_metadata.py
python generate_seasonal_rankings.py
python generate_player_records.py
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: flask` | `pip install -r requirements_web.txt` |
| `datasets/matches.csv not found` | Download from Kaggle, place in `datasets/` |
| Port 5000 in use | Edit `app.py` last line: change `port=5000` to `port=5001` |
| Player data not loading | Re-run the four `generate_*.py` scripts |
| Slow first load | Normal — data loads into memory once at startup |

---

## 🎓 Learning Outcomes

This project demonstrates:
- Full-stack web application development (Flask + Vanilla JS)
- Large dataset processing with Pandas and NumPy
- Parallel processing with Python Multiprocessing
- Distributed computing with Apache Spark
- REST API design and implementation
- Interactive data visualization with Plotly.js
- Single-page application architecture
- Big Data tooling: Hive (HQL) and Pig scripts included as reference

---

## 📄 License

Created for educational and portfolio purposes. Data sourced from the [Kaggle IPL Dataset](https://www.kaggle.com/datasets/manasgarg/ipl).
