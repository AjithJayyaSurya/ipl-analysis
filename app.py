"""
IPL Big Data Analytics - Flask Web Application (FIXED)
A web-based dashboard for IPL cricket analytics

Install: pip install -r requirements_web.txt
Run: python app.py
Access: http://localhost:5000
"""
import os
import sys
import pandas as pd
import json
import traceback
from pathlib import Path
from flask import Flask, render_template, jsonify, request, redirect, url_for
import analytics_api as aapi

# Force UTF-8 on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'ipl-analytics-2024'
app.config['JSON_SORT_KEYS'] = False

# Global data
DATA = {}
COLUMNS_INFO = {}
PLAYER_METADATA = {}
IPL_CHAMPIONS = {}
SEASONAL_RANKINGS = {}
PLAYER_RECORDS = {}

def load_data():
    """Load CSV data and JSON metadata into memory"""
    global DATA, COLUMNS_INFO, PLAYER_METADATA, IPL_CHAMPIONS, SEASONAL_RANKINGS, PLAYER_RECORDS
    try:
        print("[INFO] Loading datasets...")
        DATA['matches'] = pd.read_csv('datasets/matches.csv')
        DATA['deliveries'] = pd.read_csv('datasets/deliveries.csv')

        # Store column info for debugging
        COLUMNS_INFO['matches'] = list(DATA['matches'].columns)
        COLUMNS_INFO['deliveries'] = list(DATA['deliveries'].columns)

        print(f"[OK] Matches loaded: {len(DATA['matches'])} rows")
        print(f"[OK] Deliveries loaded: {len(DATA['deliveries'])} rows")

        # Load JSON metadata files
        print("[INFO] Loading player metadata...")
        if Path('data/player_metadata.json').exists():
            with open('data/player_metadata.json', 'r', encoding='utf-8') as f:
                PLAYER_METADATA.update(json.load(f))
            print(f"[OK] Player metadata loaded: {len(PLAYER_METADATA)} players")

        if Path('data/ipl_champions.json').exists():
            with open('data/ipl_champions.json', 'r', encoding='utf-8') as f:
                IPL_CHAMPIONS.update(json.load(f))
            print(f"[OK] IPL champions loaded")

        if Path('data/seasonal_rankings.json').exists():
            with open('data/seasonal_rankings.json', 'r', encoding='utf-8') as f:
                SEASONAL_RANKINGS.update(json.load(f))
            print(f"[OK] Seasonal rankings loaded")

        if Path('data/player_records.json').exists():
            with open('data/player_records.json', 'r', encoding='utf-8') as f:
                PLAYER_RECORDS.update(json.load(f))
            print(f"[OK] Player records loaded")

        return True
    except Exception as e:
        print(f"[ERROR] Failed to load data: {e}")
        traceback.print_exc()
        return False

# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def safe_api_call(func):
    """Decorator for safe API calls with error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[ERROR] in {func.__name__}: {e}")
            traceback.print_exc()
            return []
    return wrapper

@safe_api_call
def get_top_batsmen():
    """Get top 20 batsmen"""
    if 'deliveries' not in DATA or DATA['deliveries'].empty:
        return []

    deliveries = DATA['deliveries'].copy()

    # Filter wides and super overs
    df = deliveries[
        (deliveries.get('wide_runs', 0) == 0) &
        (deliveries.get('is_super_over', 0) == 0)
    ]

    if df.empty:
        return []

    batsmen = df.groupby('batsman').agg({
        'batsman_runs': 'sum',
        'match_id': 'count'
    }).reset_index().rename(columns={
        'batsman_runs': 'total_runs',
        'match_id': 'balls_faced'
    })

    batsmen['strike_rate'] = round((batsmen['total_runs'] * 100.0 / batsmen['balls_faced']), 2)
    batsmen = batsmen[batsmen['balls_faced'] >= 100]

    if batsmen.empty:
        return []

    result = batsmen.sort_values('total_runs', ascending=False).head(20)
    return result.to_dict('records')

@safe_api_call
def get_top_bowlers():
    """Get top 20 bowlers"""
    if 'deliveries' not in DATA or DATA['deliveries'].empty:
        return []

    deliveries = DATA['deliveries'].copy()
    df = deliveries[
        (deliveries['player_dismissed'].notna()) &
        (deliveries['player_dismissed'] != '') &
        (~deliveries['dismissal_kind'].isin(['run out', 'retired hurt', 'obstructing the field'])) &
        (deliveries.get('is_super_over', 0) == 0)
    ]

    if df.empty:
        return []

    bowlers = df.groupby('bowler').size().reset_index(name='wickets')
    result = bowlers.sort_values('wickets', ascending=False).head(20)
    return result.to_dict('records')

@safe_api_call
def get_team_stats():
    """Get team batting statistics"""
    if 'deliveries' not in DATA or DATA['deliveries'].empty:
        return []

    deliveries = DATA['deliveries'].copy()
    df = deliveries[deliveries.get('is_super_over', 0) == 0]

    if df.empty:
        return []

    teams = df.groupby('batting_team').agg({
        'total_runs': 'sum',
        'batsman_runs': 'sum',
        'extra_runs': 'sum',
        'match_id': 'count',
        'wide_runs': lambda x: (x > 0).sum()
    }).reset_index()

    teams.rename(columns={
        'total_runs': 'total_runs',
        'batsman_runs': 'bat_runs',
        'extra_runs': 'extras',
        'match_id': 'total_balls',
        'wide_runs': 'wide_count'
    }, inplace=True)

    teams['valid_balls'] = teams['total_balls'] - teams['wide_count']
    teams['run_rate'] = round((teams['total_runs'] * 6.0 / teams['valid_balls']), 2)

    result = teams[['batting_team', 'total_runs', 'bat_runs', 'extras', 'total_balls', 'run_rate']]
    result = result.sort_values('run_rate', ascending=False)
    return result.to_dict('records')

@safe_api_call
def get_phase_analysis():
    """Get phase-wise analysis"""
    if 'deliveries' not in DATA or DATA['deliveries'].empty:
        return []

    deliveries = DATA['deliveries'].copy()
    df = deliveries[deliveries.get('is_super_over', 0) == 0].copy()

    if df.empty:
        return []

    def get_phase(over):
        try:
            over = int(over)
            if 1 <= over <= 6:
                return 'Powerplay'
            elif 7 <= over <= 15:
                return 'Middle'
            else:
                return 'Death'
        except:
            return 'Unknown'

    df['phase'] = df['over'].apply(get_phase)
    df['is_dismissed'] = (df['player_dismissed'].notna()) & (df['player_dismissed'] != '')

    phases = df.groupby(['batting_team', 'phase']).agg({
        'total_runs': 'sum',
        'match_id': 'count',
        'is_dismissed': 'sum'
    }).reset_index()

    phases.rename(columns={
        'total_runs': 'runs_scored',
        'match_id': 'balls_bowled',
        'is_dismissed': 'wickets_lost'
    }, inplace=True)

    phases['run_rate'] = round((phases['runs_scored'] * 6.0 / phases['balls_bowled']), 2)
    phases = phases.sort_values(['batting_team', 'phase'])
    return phases.to_dict('records')

@safe_api_call
def get_dismissals():
    """Get dismissal types"""
    if 'deliveries' not in DATA or DATA['deliveries'].empty:
        return []

    deliveries = DATA['deliveries'].copy()
    df = deliveries[
        (deliveries['player_dismissed'].notna()) &
        (deliveries['player_dismissed'] != '')
    ]

    if df.empty:
        return []

    dismissals = df.groupby('dismissal_kind').size().reset_index(name='total_dismissals')
    total = dismissals['total_dismissals'].sum()

    if total > 0:
        dismissals['percentage'] = round((dismissals['total_dismissals'] * 100.0 / total), 2)
    else:
        dismissals['percentage'] = 0

    result = dismissals.sort_values('total_dismissals', ascending=False)
    return result.to_dict('records')

@safe_api_call
def get_top_fielders():
    """Get top fielders by catches"""
    if 'deliveries' not in DATA or DATA['deliveries'].empty:
        return []

    deliveries = DATA['deliveries'].copy()
    df = deliveries[
        (deliveries['dismissal_kind'] == 'caught') &
        (deliveries['fielder'].notna()) &
        (deliveries['fielder'] != '')
    ]

    if df.empty:
        return []

    fielders = df.groupby('fielder').size().reset_index(name='catches_taken')
    result = fielders.sort_values('catches_taken', ascending=False).head(15)
    return result.to_dict('records')

# ============================================================
# NEW PLAYER-CENTRIC FUNCTIONS
# ============================================================

@safe_api_call
def get_player_profile(player_name):
    """Get complete player profile"""
    if player_name not in PLAYER_METADATA:
        return None

    metadata = PLAYER_METADATA[player_name]
    return metadata

@safe_api_call
def get_player_comparison(players):
    """Compare multiple players"""
    if not isinstance(players, list) or len(players) < 2:
        return []

    comparison = []
    for player_name in players:
        if player_name not in PLAYER_METADATA:
            continue

        metadata = PLAYER_METADATA[player_name]
        stats = metadata.get('career_stats', {})

        comparison.append({
            'player': player_name,
            'nationality': metadata.get('nationality', 'Unknown'),
            'role': metadata.get('role', 'Unknown'),
            'current_team': metadata.get('current_team', 'Unknown'),
            'image_url': metadata.get('image_url', ''),
            'teams': metadata.get('teams', []),
            'career_stats': stats
        })

    return comparison

@safe_api_call
def get_player_head_to_head(player1, player2):
    """Get head-to-head stats between two players"""
    if 'deliveries' not in DATA or DATA['deliveries'].empty:
        return {}

    deliveries = DATA['deliveries'].copy()

    # Find matches where both players appeared
    p1_matches = set(deliveries[deliveries['batsman'] == player1]['match_id'].unique()) | \
                 set(deliveries[deliveries['bowler'] == player1]['match_id'].unique())

    p2_matches = set(deliveries[deliveries['batsman'] == player2]['match_id'].unique()) | \
                 set(deliveries[deliveries['bowler'] == player2]['match_id'].unique())

    common_matches = list(p1_matches & p2_matches)

    if not common_matches:
        return {'message': 'No common matches found'}

    # Get stats for common matches
    common_deliveries = deliveries[deliveries['match_id'].isin(common_matches)]

    p1_batting = common_deliveries[common_deliveries['batsman'] == player1]
    p1_runs = int(p1_batting['batsman_runs'].sum()) if not p1_batting.empty else 0
    p1_dismissals = len(p1_batting[p1_batting['player_dismissed'].notna()]) if not p1_batting.empty else 0

    p2_batting = common_deliveries[common_deliveries['batsman'] == player2]
    p2_runs = int(p2_batting['batsman_runs'].sum()) if not p2_batting.empty else 0
    p2_dismissals = len(p2_batting[p2_batting['player_dismissed'].notna()]) if not p2_batting.empty else 0

    return {
        'common_matches': len(common_matches),
        player1: {
            'runs': p1_runs,
            'dismissals': p1_dismissals
        },
        player2: {
            'runs': p2_runs,
            'dismissals': p2_dismissals
        }
    }

@safe_api_call
def get_ipl_champions():
    """Get IPL champions by year"""
    if not IPL_CHAMPIONS:
        return {}

    # Extract just the champions data
    champions_list = []
    if 'champions' in IPL_CHAMPIONS:
        for season, data in IPL_CHAMPIONS['champions'].items():
            champions_list.append({
                'season': int(season),
                'champion': data.get('champion', ''),
                'runner_up': data.get('runner_up', ''),
                'finals_mvp': data.get('finals_mvp', '')
            })

    return sorted(champions_list, key=lambda x: x['season'])

@safe_api_call
def get_seasonal_rankings(season=None):
    """Get seasonal rankings for a specific year"""
    if not SEASONAL_RANKINGS:
        return {}

    if season is None:
        return SEASONAL_RANKINGS

    season_str = str(season)
    if season_str in SEASONAL_RANKINGS:
        return SEASONAL_RANKINGS[season_str]

    return {}

@safe_api_call
def get_player_records():
    """Get all IPL records"""
    if not PLAYER_RECORDS:
        return {}

    return PLAYER_RECORDS

@safe_api_call
def search_player(query):
    """Search for player by name (partial match)"""
    if not query or len(query) < 2:
        return []

    query_lower = query.lower()
    matches = []

    for player_name in PLAYER_METADATA.keys():
        if query_lower in player_name.lower():
            metadata = PLAYER_METADATA[player_name]
            matches.append({
                'name': player_name,
                'role': metadata.get('role', 'Unknown'),
                'current_team': metadata.get('current_team', 'Unknown'),
                'nationality': metadata.get('nationality', 'Unknown'),
                'image_url': metadata.get('image_url', '')
            })

    return sorted(matches, key=lambda x: x['name'])[:20]  # Limit to 20 results

@safe_api_call
def get_performance_heatmap(player_name):
    """Get player performance heatmap (vs teams, venues, phases)"""
    if 'deliveries' not in DATA or DATA['deliveries'].empty:
        return {}

    deliveries = DATA['deliveries'].copy()

    # Performance vs teams (as batsman)
    batting_vs_teams = deliveries[
        (deliveries['batsman'] == player_name) &
        (deliveries['wide_runs'] == 0)
    ].groupby('bowling_team').agg({
        'batsman_runs': 'sum',
        'match_id': 'count'
    }).rename(columns={'batsman_runs': 'runs', 'match_id': 'balls'}).reset_index()

    batting_vs_teams['strike_rate'] = round(
        batting_vs_teams['runs'] * 100 / batting_vs_teams['balls'], 2
    )

    # Performance vs phases (as batsman)
    def get_phase(over):
        try:
            over = int(over)
            if 1 <= over <= 6:
                return 'Powerplay'
            elif 7 <= over <= 15:
                return 'Middle'
            else:
                return 'Death'
        except:
            return 'Unknown'

    batting_phase = deliveries[
        (deliveries['batsman'] == player_name) &
        (deliveries['wide_runs'] == 0)
    ].copy()

    if not batting_phase.empty:
        batting_phase['phase'] = batting_phase['over'].apply(get_phase)
        phase_stats = batting_phase.groupby('phase').agg({
            'batsman_runs': 'sum',
            'match_id': 'count'
        }).rename(columns={'batsman_runs': 'runs', 'match_id': 'balls'}).reset_index()

        phase_stats['strike_rate'] = round(
            phase_stats['runs'] * 100 / phase_stats['balls'], 2
        )
    else:
        phase_stats = []

    return {
        'vs_teams': batting_vs_teams.to_dict('records') if not batting_vs_teams.empty else [],
        'vs_phases': phase_stats.to_dict('records') if not isinstance(phase_stats, list) else phase_stats
    }

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Redirect to single-page app"""
    return redirect(url_for('index'))

@app.route('/unified')
def unified_dashboard():
    """Unified single-page dashboard"""
    return render_template('unified_dashboard.html')

# API Routes
@app.route('/api/top-batsmen')
def api_top_batsmen():
    """API: Top batsmen"""
    data = get_top_batsmen()
    return jsonify(data)

@app.route('/api/top-bowlers')
def api_top_bowlers():
    """API: Top bowlers"""
    data = get_top_bowlers()
    return jsonify(data)

@app.route('/api/team-stats')
def api_team_stats():
    """API: Team statistics"""
    data = get_team_stats()
    return jsonify(data)

@app.route('/api/phase-analysis')
def api_phase_analysis():
    """API: Phase analysis"""
    data = get_phase_analysis()
    return jsonify(data)

@app.route('/api/dismissals')
def api_dismissals():
    """API: Dismissals"""
    data = get_dismissals()
    return jsonify(data)

@app.route('/api/top-fielders')
def api_top_fielders():
    """API: Top fielders"""
    data = get_top_fielders()
    return jsonify(data)

@app.route('/api/summary')
def api_summary():
    """API: Summary statistics"""
    try:
        if not DATA or 'matches' not in DATA or 'deliveries' not in DATA:
            return jsonify({'error': 'Data not loaded'}), 500

        matches = DATA['matches']
        deliveries = DATA['deliveries']

        summary = {
            'total_matches': int(len(matches)),
            'total_deliveries': int(len(deliveries)),
            'total_teams': int(len(deliveries['batting_team'].unique())) if 'batting_team' in deliveries.columns else 0,
            'total_batsmen': int(len(deliveries['batsman'].unique())) if 'batsman' in deliveries.columns else 0,
            'total_bowlers': int(len(deliveries['bowler'].unique())) if 'bowler' in deliveries.columns else 0,
        }

        return jsonify(summary)
    except Exception as e:
        print(f"[ERROR] Summary API: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'data_loaded': len(DATA) > 0})

# ============================================================
# NEW PLAYER-CENTRIC API ENDPOINTS
# ============================================================

@app.route('/api/player/<player_name>')
def api_player_profile(player_name):
    """API: Get player profile"""
    data = get_player_profile(player_name)
    if data is None:
        return jsonify({'error': 'Player not found'}), 404
    return jsonify(data)

@app.route('/api/compare-players')
def api_compare_players():
    """API: Compare multiple players"""
    players = request.args.getlist('players')
    if not players:
        return jsonify({'error': 'No players specified'}), 400

    data = get_player_comparison(players)
    return jsonify(data)

@app.route('/api/player-head-to-head')
def api_head_to_head():
    """API: Head-to-head stats between two players"""
    player1 = request.args.get('player1')
    player2 = request.args.get('player2')

    if not player1 or not player2:
        return jsonify({'error': 'Both players required'}), 400

    data = get_player_head_to_head(player1, player2)
    return jsonify(data)

@app.route('/api/ipl-champions')
def api_champions():
    """API: IPL champions by year"""
    data = get_ipl_champions()
    return jsonify(data)

@app.route('/api/seasonal-rankings')
def api_rankings():
    """API: Seasonal rankings"""
    season = request.args.get('season', type=int)
    data = get_seasonal_rankings(season)
    return jsonify(data)

@app.route('/api/player-records')
def api_records():
    """API: Player records milestones"""
    data = get_player_records()
    return jsonify(data)

@app.route('/api/player-search')
def api_player_search():
    """API: Search for players"""
    query = request.args.get('q', '')
    data = search_player(query)
    return jsonify(data)

@app.route('/api/player-heatmap/<player_name>')
def api_heatmap(player_name):
    """API: Player performance heatmap"""
    data = get_performance_heatmap(player_name)
    return jsonify(data)

# ============================================================
# NEW PAGE ROUTES (Templates)
# ============================================================

@app.route('/player/<player_name>')
def player_profile(player_name):
    """Player profile page"""
    return render_template('player_profile.html', player_name=player_name)

@app.route('/compare')
def player_comparison():
    """Player comparison page"""
    return render_template('player_comparison.html')

@app.route('/rankings')
def player_rankings():
    """Seasonal rankings page"""
    return render_template('seasonal_rankings.html')

@app.route('/records')
def player_records_page():
    """Records page"""
    return render_template('player_records.html')

@app.route('/champions')
def champions_page():
    """IPL champions history page"""
    return render_template('ipl_champions.html')

@app.route('/player/<player_name>/performance')
def player_performance_page(player_name):
    """Player performance graphs page"""
    return render_template('player_performance.html', player_name=player_name)

@app.route('/venue-analysis')
def venue_analysis_page():
    """Venue-wise analysis page"""
    return render_template('venue_analysis.html')

@app.route('/team-comparison')
def team_comparison_page():
    """Team comparison page"""
    return render_template('team_comparison.html')

@app.route('/live')
def live_matches_page():
    """Live matches dashboard"""
    return render_template('live_matches.html')

# ============================================================
# VENUE-WISE ANALYSIS ENDPOINTS
# ============================================================

@app.route('/api/venue-stats')
def api_venue_stats():
    """Get all venue statistics"""
    try:
        if 'matches' not in DATA or DATA['matches'].empty:
            return jsonify([]), 200

        matches = DATA['matches']
        venue_stats = []

        for venue in matches['venue'].unique():
            venue_matches = matches[matches['venue'] == venue]
            venue_runs = DATA['deliveries'][
                DATA['deliveries']['match_id'].isin(venue_matches['id'])
            ]['total_runs'].sum()

            venue_stats.append({
                'venue': venue,
                'matches': int(len(venue_matches)),
                'total_runs': int(venue_runs),
                'avg_runs': round(venue_runs / len(venue_matches), 2) if len(venue_matches) > 0 else 0
            })

        return jsonify(sorted(venue_stats, key=lambda x: x['avg_runs'], reverse=True))
    except Exception as e:
        print(f"[ERROR] Venue stats: {e}")
        traceback.print_exc()
        return jsonify([]), 500

@app.route('/api/venue/<venue_name>')
def api_venue_details(venue_name):
    """Get specific venue details"""
    try:
        if 'matches' not in DATA or DATA['matches'].empty:
            return jsonify({})

        matches = DATA['matches'][DATA['matches']['venue'] == venue_name]

        if matches.empty:
            return jsonify({'error': 'Venue not found'}), 404

        top_performers = []
        for batsman in DATA['deliveries']['batsman'].unique():
            batsman_at_venue = DATA['deliveries'][
                (DATA['deliveries']['batsman'] == batsman) &
                (DATA['deliveries']['match_id'].isin(matches['id']))
            ]
            if len(batsman_at_venue) >= 10:
                runs = batsman_at_venue['batsman_runs'].sum()
                top_performers.append({
                    'player': batsman,
                    'runs': int(runs),
                    'matches': int(batsman_at_venue['match_id'].nunique())
                })

        return jsonify({
            'venue': venue_name,
            'total_matches': int(len(matches)),
            'top_performers': sorted(top_performers, key=lambda x: x['runs'], reverse=True)[:10]
        })
    except Exception as e:
        print(f"[ERROR] Venue details: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================
# TEAM COMPARISON ENDPOINTS
# ============================================================

@app.route('/api/compare-teams')
def api_compare_teams():
    """Compare multiple teams"""
    try:
        teams = request.args.getlist('teams')
        if len(teams) < 2:
            return jsonify({'error': 'Need at least 2 teams'}), 400

        comparison = []

        for team in teams:
            team_matches = DATA['matches'][(DATA['matches']['batting_team'] == team) |
                                          (DATA['matches']['bowling_team'] == team)]

            wins = len(team_matches[team_matches['winner'] == team])
            total = len(team_matches)
            win_rate = (wins / total * 100) if total > 0 else 0

            comparison.append({
                'team': team,
                'matches': int(total),
                'wins': int(wins),
                'win_rate': round(win_rate, 2)
            })

        return jsonify(comparison)
    except Exception as e:
        print(f"[ERROR] Compare teams: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/team/<team_name>/stats')
def api_team_details(team_name):
    """Get team statistics"""
    try:
        team_matches = DATA['matches'][(DATA['matches']['batting_team'] == team_name) |
                                       (DATA['matches']['bowling_team'] == team_name)]

        if team_matches.empty:
            return jsonify({'error': 'Team not found'}), 404

        wins = len(team_matches[team_matches['winner'] == team_name])
        total = len(team_matches)

        return jsonify({
            'team': team_name,
            'total_matches': int(total),
            'wins': int(wins),
            'losses': int(total - wins),
            'win_rate': round(wins / total * 100, 2) if total > 0 else 0
        })
    except Exception as e:
        print(f"[ERROR] Team stats: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================
# LIVE MATCHES ENDPOINTS
# ============================================================

@app.route('/api/live-matches')
def api_live_matches():
    """Get current live matches"""
    try:
        # For now, show recent matches as "live"
        if 'matches' not in DATA or DATA['matches'].empty:
            return jsonify([])

        recent_matches = DATA['matches'].tail(5)
        live_matches = []

        for _, match in recent_matches.iterrows():
            live_matches.append({
                'match_id': int(match['id']),
                'season': int(match['season']),
                'batting_team': match['batting_team'] if 'batting_team' in match else 'TBD',
                'bowling_team': match['bowling_team'] if 'bowling_team' in match else 'TBD',
                'winner': match['winner'] if 'winner' in match else 'In Progress'
            })

        return jsonify(live_matches)
    except Exception as e:
        print(f"[ERROR] Live matches: {e}")
        return jsonify([]), 500

@app.route('/api/live-scorecard/<int:match_id>')
def api_live_scorecard(match_id):
    """Get live match scorecard"""
    try:
        match = DATA['matches'][DATA['matches']['id'] == match_id]

        if match.empty:
            return jsonify({'error': 'Match not found'}), 404

        match_data = match.iloc[0]
        deliveries = DATA['deliveries'][DATA['deliveries']['match_id'] == match_id]

        return jsonify({
            'match_id': match_id,
            'season': int(match_data['season']),
            'batting_team': match_data['batting_team'] if 'batting_team' in match_data else 'TBD',
            'bowling_team': match_data['bowling_team'] if 'bowling_team' in match_data else 'TBD',
            'winner': match_data['winner'] if 'winner' in match_data else 'In Progress',
            'total_deliveries': int(len(deliveries))
        })
    except Exception as e:
        print(f"[ERROR] Live scorecard: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================
# ENHANCED PLAYER PERFORMANCE ENDPOINTS
# ============================================================

@app.route('/api/player-performance/<player_name>')
def api_player_performance(player_name):
    """Get player performance trends and statistics"""
    try:
        if player_name not in PLAYER_METADATA:
            return jsonify({'error': 'Player not found'}), 404

        metadata = PLAYER_METADATA[player_name]
        career_stats = metadata.get('career_stats', {})

        return jsonify({
            'player': player_name,
            'role': metadata.get('role', 'Unknown'),
            'batting_stats': career_stats.get('batting', {}),
            'bowling_stats': career_stats.get('bowling', {}),
            'fielding_stats': career_stats.get('fielding', {}),
            'teams': metadata.get('teams', []),
            'current_team': metadata.get('current_team', 'Unknown'),
            'nationality': metadata.get('nationality', 'Unknown')
        })
    except Exception as e:
        print(f"[ERROR] Player performance: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================
# EXPORT ENDPOINTS
# ============================================================

@app.route('/export/player/<player_name>/json')
def export_player_json(player_name):
    """Export player profile as JSON"""
    try:
        if player_name not in PLAYER_METADATA:
            return jsonify({'error': 'Player not found'}), 404

        data = PLAYER_METADATA[player_name]
        return jsonify(data)
    except Exception as e:
        print(f"[ERROR] Export player JSON: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/export/player/<player_name>/csv')
def export_player_csv(player_name):
    """Export player profile as CSV"""
    try:
        if player_name not in PLAYER_METADATA:
            return jsonify({'error': 'Player not found'}), 404

        metadata = PLAYER_METADATA[player_name]
        batting = metadata.get('career_stats', {}).get('batting', {})
        bowling = metadata.get('career_stats', {}).get('bowling', {})

        csv_content = f"""Player Name,{player_name}
Nationality,{metadata.get('nationality', 'N/A')}
Role,{metadata.get('role', 'N/A')}
Current Team,{metadata.get('current_team', 'N/A')}

BATTING STATISTICS
Total Runs,{batting.get('total_runs', 0)}
Balls Faced,{batting.get('balls_faced', 0)}
Matches,{batting.get('matches', 0)}
Batting Average,{batting.get('batting_avg', 0)}
Strike Rate,{batting.get('strike_rate', 0)}
Centuries,{batting.get('centuries', 0)}
Fifties,{batting.get('fifties', 0)}

BOWLING STATISTICS
Total Wickets,{bowling.get('total_wickets', 0)}
Runs Conceded,{bowling.get('runs_conceded', 0)}
Balls Bowled,{bowling.get('balls_bowled', 0)}
Bowling Average,{bowling.get('bowling_avg', 0)}
Economy Rate,{bowling.get('economy', 0)}
Best Figures,{bowling.get('best_figures', 0)}
"""
        return csv_content, 200, {
            'Content-Disposition': f'attachment; filename={player_name}_profile.csv',
            'Content-Type': 'text/csv'
        }
    except Exception as e:
        print(f"[ERROR] Export player CSV: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/export/season-rankings/json')
def export_rankings_json():
    """Export seasonal rankings as JSON"""
    try:
        return jsonify(SEASONAL_RANKINGS)
    except Exception as e:
        print(f"[ERROR] Export rankings JSON: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/export/top-records/json')
def export_records_json():
    """Export IPL records as JSON"""
    try:
        return jsonify(PLAYER_RECORDS)
    except Exception as e:
        print(f"[ERROR] Export records JSON: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================
# ERROR HANDLERS
# ============================================================

# ============================================================
# NEW ADVANCED ANALYTICS ENDPOINTS
# ============================================================

@app.route('/api/playoff-scorers')
def api_playoff_scorers():
    return jsonify(aapi.get_playoff_run_scorers(DATA))

@app.route('/api/batsman-consistency')
def api_batsman_consistency():
    return jsonify(aapi.get_batsman_consistency(DATA))

@app.route('/api/partnership-analysis')
def api_partnership_analysis():
    return jsonify(aapi.get_partnership_analysis(DATA))

@app.route('/api/powerplay-batsmen')
def api_powerplay_batsmen():
    return jsonify(aapi.get_powerplay_batsmen(DATA))

@app.route('/api/powerplay-bowlers')
def api_powerplay_bowlers():
    return jsonify(aapi.get_powerplay_bowlers(DATA))

@app.route('/api/death-batsmen')
def api_death_batsmen():
    return jsonify(aapi.get_death_batsmen(DATA))

@app.route('/api/death-bowlers')
def api_death_bowlers():
    return jsonify(aapi.get_death_bowlers(DATA))

@app.route('/api/middle-batsmen')
def api_middle_batsmen():
    return jsonify(aapi.get_middle_batsmen(DATA))

@app.route('/api/middle-bowlers')
def api_middle_bowlers():
    return jsonify(aapi.get_middle_bowlers(DATA))

@app.route('/api/spinner-vs-fast')
def api_spinner_vs_fast():
    return jsonify(aapi.get_spinner_vs_fast(DATA, PLAYER_METADATA))

@app.route('/api/bowler-consistency')
def api_bowler_consistency():
    return jsonify(aapi.get_bowler_consistency(DATA))

@app.route('/api/age-vs-sr')
def api_age_vs_sr():
    return jsonify(aapi.get_age_vs_sr(DATA, PLAYER_METADATA))

@app.route('/api/age-vs-economy')
def api_age_vs_economy():
    return jsonify(aapi.get_age_vs_economy(DATA, PLAYER_METADATA))

@app.route('/api/mvp-per-season')
def api_mvp_per_season():
    return jsonify(aapi.get_mvp_per_season(DATA))

@app.route('/api/par-score-evolution')
def api_par_score_evolution():
    return jsonify(aapi.get_par_score_evolution(DATA))

@app.route('/api/venue-dominance')
def api_venue_dominance():
    return jsonify(aapi.get_venue_dominance(DATA))

@app.route('/api/toss-impact')
def api_toss_impact():
    return jsonify(aapi.get_toss_impact(DATA))

@app.route('/api/chasing-defending')
def api_chasing_defending():
    return jsonify(aapi.get_chasing_defending(DATA))

@app.route('/api/best-xi')
def api_best_xi():
    return jsonify(aapi.get_best_xi(DATA, PLAYER_METADATA))

@app.route('/api/teams-list')
def api_teams_list():
    try:
        teams = sorted(DATA['matches']['team1'].unique().tolist())
        return jsonify(teams)
    except Exception as e:
        return jsonify([])

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  IPL Big Data Analytics - Web Application")
    print("="*60 + "\n")

    # Check datasets
    if not Path('datasets/matches.csv').exists() or not Path('datasets/deliveries.csv').exists():
        print("[ERROR] Datasets not found!")
        print("   Please download from: https://www.kaggle.com/datasets/manasgarg/ipl")
        print("   Place CSV files in: datasets/ folder")
        sys.exit(1)

    # Load data
    if not load_data():
        print("[ERROR] Failed to load data")
        sys.exit(1)

    print()
    print("[INFO] Starting web server...")
    print("[INFO] Access the app at: http://localhost:5000")
    print("[INFO] Press Ctrl+C to stop\n")

    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
