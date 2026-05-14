"""
Analysis 9: Economy Rates - Best Bowlers
"""
import sys
import pandas as pd

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_economy(deliveries_df):
    """Analyze economy rates for bowlers with min 100 overs"""

    df = deliveries_df[
        (deliveries_df['is_super_over'] == 0) &
        (deliveries_df['wide_runs'] == 0)  # legal deliveries only
    ].copy()

    # Count dismissals
    df['is_dismissed'] = (
        (df['player_dismissed'].notna()) &
        (df['player_dismissed'] != '') &
        (~df['dismissal_kind'].isin(['run out', 'retired hurt']))
    )

    # Group by bowler
    bowlers = df.groupby('bowler').agg({
        'match_id': 'count',  # legal balls
        'total_runs': 'sum',
        'is_dismissed': 'sum'  # wickets
    }).rename(columns={
        'match_id': 'legal_balls',
        'total_runs': 'runs_conceded',
        'is_dismissed': 'wickets'
    })

    # Calculate overs and economy
    bowlers['overs_bowled'] = round(bowlers['legal_balls'] / 6.0, 1)
    bowlers['economy_rate'] = round((bowlers['runs_conceded'] * 6.0 / bowlers['legal_balls']), 2)

    # Filter: minimum 100 overs (600 legal balls)
    bowlers = bowlers[bowlers['legal_balls'] >= 600]

    result = bowlers.reset_index()
    result = result.sort_values('economy_rate', ascending=True).head(20)
    result = result[['bowler', 'legal_balls', 'overs_bowled', 'runs_conceded', 'economy_rate', 'wickets']]

    return result

if __name__ == "__main__":
    # Load data
    deliveries = pd.read_csv('datasets/deliveries.csv')

    # Run analysis
    result = analyze_economy(deliveries)

    # Save to CSV
    result.to_csv('output/09_economy.csv', index=False)

    print("\n=== Economy Rates (Min 100 Overs) ===")
    print(result.to_string(index=False))
    print(f"\n[OK] Saved to output/09_economy.csv")
