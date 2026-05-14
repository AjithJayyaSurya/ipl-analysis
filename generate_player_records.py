"""
Generate Player Records
Extract record milestones (highest score, most wickets, fastest century, etc.)
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
OUTPUT_FILE = 'data/player_records.json'


class PlayerRecordsGenerator:
    """Generate IPL player records"""

    def __init__(self):
        self.deliveries_df = None
        self.matches_df = None

    def load_data(self):
        """Load datasets"""
        print("[INFO] Loading data...")
        self.deliveries_df = pd.read_csv(DELIVERIES_CSV)
        self.matches_df = pd.read_csv(MATCHES_CSV)
        print(f"[OK] Loaded {len(self.deliveries_df)} deliveries")

    def get_highest_individual_score(self) -> dict:
        """Get highest individual score in IPL"""
        # Group by match and batsman to get innings scores
        innings = self.deliveries_df[
            (self.deliveries_df['wide_runs'] == 0) &
            (self.deliveries_df['is_super_over'] == 0)
        ].groupby(['match_id', 'inning', 'batsman']).agg({
            'batsman_runs': 'sum',
            'batting_team': 'first',
            'bowling_team': 'first'
        }).reset_index().rename(columns={'batsman_runs': 'score'})

        highest = innings.nlargest(1, 'score').iloc[0]

        return {
            'player': str(highest['batsman']),
            'score': int(highest['score']),
            'match_id': int(highest['match_id']),
            'inning': int(highest['inning']),
            'batting_team': str(highest['batting_team']),
            'bowling_team': str(highest['bowling_team'])
        }

    def get_most_centuries(self) -> list:
        """Get players with most centuries"""
        innings = self.deliveries_df[
            (self.deliveries_df['wide_runs'] == 0) &
            (self.deliveries_df['is_super_over'] == 0)
        ].groupby(['match_id', 'inning', 'batsman']).agg({
            'batsman_runs': 'sum'
        }).reset_index().rename(columns={'batsman_runs': 'score'})

        centuries = innings[innings['score'] >= 100].groupby('batsman').size().reset_index(name='centuries')
        centuries = centuries.sort_values('centuries', ascending=False).head(15)

        return [
            {'player': row['batsman'], 'centuries': int(row['centuries'])}
            for _, row in centuries.iterrows()
        ]

    def get_most_fifties(self) -> list:
        """Get players with most fifties"""
        innings = self.deliveries_df[
            (self.deliveries_df['wide_runs'] == 0) &
            (self.deliveries_df['is_super_over'] == 0)
        ].groupby(['match_id', 'inning', 'batsman']).agg({
            'batsman_runs': 'sum'
        }).reset_index().rename(columns={'batsman_runs': 'score'})

        fifties = innings[(innings['score'] >= 50) & (innings['score'] < 100)].groupby('batsman').size().reset_index(name='fifties')
        fifties = fifties.sort_values('fifties', ascending=False).head(15)

        return [
            {'player': row['batsman'], 'fifties': int(row['fifties'])}
            for _, row in fifties.iterrows()
        ]

    def get_best_bowling_figures(self) -> dict:
        """Get best bowling figures in an innings"""
        bowling = self.deliveries_df[
            (self.deliveries_df['is_super_over'] == 0)
        ].groupby(['match_id', 'inning', 'bowler']).agg({
            'player_dismissed': lambda x: (x.notna()).sum(),
            'total_runs': 'sum',
            'bowling_team': 'first'
        }).reset_index().rename(columns={
            'player_dismissed': 'wickets',
            'total_runs': 'runs'
        })

        # Format as "X/Y" (wickets/runs)
        bowling['figures'] = bowling['wickets'].astype(str) + '/' + bowling['runs'].astype(str)
        best = bowling.nlargest(1, 'wickets').iloc[0]

        return {
            'player': str(best['bowler']),
            'wickets': int(best['wickets']),
            'runs': int(best['runs']),
            'figures': str(best['figures']),
            'match_id': int(best['match_id'])
        }

    def get_most_wickets(self) -> list:
        """Get bowlers with most total wickets"""
        dismissals = self.deliveries_df[
            (self.deliveries_df['player_dismissed'].notna()) &
            (self.deliveries_df['is_super_over'] == 0)
        ]

        bowlers = dismissals.groupby('bowler').size().reset_index(name='wickets')
        bowlers = bowlers.sort_values('wickets', ascending=False).head(15)

        return [
            {'player': row['bowler'], 'wickets': int(row['wickets'])}
            for _, row in bowlers.iterrows()
        ]

    def get_highest_strike_rate(self) -> list:
        """Get batsmen with highest strike rate (min 500 balls)"""
        batting = self.deliveries_df[
            (self.deliveries_df['wide_runs'] == 0) &
            (self.deliveries_df['is_super_over'] == 0)
        ].groupby('batsman').agg({
            'batsman_runs': 'sum',
            'match_id': 'count'
        }).rename(columns={
            'batsman_runs': 'runs',
            'match_id': 'balls'
        })

        batting = batting[batting['balls'] >= 500]
        batting['strike_rate'] = round(batting['runs'] * 100 / batting['balls'], 2)
        batting = batting.sort_values('strike_rate', ascending=False).head(10).reset_index()

        return [
            {'player': row['batsman'], 'strike_rate': row['strike_rate'], 'balls': int(row['balls'])}
            for _, row in batting.iterrows()
        ]

    def get_best_economy_rate(self) -> list:
        """Get bowlers with best economy rate (min 500 balls)"""
        bowling = self.deliveries_df[
            (self.deliveries_df['is_super_over'] == 0)
        ].groupby('bowler').agg({
            'total_runs': 'sum',
            'match_id': 'count'
        }).rename(columns={
            'total_runs': 'runs',
            'match_id': 'balls'
        })

        bowling = bowling[bowling['balls'] >= 500]
        bowling['economy'] = round(bowling['runs'] * 6 / bowling['balls'], 2)
        bowling = bowling.sort_values('economy', ascending=True).head(10).reset_index()

        return [
            {'player': row['bowler'], 'economy': row['economy'], 'balls': int(row['balls'])}
            for _, row in bowling.iterrows()
        ]

    def get_most_sixes(self) -> list:
        """Get players hitting most sixes"""
        sixes = self.deliveries_df[
            self.deliveries_df['batsman_runs'] == 6
        ].groupby('batsman').size().reset_index(name='sixes')

        sixes = sixes.sort_values('sixes', ascending=False).head(15)

        return [
            {'player': row['batsman'], 'sixes': int(row['sixes'])}
            for _, row in sixes.iterrows()
        ]

    def get_most_fours(self) -> list:
        """Get players hitting most fours"""
        fours = self.deliveries_df[
            self.deliveries_df['batsman_runs'] == 4
        ].groupby('batsman').size().reset_index(name='fours')

        fours = fours.sort_values('fours', ascending=False).head(15)

        return [
            {'player': row['batsman'], 'fours': int(row['fours'])}
            for _, row in fours.iterrows()
        ]

    def get_most_catches(self) -> list:
        """Get fielders with most catches"""
        catches = self.deliveries_df[
            (self.deliveries_df['dismissal_kind'] == 'caught') &
            (self.deliveries_df['fielder'].notna())
        ].groupby('fielder').size().reset_index(name='catches')

        catches = catches.sort_values('catches', ascending=False).head(15)

        return [
            {'player': row['fielder'], 'catches': int(row['catches'])}
            for _, row in catches.iterrows()
        ]

    def generate_all_records(self) -> dict:
        """Generate all records"""
        print("\n[INFO] Generating records...")

        records = {
            'highest_individual_score': self.get_highest_individual_score(),
            'most_centuries': self.get_most_centuries(),
            'most_fifties': self.get_most_fifties(),
            'best_bowling_figures': self.get_best_bowling_figures(),
            'most_wickets': self.get_most_wickets(),
            'highest_strike_rate': self.get_highest_strike_rate(),
            'best_economy_rate': self.get_best_economy_rate(),
            'most_sixes': self.get_most_sixes(),
            'most_fours': self.get_most_fours(),
            'most_catches': self.get_most_catches()
        }

        print("[OK] Records generated")
        return records

    def save_records(self, records: dict):
        """Save records to JSON"""
        print(f"\n[INFO] Saving to {OUTPUT_FILE}...")

        Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved player records to {OUTPUT_FILE}")

    def run(self):
        """Execute generation"""
        print("\n" + "="*60)
        print("  IPL Player Records Generator")
        print("="*60 + "\n")

        try:
            self.load_data()
            records = self.generate_all_records()
            self.save_records(records)

            print("\n" + "="*60)
            print("  ✓ Player Records Generation Complete!")
            print("="*60 + "\n")

            print("📊 Summary:")
            print(f"   Highest Score: {records['highest_individual_score']['score']} by {records['highest_individual_score']['player']}")
            print(f"   Most Centuries: {records['most_centuries'][0]['player']} ({records['most_centuries'][0]['centuries']})")
            print(f"   Most Wickets: {records['most_wickets'][0]['player']} ({records['most_wickets'][0]['wickets']})")

            return True
        except Exception as e:
            print(f"\n[ERROR] Failed: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    generator = PlayerRecordsGenerator()
    success = generator.run()
    sys.exit(0 if success else 1)
