"""
Analysis 1: Top 20 Batsmen by Runs and Strike Rate
"""
import sys
import pandas as pd

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_top_batsmen(deliveries_df):
    """Find top 20 batsmen by total runs and strike rate"""

    # Filter out wides and super overs
    df = deliveries_df[
        (deliveries_df['wide_runs'] == 0) &
        (deliveries_df['is_super_over'] == 0)
    ].copy()

    # Group by batsman and calculate stats
    batsmen = df.groupby('batsman').agg({
        'batsman_runs': 'sum',
        'match_id': 'count'  # balls faced
    }).rename(columns={
        'batsman_runs': 'total_runs',
        'match_id': 'balls_faced'
    })

    # Calculate strike rate
    batsmen['strike_rate'] = round((batsmen['total_runs'] * 100.0 / batsmen['balls_faced']), 2)

    # Filter: only players who faced at least 100 balls
    batsmen = batsmen[batsmen['balls_faced'] >= 100]

    # Sort by total runs descending and get top 20
    result = batsmen.sort_values('total_runs', ascending=False).head(20)
    result = result[['total_runs', 'balls_faced', 'strike_rate']].reset_index()

    return result

if __name__ == "__main__":
    # Load data
    deliveries = pd.read_csv('datasets/deliveries.csv')

    # Run analysis
    result = analyze_top_batsmen(deliveries)

    # Save to CSV
    result.to_csv('output/01_top_batsmen.csv', index=False)

    print("\n=== Top 20 Batsmen ===")
    print(result.to_string(index=False))
    print(f"\n[OK] Saved to output/01_top_batsmen.csv")
