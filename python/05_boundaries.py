"""
Analysis 5: Boundaries - Fours and Sixes
"""
import sys
import pandas as pd

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_boundaries(deliveries_df):
    """Analyze boundaries (4s and 6s) by batsman"""

    df = deliveries_df[deliveries_df['is_super_over'] == 0].copy()

    # Count 4s and 6s
    boundaries = df.groupby('batsman').agg({
        'batsman_runs': [
            lambda x: (x == 4).sum(),  # fours
            lambda x: (x == 6).sum(),  # sixes
            lambda x: ((x == 4) | (x == 6)).sum(),  # total boundaries
        ]
    })

    # Calculate boundary runs
    df['boundary_runs'] = df['batsman_runs'].apply(
        lambda x: x if x in [4, 6] else 0
    )
    boundary_run_sums = df.groupby('batsman')['boundary_runs'].sum()

    # Flatten column names
    boundaries.columns = ['fours', 'sixes', 'total_boundaries']
    boundaries['boundary_runs'] = boundary_run_sums

    result = boundaries.reset_index()
    result = result.sort_values('total_boundaries', ascending=False).head(20)

    return result

if __name__ == "__main__":
    # Load data
    deliveries = pd.read_csv('datasets/deliveries.csv')

    # Run analysis
    result = analyze_boundaries(deliveries)

    # Save to CSV
    result.to_csv('output/05_boundaries.csv', index=False)

    print("\n=== Top Boundaries (4s & 6s) ===")
    print(result.to_string(index=False))
    print(f"\n[OK] Saved to output/05_boundaries.csv")
