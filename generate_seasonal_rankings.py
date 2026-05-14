"""
Generate Seasonal Rankings
Calculate top batsmen and bowlers for each season
"""

import pandas as pd
import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
DELIVERIES_CSV = 'datasets/deliveries.csv'
MATCHES_CSV = 'datasets/matches.csv'
OUTPUT_FILE = 'data/seasonal_rankings.json'


class SeasonalRankingsGenerator:
    """Generate season-wise player rankings"""

    def __init__(self):
        self.deliveries_df = None
        self.matches_df = None

    def load_data(self):
        """Load datasets"""
        print("[INFO] Loading data...")
        self.deliveries_df = pd.read_csv(DELIVERIES_CSV)
        self.matches_df = pd.read_csv(MATCHES_CSV)

        # Create season mapping from matches
        self.season_map = dict(zip(self.matches_df['id'], self.matches_df['season']))
        self.deliveries_df['season'] = self.deliveries_df['match_id'].map(self.season_map)

        print(f"[OK] Loaded {len(self.deliveries_df)} deliveries")
        print(f"[OK] Loaded {len(self.matches_df)} matches")

    def get_season_batsmen_rankings(self, season) -> list:
        """Get top 10 batsmen for a season"""
        season_data = self.deliveries_df[
            (self.deliveries_df['season'] == season) &
            (self.deliveries_df['wide_runs'] == 0) &
            (self.deliveries_df['is_super_over'] == 0)
        ]

        if season_data.empty:
            return []

        batsmen = season_data.groupby('batsman').agg({
            'batsman_runs': 'sum',
            'match_id': 'count'
        }).rename(columns={
            'batsman_runs': 'runs',
            'match_id': 'balls'
        })

        # Filter players with minimum 10 deliveries
        batsmen = batsmen[batsmen['balls'] >= 10]

        if batsmen.empty:
            return []

        batsmen['strike_rate'] = round(batsmen['runs'] * 100 / batsmen['balls'], 2)
        batsmen = batsmen.sort_values('runs', ascending=False).head(10).reset_index()

        return [
            {
                'rank': idx + 1,
                'name': row['batsman'],
                'runs': int(row['runs']),
                'matches': int(row['balls']),
                'strike_rate': row['strike_rate']
            }
            for idx, row in batsmen.iterrows()
        ]

    def get_season_bowlers_rankings(self, season) -> list:
        """Get top 10 bowlers for a season"""
        season_data = self.deliveries_df[
            (self.deliveries_df['season'] == season) &
            (self.deliveries_df['is_super_over'] == 0)
        ]

        if season_data.empty:
            return []

        # Count wickets
        dismissals = season_data[season_data['player_dismissed'].notna()]

        bowlers = dismissals.groupby('bowler').size().reset_index(name='wickets')

        if bowlers.empty:
            return []

        bowlers = bowlers.sort_values('wickets', ascending=False).head(10).reset_index(drop=True)

        return [
            {
                'rank': idx + 1,
                'name': row['bowler'],
                'wickets': int(row['wickets'])
            }
            for idx, row in bowlers.iterrows()
        ]

    def generate_all_rankings(self) -> dict:
        """Generate rankings for all seasons"""
        print("\n[INFO] Generating seasonal rankings...")

        seasons = sorted(self.deliveries_df['season'].unique())
        rankings = {}

        for season in seasons:
            print(f"[PROGRESS] Season {season}...", end="")

            batsmen = self.get_season_batsmen_rankings(season)
            bowlers = self.get_season_bowlers_rankings(season)

            rankings[int(season)] = {
                'top_batsmen': batsmen,
                'top_bowlers': bowlers
            }

            print(" ✓")

        print(f"\n[OK] Generated rankings for {len(rankings)} seasons")
        return rankings

    def save_rankings(self, rankings: dict):
        """Save rankings to JSON"""
        print(f"\n[INFO] Saving to {OUTPUT_FILE}...")

        Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(rankings, f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved seasonal rankings to {OUTPUT_FILE}")

    def run(self):
        """Execute generation"""
        print("\n" + "="*60)
        print("  IPL Seasonal Rankings Generator")
        print("="*60 + "\n")

        try:
            self.load_data()
            rankings = self.generate_all_rankings()
            self.save_rankings(rankings)

            print("\n" + "="*60)
            print("  ✓ Seasonal Rankings Generation Complete!")
            print("="*60 + "\n")

            return True
        except Exception as e:
            print(f"\n[ERROR] Failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    generator = SeasonalRankingsGenerator()
    success = generator.run()
    sys.exit(0 if success else 1)
