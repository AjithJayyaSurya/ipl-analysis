"""
Analysis 10: Head-to-Head Team Comparison
"""
import sys
import pandas as pd

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_head_to_head_runs(deliveries_df):
    """Analyze run rate of each team vs each opponent"""

    df = deliveries_df[deliveries_df['is_super_over'] == 0].copy()

    # Group by batting team and bowling team
    h2h = df.groupby(['batting_team', 'bowling_team']).agg({
        'match_id': 'nunique',  # matches played
        'total_runs': 'sum'
    }).rename(columns={
        'match_id': 'matches_played',
        'total_runs': 'total_runs_scored'
    })

    # Add run rate
    ball_count = df.groupby(['batting_team', 'bowling_team']).size().reset_index(name='ball_count')
    h2h = h2h.reset_index()
    h2h = h2h.merge(ball_count, on=['batting_team', 'bowling_team'])

    h2h['run_rate'] = round((h2h['total_runs_scored'] * 6.0 / h2h['ball_count']), 2)

    result = h2h[['batting_team', 'bowling_team', 'matches_played', 'total_runs_scored', 'run_rate']]
    result.columns = ['team', 'opponent', 'matches_played', 'total_runs_scored', 'run_rate']
    result = result.sort_values(['team', 'run_rate'], ascending=[True, False])

    return result

def analyze_head_to_head_wins(matches_df):
    """Analyze wins between teams"""

    df = matches_df[matches_df['result'] == 'normal'].copy()

    wins = df.groupby(['team1', 'team2', 'winner']).size().reset_index(name='wins')
    wins.columns = ['team1', 'team2', 'winner', 'wins']
    wins = wins.sort_values(['team1', 'wins'], ascending=[True, False])

    return wins

def analyze_season_wins(matches_df):
    """Analyze wins per team per season"""

    df = matches_df[
        (matches_df['winner'].notna()) &
        (matches_df['winner'] != '')
    ].copy()

    season_wins = df.groupby(['season', 'winner']).size().reset_index(name='wins')
    season_wins.columns = ['season', 'winner', 'wins']
    season_wins = season_wins.sort_values(['season', 'wins'], ascending=[True, False])

    return season_wins

if __name__ == "__main__":
    # Load data
    deliveries = pd.read_csv('datasets/deliveries.csv')
    matches = pd.read_csv('datasets/matches.csv')

    # Run analysis
    h2h_runs = analyze_head_to_head_runs(deliveries)
    h2h_wins = analyze_head_to_head_wins(matches)
    season_wins = analyze_season_wins(matches)

    # Save to CSV
    h2h_runs.to_csv('output/10_head_to_head_runs.csv', index=False)
    h2h_wins.to_csv('output/10_head_to_head_wins.csv', index=False)
    season_wins.to_csv('output/10_season_wins.csv', index=False)

    print("\n=== Head-to-Head: Run Rates ===")
    print(h2h_runs.head(15).to_string(index=False))
    print(f"\n[OK] Saved to output/10_head_to_head_runs.csv")

    print("\n=== Head-to-Head: Wins ===")
    print(h2h_wins.head(15).to_string(index=False))
    print(f"\n[OK] Saved to output/10_head_to_head_wins.csv")

    print("\n=== Season Wins ===")
    print(season_wins.head(15).to_string(index=False))
    print(f"\n[OK] Saved to output/10_season_wins.csv")
