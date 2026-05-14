"""
Analysis 8: Inning Scores - Average, Max, Min
"""
import sys
import pandas as pd

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_inning_scores(deliveries_df):
    """Calculate inning-level score statistics"""

    df = deliveries_df[deliveries_df['is_super_over'] == 0].copy()

    # Calculate total runs per innings per match
    inning_totals = df.groupby(['match_id', 'inning']).agg({
        'total_runs': 'sum'
    }).reset_index()
    inning_totals.rename(columns={'total_runs': 'inning_total'}, inplace=True)

    # Group by inning and calculate stats
    stats = inning_totals.groupby('inning').agg({
        'inning_total': ['mean', 'max', 'min', 'count']
    }).reset_index()

    stats.columns = ['inning', 'avg_score', 'max_score', 'min_score', 'total_innings_played']
    stats['avg_score'] = round(stats['avg_score'], 2)

    return stats

def analyze_highest_innings(deliveries_df):
    """Bonus: Top 10 highest team innings scores"""

    df = deliveries_df[deliveries_df['is_super_over'] == 0].copy()

    highest = df.groupby(['match_id', 'inning', 'batting_team']).agg({
        'total_runs': 'sum'
    }).reset_index()
    highest.rename(columns={'total_runs': 'total_score'}, inplace=True)

    highest = highest.sort_values('total_score', ascending=False).head(10)

    return highest

if __name__ == "__main__":
    # Load data
    deliveries = pd.read_csv('datasets/deliveries.csv')

    # Run analysis
    stats = analyze_inning_scores(deliveries)
    highest = analyze_highest_innings(deliveries)

    # Save to CSV
    stats.to_csv('output/08_inning_scores.csv', index=False)
    highest.to_csv('output/08_highest_innings.csv', index=False)

    print("\n=== Inning Score Statistics ===")
    print(stats.to_string(index=False))
    print(f"\n[OK] Saved to output/08_inning_scores.csv")

    print("\n=== Top 10 Highest Team Innings ===")
    print(highest.to_string(index=False))
    print(f"\n[OK] Saved to output/08_highest_innings.csv")
