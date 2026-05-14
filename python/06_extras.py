"""
Analysis 6: Extras - Bowling Discipline
"""
import sys
import pandas as pd

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_extras(deliveries_df):
    """Analyze extras conceded by bowling team"""

    df = deliveries_df[deliveries_df['is_super_over'] == 0].copy()

    # Group by bowling team
    extras = df.groupby('bowling_team').agg({
        'wide_runs': 'sum',
        'noball_runs': 'sum',
        'bye_runs': 'sum',
        'legbye_runs': 'sum',
        'extra_runs': 'sum',
        'match_id': 'count'  # total balls bowled
    }).rename(columns={
        'wide_runs': 'total_wides',
        'noball_runs': 'total_no_balls',
        'bye_runs': 'total_byes',
        'legbye_runs': 'total_leg_byes',
        'extra_runs': 'total_extras',
        'match_id': 'total_balls_bowled'
    })

    # Calculate extras per 100 balls (discipline metric - lower is better)
    extras['extras_per_100_balls'] = round(
        (extras['total_extras'] * 100.0 / extras['total_balls_bowled']), 2
    )

    result = extras.reset_index()
    result = result.sort_values('extras_per_100_balls', ascending=True)

    return result

if __name__ == "__main__":
    # Load data
    deliveries = pd.read_csv('datasets/deliveries.csv')

    # Run analysis
    result = analyze_extras(deliveries)

    # Save to CSV
    result.to_csv('output/06_extras.csv', index=False)

    print("\n=== Extras - Bowling Discipline ===")
    print(result.to_string(index=False))
    print(f"\n[OK] Saved to output/06_extras.csv")
