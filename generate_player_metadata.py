"""
Generate Player Metadata from IPL Data
Creates player_metadata.json with:
- Career stats (runs, wickets, matches, batting avg, strike rate, economy)
- Role detection (batsman, bowler, all-rounder)
- Teams played for (with years)
- Current team inference
- Wikipedia image URLs (cached)
"""

import pandas as pd
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import urllib.request
import urllib.error
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
DELIVERIES_CSV = 'datasets/deliveries.csv'
MATCHES_CSV = 'datasets/matches.csv'
OUTPUT_FILE = 'data/player_metadata.json'


class PlayerMetadataGenerator:
    """Generate comprehensive player metadata from IPL data"""

    def __init__(self):
        self.players = {}
        self.deliveries_df = None
        self.matches_df = None

    def load_data(self):
        """Load CSV datasets"""
        print("[INFO] Loading datasets...")
        self.deliveries_df = pd.read_csv(DELIVERIES_CSV)
        self.matches_df = pd.read_csv(MATCHES_CSV)
        print(f"[OK] Loaded {len(self.deliveries_df)} deliveries")
        print(f"[OK] Loaded {len(self.matches_df)} matches")

    def extract_all_players(self):
        """Extract unique players from deliveries"""
        print("\n[INFO] Extracting all players...")

        # Get all unique batsmen
        batsmen = set(self.deliveries_df['batsman'].unique())
        bowlers = set(self.deliveries_df['bowler'].unique())
        fielders = set(self.deliveries_df['fielder'].dropna().unique())

        # Combine all
        all_players = batsmen | bowlers | fielders

        # Remove any NaN values
        all_players = {p for p in all_players if pd.notna(p) and p != ''}

        print(f"[OK] Found {len(all_players)} unique players")
        print(f"     - Batsmen: {len(batsmen)}")
        print(f"     - Bowlers: {len(bowlers)}")
        print(f"     - Fielders: {len(fielders)}")

        return all_players

    def calculate_batting_stats(self, player_name: str) -> Dict:
        """Calculate batting statistics for a player"""
        # Filter deliveries where player is batting
        batting_df = self.deliveries_df[
            (self.deliveries_df['batsman'] == player_name) &
            (self.deliveries_df['is_super_over'] == 0) &
            (self.deliveries_df['wide_runs'] == 0)  # Wides don't count as balls
        ]

        if batting_df.empty:
            return {
                'total_runs': 0,
                'balls_faced': 0,
                'matches': 0,
                'centuries': 0,
                'fifties': 0,
                'batting_avg': 0,
                'strike_rate': 0,
                'highest_score': 0,
                'times_out': 0
            }

        # Group by match to get per-match stats
        match_stats = batting_df.groupby('match_id').agg({
            'batsman_runs': 'sum',
            'match_id': 'count',
            'player_dismissed': lambda x: (x.notna()).sum()
        }).rename(columns={
            'batsman_runs': 'runs',
            'match_id': 'balls'
        })

        total_runs = int(match_stats['runs'].sum())
        total_balls = int(match_stats['balls'].sum())
        matches = len(match_stats)
        centuries = int((match_stats['runs'] >= 100).sum())
        fifties = int(((match_stats['runs'] >= 50) & (match_stats['runs'] < 100)).sum())
        highest_score = int(match_stats['runs'].max())
        times_out = int(match_stats['player_dismissed'].sum())

        batting_avg = round(total_runs / max(times_out, 1), 2) if times_out > 0 else total_runs
        strike_rate = round(total_runs * 100 / max(total_balls, 1), 2) if total_balls > 0 else 0

        return {
            'total_runs': total_runs,
            'balls_faced': total_balls,
            'matches': matches,
            'centuries': centuries,
            'fifties': fifties,
            'batting_avg': batting_avg,
            'strike_rate': strike_rate,
            'highest_score': highest_score,
            'times_out': times_out
        }

    def calculate_bowling_stats(self, player_name: str) -> Dict:
        """Calculate bowling statistics for a player"""
        # Filter deliveries where player is bowling
        bowling_df = self.deliveries_df[
            (self.deliveries_df['bowler'] == player_name) &
            (self.deliveries_df['is_super_over'] == 0)
        ]

        if bowling_df.empty:
            return {
                'total_wickets': 0,
                'balls_bowled': 0,
                'runs_conceded': 0,
                'matches': 0,
                'bowling_avg': 0,
                'economy': 0,
                'best_figures': 0,
                '4_wicket_haul': 0,
                '5_wicket_haul': 0
            }

        # Calculate wickets
        wickets_df = bowling_df[bowling_df['player_dismissed'].notna()]
        total_wickets = len(wickets_df)

        # Group by match to get per-match stats
        match_stats = bowling_df.groupby('match_id').agg({
            'total_runs': 'sum',
            'match_id': 'count',  # balls bowled
            'player_dismissed': lambda x: (x.notna()).sum()
        }).rename(columns={
            'total_runs': 'runs',
            'match_id': 'balls',
            'player_dismissed': 'wickets'
        })

        total_balls = int(match_stats['balls'].sum())
        runs_conceded = int(match_stats['runs'].sum())
        matches = len(match_stats)
        best_figures = int(match_stats['wickets'].max())
        haul_4 = int((match_stats['wickets'] >= 4).sum())
        haul_5 = int((match_stats['wickets'] >= 5).sum())

        bowling_avg = round(runs_conceded / max(total_wickets, 1), 2) if total_wickets > 0 else 0
        overs = total_balls / 6.0  # 6 balls = 1 over
        economy = round(runs_conceded * 6 / max(total_balls, 1), 2) if total_balls > 0 else 0

        return {
            'total_wickets': total_wickets,
            'balls_bowled': total_balls,
            'runs_conceded': runs_conceded,
            'matches': matches,
            'bowling_avg': bowling_avg,
            'economy': economy,
            'best_figures': best_figures,
            '4_wicket_haul': haul_4,
            '5_wicket_haul': haul_5
        }

    def get_fielding_stats(self, player_name: str) -> Dict:
        """Calculate fielding statistics"""
        catches_df = self.deliveries_df[
            (self.deliveries_df['fielder'] == player_name) &
            (self.deliveries_df['dismissal_kind'] == 'caught')
        ]
        catches = len(catches_df)

        return {
            'catches': catches,
            'run_outs': 0  # Would need additional processing
        }

    def infer_player_role(self, player_name: str) -> str:
        """Infer player role (batsman, bowler, all-rounder)"""
        batting_stats = self.calculate_batting_stats(player_name)
        bowling_stats = self.calculate_bowling_stats(player_name)

        batting_matches = batting_stats['matches']
        bowling_matches = bowling_stats['matches']

        # Thresholds
        if batting_matches >= 5 and bowling_matches >= 3:
            return 'All-rounder'
        elif bowling_matches >= 5:
            return 'Bowler'
        elif batting_matches >= 5:
            return 'Batsman'
        elif bowling_matches > 0:
            return 'Bowler'
        else:
            return 'Batsman'

    def get_player_teams(self, player_name: str) -> List[str]:
        """Get all teams a player has played for"""
        # Check batting teams
        batting_teams = self.deliveries_df[
            self.deliveries_df['batsman'] == player_name
        ]['batting_team'].unique()

        # Check bowling teams (infer from match data)
        bowling_deliveries = self.deliveries_df[
            self.deliveries_df['bowler'] == player_name
        ]

        bowling_matches_ids = bowling_deliveries['match_id'].unique()
        bowling_teams = []
        if len(bowling_matches_ids) > 0:
            match_data = self.matches_df[
                self.matches_df['id'].isin(bowling_matches_ids)
            ]
            # Team2 is the bowling team (assumption based on typical format)
            bowling_teams = match_data['team2'].unique()

        teams = list(set(batting_teams) | set(bowling_teams))
        return sorted(teams)

    def get_current_team(self, player_name: str) -> str:
        """Get current team (last team player appeared for)"""
        # Get most recent match for this player
        player_deliveries = self.deliveries_df[
            (self.deliveries_df['batsman'] == player_name) |
            (self.deliveries_df['bowler'] == player_name)
        ]

        if player_deliveries.empty:
            return "Unknown"

        latest_match_id = player_deliveries['match_id'].max()
        match_info = self.matches_df[self.matches_df['id'] == latest_match_id]

        if match_info.empty:
            return "Unknown"

        # Determine if batting or bowling
        latest_batting = self.deliveries_df[
            (self.deliveries_df['batsman'] == player_name) &
            (self.deliveries_df['match_id'] == latest_match_id)
        ]

        if not latest_batting.empty:
            return latest_batting.iloc[0]['batting_team']

        return"Unknown"

    def get_wikipedia_image_url(self, player_name: str) -> str:
        """
        Get player image URL from Wikipedia
        Returns placeholder if not found
        """
        try:
            # Simple Wikipedia image URL generation (would need actual API call for production)
            # Using player name initials as fallback
            initials = ''.join([word[0].upper() for word in player_name.split()])
            return f"/static/player-avatars/{initials}.svg"  # Placeholder
        except Exception as e:
            print(f"[WARN] Could not fetch image for {player_name}: {e}")
            return "/static/default-avatar.svg"

    def get_player_nationality(self, player_name: str) -> str:
        """
        Get nationality (would require external data source)
        For now, using patterns or external mapping
        """
        # Known mappings (can be expanded)
        international_mapping = {
            'DA Warner': 'Australia',
            'S Dhawan': 'India',
            'V Kohli': 'India',
            'AB de Villiers': 'South Africa',
            'CH Gayle': 'West Indies',
            'MS Dhoni': 'India',
            'SK Warne': 'Australia',
            'L Malinga': 'Sri Lanka',
            'A Finch': 'Australia',
            'JE Root': 'England',
            'KA Pollard': 'West Indies',
            'SR Watson': 'Australia',
            'JH Kallis': 'South Africa',
        }

        # Try exact match
        if player_name in international_mapping:
            return international_mapping[player_name]

        # Default to India (most common)
        return 'India'

    def generate_player_metadata(self) -> Dict:
        """Generate complete metadata for all players"""
        print("\n[INFO] Generating player metadata...")

        all_players = self.extract_all_players()
        metadata = {}

        for idx, player_name in enumerate(sorted(all_players), 1):
            if idx % 500 == 0:
                print(f"[PROGRESS] Processing player {idx}/{len(all_players)}: {player_name}")

            batting_stats = self.calculate_batting_stats(player_name)
            bowling_stats = self.calculate_bowling_stats(player_name)
            fielding_stats = self.get_fielding_stats(player_name)
            role = self.infer_player_role(player_name)
            teams = self.get_player_teams(player_name)
            current_team = self.get_current_team(player_name)
            nationality = self.get_player_nationality(player_name)
            image_url = self.get_wikipedia_image_url(player_name)

            metadata[player_name] = {
                'nationality': nationality,
                'role': role,
                'current_team': current_team,
                'teams': teams,
                'image_url': image_url,
                'career_stats': {
                    'batting': batting_stats,
                    'bowling': bowling_stats,
                    'fielding': fielding_stats,
                    'matches_played': max(batting_stats['matches'], bowling_stats['matches'])
                }
            }

        print(f"\n[OK] Generated metadata for {len(metadata)} players")
        return metadata

    def save_metadata(self, metadata: Dict):
        """Save metadata to JSON file"""
        print(f"\n[INFO] Saving to {OUTPUT_FILE}...")

        Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved player metadata to {OUTPUT_FILE}")

    def run(self):
        """Execute full generation process"""
        print("\n" + "="*60)
        print("  IPL Player Metadata Generator")
        print("="*60 + "\n")

        try:
            self.load_data()
            metadata = self.generate_player_metadata()
            self.save_metadata(metadata)

            print("\n" + "="*60)
            print("  ✓ Player Metadata Generation Complete!")
            print("="*60 + "\n")

            return True
        except Exception as e:
            print(f"\n[ERROR] Failed to generate metadata: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    generator = PlayerMetadataGenerator()
    success = generator.run()
    sys.exit(0 if success else 1)
