"""
Analysis 3: Team Batting Stats - Total Runs, Run Rate
"""
import sys
import pandas as pd

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_team_batting(deliveries_df):
    """Calculate team batting statistics including run rate"""

    df = deliveries_df[deliveries_df['is_super_over'] == 0].copy()

    # Group by batting team
    teams = df.groupby('batting_team').agg({
        'total_runs': 'sum',
        'batsman_runs': 'sum',
        'extra_runs': 'sum',
        'match_id': 'count',  # total balls
        'wide_runs': lambda x: (x > 0).sum()  # count of wides
    }).rename(columns={
        'total_runs': 'total_runs',
        'batsman_runs': 'bat_runs',
        'extra_runs': 'extras',
        'match_id': 'total_balls',
        'wide_runs': 'wide_count'
    })

    # Calculate run rate = (total_runs * 6) / (valid_balls)
    teams['valid_balls'] = teams['total_balls'] - teams['wide_count']
    teams['run_rate'] = round((teams['total_runs'] * 6.0 / teams['valid_balls']), 2)

    # Keep relevant columns
    result = teams[['total_runs', 'bat_runs', 'extras', 'total_balls', 'run_rate']].reset_index()
    result = result.sort_values('run_rate', ascending=False)

    return result

if __name__ == "__main__":
    # Load data
    deliveries = pd.read_csv('datasets/deliveries.csv')

    # Run analysis
    result = analyze_team_batting(deliveries)

    # Save to CSV
    result.to_csv('output/03_team_batting.csv', index=False)

    print("\n=== Team Batting Stats ===")
    print(result.to_string(index=False))
    print(f"\n[OK] Saved to output/03_team_batting.csv")
