# IPL Web Analytics - QUICK START

## Run the Website in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements_web.txt
```

Installs:
- Flask (web framework)
- Plotly (interactive charts)
- Pandas (data processing)
- NumPy (numeric library)

### Step 2: Start Web Server
```bash
python start_web.py
```

You'll see:
```
==================================================
  IPL Big Data Analytics - Web Application
==================================================

  Open your browser to: http://localhost:5000

  Visit these pages:
  • Home:      http://localhost:5000
  • Dashboard: http://localhost:5000/dashboard
  ...
```

### Step 3: Open Browser
Visit: **http://localhost:5000**

---

## What You'll See

### Home Page
- Welcome message
- 4 feature highlights
- Button to access dashboard

### Dashboard (/dashboard)
**Summary Cards (top):**
- Total Matches: 700
- Total Teams: 13
- Total Batsmen: 800
- Total Bowlers: 600

**6 Tabs with Interactive Charts:**
1. **Top Batsmen** - Bar chart + table
2. **Top Bowlers** - Bar chart + table
3. **Team Stats** - Run rates by team
4. **Phase Analysis** - Powerplay/Middle/Death performance
5. **Dismissals** - Pie chart of dismissal types
6. **Top Fielders** - Catches by fielder

All charts are **interactive** - hover, zoom, pan!

---

## API Endpoints

All data available via REST API:

```bash
# Try in your browser:
http://localhost:5000/api/summary
http://localhost:5000/api/top-batsmen
http://localhost:5000/api/top-bowlers
http://localhost:5000/api/team-stats
http://localhost:5000/api/phase-analysis
http://localhost:5000/api/dismissals
http://localhost:5000/api/top-fielders
```

Returns JSON data!

---

## Stop the Server

Press **Ctrl+C** in the terminal

---

## Access from Other Computers

If on same network, other computers can visit:
```
http://<your-computer-ip>:5000
```

Find your IP:
- **Windows:** Run `ipconfig` in cmd, look for "IPv4 Address"
- **Mac/Linux:** Run `ifconfig` in terminal

---

## File Structure

```
ipl_big_data_project/
├── start_web.py           ← Run this to start
├── app.py                 ← Flask app
├── requirements_web.txt   ← Dependencies
│
├── templates/             ← Web pages
│   ├── index.html         (home)
│   └── dashboard.html     (dashboard)
│
├── static/                ← CSS & JavaScript
│   ├── style.css
│   └── dashboard.js
│
└── datasets/              ← Your data
    ├── matches.csv
    └── deliveries.csv
```

---

## Troubleshooting

### "Port 5000 already in use"
Another app is using port 5000. Either:
- Close the other app
- Run on different port: `python -c "from app import app; app.run(port=5001)"`

### "Datasets not found"
- Check datasets/ folder exists
- Place matches.csv and deliveries.csv files there
- Download from: https://www.kaggle.com/datasets/manasgarg/ipl

### "ModuleNotFoundError: No module named 'flask'"
Run: `pip install -r requirements_web.txt`

### Charts not showing
- Try refreshing browser (F5)
- Check browser console (F12 → Console)
- Verify API endpoint works: http://localhost:5000/api/summary

---

## Features

✅ Interactive dashboards
✅ 6 different analyses
✅ Real-time charts
✅ REST API
✅ Mobile responsive
✅ Fast & lightweight
✅ No database needed
✅ Windows native

---

## Next Steps

1. Run: `python start_web.py`
2. Visit: http://localhost:5000
3. Click "Dashboard" button
4. Explore tabs and charts
5. Try API endpoints
6. Share URL with others!

---

## Compare: CLI vs Web

| Aspect | Python CLI | Website |
|--------|-----------|---------|
| **Start** | `python run_all_multiprocessing.py` | `python start_web.py` |
| **Time** | 7 seconds | Instant |
| **Output** | 14 CSV files | Interactive charts |
| **Share** | Email CSVs | Share URL |
| **View** | Text/Excel | Beautiful dashboard |
| **Update** | Regenerate output | Auto-loads new data |

---

**Which to Use?**
- **Need raw data?** → Use Python CLI
- **Want dashboard?** → Use Website
- **Both!** → Run both (they use same data!)

---

## That's it! Start exploring! 🚀

Run: `python start_web.py`
