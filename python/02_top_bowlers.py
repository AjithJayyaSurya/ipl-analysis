"""
Analysis 2: Top 20 Bowlers by Wickets
"""
import sys
import pandas as pd

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_top_bowlers(deliveries_df):
    """Find top 20 bowlers by wickets (excluding run-outs)"""

    # Filter: player dismissed, not run-out, not super over
    df = deliveries_df[
        (deliveries_df['player_dismissed'].notna()) &
        (deliveries_df['player_dismissed'] != '') &
        (~deliveries_df['dismissal_kind'].isin(['run out', 'retired hurt', 'obstructing the field'])) &
        (deliveries_df['is_super_over'] == 0)
    ].copy()

    # Group by bowler and count wickets
    bowlers = df.groupby('bowler').size().reset_index(name='wickets')

    # Sort by wickets descending and get top 20
    result = bowlers.sort_values('wickets', ascending=False).head(20)

    return result

if __name__ == "__main__":
    # Load data
    deliveries = pd.read_csv('datasets/deliveries.csv')

    # Run analysis
    result = analyze_top_bowlers(deliveries)

    # Save to CSV
    result.to_csv('output/02_top_bowlers.csv', index=False)

    print("\n=== Top 20 Bowlers ===")
    print(result.to_string(index=False))
    print(f"\n[OK] Saved to output/02_top_bowlers.csv")
