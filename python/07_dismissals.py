"""
Analysis 7: Dismissal Types Distribution
"""
import sys
import pandas as pd

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_dismissals(deliveries_df):
    """Analyze dismissal types and their frequency"""

    df = deliveries_df[
        (deliveries_df['player_dismissed'].notna()) &
        (deliveries_df['player_dismissed'] != '')
    ].copy()

    # Count dismissals by type
    dismissals = df.groupby('dismissal_kind').size().reset_index(name='total_dismissals')

    # Calculate percentage
    total = dismissals['total_dismissals'].sum()
    dismissals['percentage'] = round((dismissals['total_dismissals'] * 100.0 / total), 2)

    # Sort by count descending
    dismissals = dismissals.sort_values('total_dismissals', ascending=False)

    return dismissals

def analyze_fielders(deliveries_df):
    """Bonus: Top fielders by catches"""

    df = deliveries_df[
        (deliveries_df['dismissal_kind'] == 'caught') &
        (deliveries_df['fielder'].notna()) &
        (deliveries_df['fielder'] != '')
    ].copy()

    # Count catches by fielder
    fielders = df.groupby('fielder').size().reset_index(name='catches_taken')
    fielders = fielders.sort_values('catches_taken', ascending=False).head(15)

    return fielders

if __name__ == "__main__":
    # Load data
    deliveries = pd.read_csv('datasets/deliveries.csv')

    # Run analysis
    dismissals = analyze_dismissals(deliveries)
    fielders = analyze_fielders(deliveries)

    # Save to CSV
    dismissals.to_csv('output/07_dismissals.csv', index=False)
    fielders.to_csv('output/07_top_fielders.csv', index=False)

    print("\n=== Dismissal Types ===")
    print(dismissals.to_string(index=False))
    print(f"\n[OK] Saved to output/07_dismissals.csv")

    print("\n=== Top Fielders ===")
    print(fielders.to_string(index=False))
    print(f"\n[OK] Saved to output/07_top_fielders.csv")
