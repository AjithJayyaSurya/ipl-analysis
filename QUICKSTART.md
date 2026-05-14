# QUICKSTART - Run in 3 Steps

## Step 1: Install Packages (1 minute)
Open terminal in VS Code and run:
```bash
pip install -r requirements.txt
```

**Output should be:**
```
Successfully installed numpy-2.4.4 pandas-3.0.3 python-dateutil-2.9.0.post0 six-1.17.0 tzdata-2026.2
```

---

## Step 2: Get Datasets (5 minutes)

1. Go to: https://www.kaggle.com/datasets/manasgarg/ipl
2. Click **Download** button
3. Extract the ZIP file
4. You'll see: `matches.csv` and `deliveries.csv`
5. Create folder named `datasets` in project root
6. Copy both CSV files into `datasets/` folder

**Folder structure should look like:**
```
ipl_big_data_project/
├── datasets/
│   ├── matches.csv
│   └── deliveries.csv
├── python/
├── output/
└── run_all.py
```

---

## Step 3: Run Analysis (1-2 minutes)

In terminal, run:
```bash
python run_all.py
```

**Watch the output:**
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

... (8 more analyses)

============================================================
  ALL ANALYSES COMPLETE!
============================================================

Output files created:
  1.2KB  01_top_batsmen.csv
  0.8KB  02_top_bowlers.csv
  ...

Total time: 45.3 seconds
```

---

## Done!

All results are in `output/` folder. Open any CSV file in VS Code.

**Tip:** Install "Rainbow CSV" VS Code extension for nice formatting:
- Open VS Code Extensions (Ctrl+Shift+X or Cmd+Shift+X)
- Search: "Rainbow CSV"
- Install by mechatroner

---

## What Each Analysis Produces

1. **Top Batsmen** - Best players by runs scored
2. **Top Bowlers** - Best bowlers by wickets
3. **Team Stats** - Overall team performance
4. **Phase Analysis** - How teams perform in Powerplay, Middle, Death overs
5. **Boundaries** - Most 4s and 6s by player
6. **Extras** - Best bowling discipline (fewest extras)
7. **Dismissals** - How batsmen get out (caught, bowled, LBW, etc.)
8. **Inning Scores** - Average, max, min scores per inning
9. **Economy** - Best bowlers by runs conceded per over
10. **Head-to-Head** - How teams perform against each other

---

## Troubleshooting

**"datasets/matches.csv not found"**
→ Check that CSV files are in `datasets/` folder

**"ModuleNotFoundError: No module named 'pandas'"**
→ Run: `pip install -r requirements.txt`

**"Permission denied"**
→ Try running VS Code as Administrator

---

## Individual Analyses (Optional)

Run just one analysis without running all:
```bash
python python/01_top_batsmen.py
python python/02_top_bowlers.py
# ... etc
```

---

**That's it! Your project is ready to use.** 🎉
