"""
Analysis 4: Phase Analysis - Powerplay vs Middle vs Death
"""
import sys
import pandas as pd

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_phases(deliveries_df):
    """Analyze performance in Powerplay, Middle, and Death phases"""

    df = deliveries_df[deliveries_df['is_super_over'] == 0].copy()

    # Define phases based on over number
    def get_phase(over):
        if 1 <= over <= 6:
            return 'Powerplay'
        elif 7 <= over <= 15:
            return 'Middle'
        else:  # 16-20
            return 'Death'

    df['phase'] = df['over'].apply(get_phase)

    # Count dismissals
    df['is_dismissed'] = (df['player_dismissed'].notna()) & (df['player_dismissed'] != '')

    # Group by batting team and phase
    phases = df.groupby(['batting_team', 'phase']).agg({
        'total_runs': 'sum',
        'match_id': 'count',  # balls
        'is_dismissed': 'sum'  # wickets
    }).rename(columns={
        'total_runs': 'runs_scored',
        'match_id': 'balls_bowled',
        'is_dismissed': 'wickets_lost'
    })

    # Calculate run rate
    phases['run_rate'] = round((phases['runs_scored'] * 6.0 / phases['balls_bowled']), 2)

    result = phases.reset_index()
    result = result.sort_values(['batting_team', 'phase'])

    return result

if __name__ == "__main__":
    # Load data
    deliveries = pd.read_csv('datasets/deliveries.csv')

    # Run analysis
    result = analyze_phases(deliveries)

    # Save to CSV
    result.to_csv('output/04_phase_analysis.csv', index=False)

    print("\n=== Phase Analysis ===")
    print(result.to_string(index=False))
    print(f"\n[OK] Saved to output/04_phase_analysis.csv")
