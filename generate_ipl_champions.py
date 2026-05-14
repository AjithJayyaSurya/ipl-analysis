"""
Generate IPL Champions Data
Extracts championship winners and details for each season
"""

import pandas as pd
import json
import sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
MATCHES_CSV = 'datasets/matches.csv'
OUTPUT_FILE = 'data/ipl_champions.json'


class IPLChampionsGenerator:
    """Generate IPL championship data"""

    def __init__(self):
        self.matches_df = None

    def load_data(self):
        """Load matches data"""
        print("[INFO] Loading matches data...")
        self.matches_df = pd.read_csv(MATCHES_CSV)
        print(f"[OK] Loaded {len(self.matches_df)} matches")

    def get_season_winner(self, season):
        """Get the IPL champion for a specific season"""
        # Filter matches for this season
        season_matches = self.matches_df[self.matches_df['season'] == season]

        if season_matches.empty:
            return None

        # The final match is typically the last one in the season
        # (matches are ordered by date, finals are at the end)
        # Group by season and get winner of last match
        final_matches = season_matches.sort_values('date', ascending=False).head(1)

        if not final_matches.empty:
            winner = final_matches.iloc[0]['winner']
            mvp = final_matches.iloc[0]['player_of_match']

            # Get runner-up: the other team in the final
            team1 = final_matches.iloc[0]['team1']
            team2 = final_matches.iloc[0]['team2']
            runner_up = team2 if winner == team1 else team1

            return {
                'champion': winner,
                'runner_up': runner_up,
                'finals_mvp': mvp,
                'final_date': final_matches.iloc[0]['date']
            }

        return None

    def identify_finals(self):
        """Identify all season finals more accurately"""
        champions = {}

        # Get unique seasons
        seasons = sorted(self.matches_df['season'].unique())

        print(f"\n[INFO] Processing {len(seasons)} seasons...")

        for season in seasons:
            print(f"[PROGRESS] Season {season}...", end=" ")

            season_data = self.get_season_winner(season)

            if season_data:
                champions[int(season)] = season_data
                print(f"✓ {season_data['champion']}")
            else:
                print("✗ Could not determine winner")

        return champions

    def add_statistics(self, champions: dict) -> dict:
        """Add championship statistics"""
        # Count titles by team
        team_titles = {}
        runner_up_count = {}

        for season, data in champions.items():
            champion = data['champion']
            runner_up = data['runner_up']

            team_titles[champion] = team_titles.get(champion, 0) + 1
            runner_up_count[runner_up] = runner_up_count.get(runner_up, 0) + 1

        # Sort teams by title count
        most_titles = sorted(team_titles.items(), key=lambda x: x[1], reverse=True)
        most_runner_up = sorted(runner_up_count.items(), key=lambda x: x[1], reverse=True)

        return {
            'champions': champions,
            'statistics': {
                'total_seasons': len(champions),
                'most_titles': dict(most_titles),
                'most_runner_up': dict(most_runner_up),
                'team_count': len(team_titles)
            }
        }

    def save_data(self, data: dict):
        """Save champions data to JSON"""
        print(f"\n[INFO] Saving to {OUTPUT_FILE}...")

        Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved IPL champions data to {OUTPUT_FILE}")

    def run(self):
        """Execute generation"""
        print("\n" + "="*60)
        print("  IPL Champions Generator")
        print("="*60 + "\n")

        try:
            self.load_data()
            champions = self.identify_finals()
            data = self.add_statistics(champions)
            self.save_data(data)

            print("\n" + "="*60)
            print("  ✓ IPL Champions Data Generation Complete!")
            print("="*60 + "\n")

            # Print summary
            stats = data['statistics']
            print(f"📊 Summary:")
            print(f"   Total Seasons: {stats['total_seasons']}")
            print(f"   Unique Teams: {stats['team_count']}")
            print(f"\n🏆 Most Titles:")
            for team, count in list(stats['most_titles'].items())[:3]:
                print(f"   {team}: {count} titles")

            return True
        except Exception as e:
            print(f"\n[ERROR] Failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    generator = IPLChampionsGenerator()
    success = generator.run()
    sys.exit(0 if success else 1)
