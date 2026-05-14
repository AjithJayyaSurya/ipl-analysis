"""
New Analytics API functions for IPL Big Data Project
All functions receive DATA dict (matches + deliveries DataFrames)
"""
import numpy as np
import traceback


def _deliveries(DATA):
    """Return deliveries filtered to non-super-overs."""
    df = DATA['deliveries'].copy()
    return df[df['is_super_over'] == 0]


def _matches(DATA):
    return DATA['matches'].copy()


# ─────────────────────────────────────────────
# 1. PLAYOFF RUN SCORERS
# ─────────────────────────────────────────────
def get_playoff_run_scorers(DATA):
    try:
        matches = _matches(DATA)
        deliveries = _deliveries(DATA)
        # Playoffs: semi-finals, finals — identified by match type or last matches per season
        # Use win_by_runs/win_by_wickets pattern: last 4 matches per season
        playoff_ids = []
        for season in matches['season'].unique():
            season_matches = matches[matches['season'] == season].sort_values('id')
            playoff_ids.extend(season_matches['id'].tail(4).tolist())

        df = deliveries[
            (deliveries['match_id'].isin(playoff_ids)) &
            (deliveries['wide_runs'] == 0)
        ]
        batsmen = df.groupby('batsman').agg(
            runs=('batsman_runs', 'sum'),
            balls=('batsman_runs', 'count'),
            matches=('match_id', 'nunique')
        ).reset_index()
        batsmen['strike_rate'] = round(batsmen['runs'] * 100 / batsmen['balls'], 2)
        batsmen = batsmen[batsmen['balls'] >= 30].sort_values('runs', ascending=False).head(20)
        return batsmen.to_dict('records')
    except Exception as e:
        traceback.print_exc()
        return []


# ─────────────────────────────────────────────
# 2. BATSMAN CONSISTENCY SCORE
# ─────────────────────────────────────────────
def get_batsman_consistency(DATA):
    try:
        deliveries = _deliveries(DATA)
        df = deliveries[deliveries['wide_runs'] == 0]

        innings = df.groupby(['match_id', 'batsman']).agg(
            runs=('batsman_runs', 'sum'),
            balls=('batsman_runs', 'count')
        ).reset_index()

        result = []
        for batsman, grp in innings.groupby('batsman'):
            if len(grp) < 10:
                continue
            runs_list = grp['runs'].tolist()
            avg = round(float(np.mean(runs_list)), 2)
            std = round(float(np.std(runs_list)), 2)
            freq_30 = round(len([r for r in runs_list if r >= 30]) / len(runs_list) * 100, 1)
            freq_50 = round(len([r for r in runs_list if r >= 50]) / len(runs_list) * 100, 1)
            consistency = round(max(0, 100 - (std / max(avg, 1)) * 50), 1)
            result.append({
                'batsman': batsman,
                'innings': len(runs_list),
                'avg': avg,
                'std_dev': std,
                'freq_30_plus': freq_30,
                'freq_50_plus': freq_50,
                'consistency_score': consistency
            })

        return sorted(result, key=lambda x: x['consistency_score'], reverse=True)[:25]
    except Exception as e:
        traceback.print_exc()
        return []


# ─────────────────────────────────────────────
# 3. PARTNERSHIP ANALYSIS
# ─────────────────────────────────────────────
def get_partnership_analysis(DATA):
    try:
        deliveries = _deliveries(DATA)
        df = deliveries[deliveries['wide_runs'] == 0].copy()

        pairs = df.groupby(['match_id', 'inning', 'batsman', 'non_striker']).agg(
            runs=('batsman_runs', 'sum')
        ).reset_index()

        # Normalise pair order
        pairs['p1'] = pairs[['batsman', 'non_striker']].min(axis=1)
        pairs['p2'] = pairs[['batsman', 'non_striker']].max(axis=1)

        agg = pairs.groupby(['p1', 'p2']).agg(
            total_runs=('runs', 'sum'),
            partnerships=('runs', 'count')
        ).reset_index()
        agg['avg_partnership'] = round(agg['total_runs'] / agg['partnerships'], 2)
        agg = agg[agg['partnerships'] >= 3].sort_values('total_runs', ascending=False).head(20)
        agg.rename(columns={'p1': 'player1', 'p2': 'player2'}, inplace=True)
        return agg.to_dict('records')
    except Exception as e:
        traceback.print_exc()
        return []


# ─────────────────────────────────────────────
# 4. PHASE SPECIALIST RANKINGS
# ─────────────────────────────────────────────
def _phase_batsmen(DATA, over_min, over_max, label):
    try:
        deliveries = _deliveries(DATA)
        df = deliveries[
            (deliveries['wide_runs'] == 0) &
            (deliveries['over'] >= over_min) &
            (deliveries['over'] <= over_max)
        ]
        batsmen = df.groupby('batsman').agg(
            runs=('batsman_runs', 'sum'),
            balls=('batsman_runs', 'count')
        ).reset_index()
        batsmen['strike_rate'] = round(batsmen['runs'] * 100 / batsmen['balls'], 2)
        batsmen = batsmen[batsmen['balls'] >= 50].sort_values('runs', ascending=False).head(15)
        return batsmen.to_dict('records')
    except Exception as e:
        traceback.print_exc()
        return []


def _phase_bowlers(DATA, over_min, over_max):
    try:
        deliveries = _deliveries(DATA)
        df = deliveries[
            (deliveries['over'] >= over_min) &
            (deliveries['over'] <= over_max)
        ]
        dismissed = df[
            df['player_dismissed'].notna() &
            (~df['dismissal_kind'].isin(['run out', 'retired hurt', 'obstructing the field']))
        ]
        wickets = dismissed.groupby('bowler').size().reset_index(name='wickets')

        legal = df[df['wide_runs'] == 0].groupby('bowler').agg(
            balls=('total_runs', 'count'),
            runs=('total_runs', 'sum')
        ).reset_index()
        legal['economy'] = round(legal['runs'] * 6 / legal['balls'], 2)

        merged = wickets.merge(legal, on='bowler')
        merged = merged[merged['balls'] >= 60].sort_values('wickets', ascending=False).head(15)
        return merged.to_dict('records')
    except Exception as e:
        traceback.print_exc()
        return []


def get_powerplay_batsmen(DATA):
    return _phase_batsmen(DATA, 1, 6, 'Powerplay')

def get_powerplay_bowlers(DATA):
    return _phase_bowlers(DATA, 1, 6)

def get_death_batsmen(DATA):
    return _phase_batsmen(DATA, 16, 20, 'Death')

def get_death_bowlers(DATA):
    return _phase_bowlers(DATA, 16, 20)

def get_middle_batsmen(DATA):
    return _phase_batsmen(DATA, 7, 15, 'Middle')

def get_middle_bowlers(DATA):
    return _phase_bowlers(DATA, 7, 15)


# ─────────────────────────────────────────────
# 5. SPINNER vs FAST BOWLER LEADERBOARD
# Uses player_metadata bowling style
# ─────────────────────────────────────────────
def get_spinner_vs_fast(DATA, PLAYER_METADATA):
    try:
        deliveries = _deliveries(DATA)
        dismissed = deliveries[
            deliveries['player_dismissed'].notna() &
            (~deliveries['dismissal_kind'].isin(['run out', 'retired hurt', 'obstructing the field']))
        ]
        wickets = dismissed.groupby('bowler').size().reset_index(name='wickets')

        legal = deliveries[deliveries['wide_runs'] == 0].groupby('bowler').agg(
            balls=('total_runs', 'count'),
            runs=('total_runs', 'sum')
        ).reset_index()
        legal['economy'] = round(legal['runs'] * 6 / legal['balls'], 2)

        merged = wickets.merge(legal, on='bowler')
        merged = merged[merged['balls'] >= 120]

        spinners, fast = [], []
        for _, row in merged.iterrows():
            meta = PLAYER_METADATA.get(row['bowler'], {})
            style = meta.get('role', '').lower()
            # Classify by name heuristics if metadata missing
            is_spinner = 'spin' in style or row['bowler'] in [
                'R Ashwin', 'SP Narine', 'A Mishra', 'PP Chawla', 'Harbhajan Singh',
                'RA Jadeja', 'PP Ojha', 'YS Chahal', 'Imran Tahir', 'SK Warne',
                'DL Vettori', 'M Muralitharan', 'A Kumble', 'J Botha', 'S Nadeem'
            ]
            entry = {
                'bowler': row['bowler'],
                'wickets': int(row['wickets']),
                'economy': float(row['economy']),
                'balls': int(row['balls'])
            }
            if is_spinner:
                spinners.append(entry)
            else:
                fast.append(entry)

        return {
            'spinners': sorted(spinners, key=lambda x: x['wickets'], reverse=True)[:15],
            'fast': sorted(fast, key=lambda x: x['wickets'], reverse=True)[:15]
        }
    except Exception as e:
        traceback.print_exc()
        return {'spinners': [], 'fast': []}


# ─────────────────────────────────────────────
# 6. BOWLER CONSISTENCY
# ─────────────────────────────────────────────
def get_bowler_consistency(DATA):
    try:
        deliveries = _deliveries(DATA)
        legal = deliveries[deliveries['wide_runs'] == 0]

        match_econ = legal.groupby(['match_id', 'bowler']).agg(
            balls=('total_runs', 'count'),
            runs=('total_runs', 'sum')
        ).reset_index()
        match_econ = match_econ[match_econ['balls'] >= 6]
        match_econ['economy'] = match_econ['runs'] * 6 / match_econ['balls']

        dismissed = deliveries[
            deliveries['player_dismissed'].notna() &
            (~deliveries['dismissal_kind'].isin(['run out', 'retired hurt', 'obstructing the field']))
        ]
        match_wkts = dismissed.groupby(['match_id', 'bowler']).size().reset_index(name='wickets')

        result = []
        for bowler, grp in match_econ.groupby('bowler'):
            if len(grp) < 8:
                continue
            econ_list = grp['economy'].tolist()
            wkt_grp = match_wkts[match_wkts['bowler'] == bowler]
            wkts_per_game = round(wkt_grp['wickets'].mean(), 2) if not wkt_grp.empty else 0
            econ_var = round(float(np.std(econ_list)), 2)
            avg_econ = round(float(np.mean(econ_list)), 2)
            consistency = round(max(0, 100 - econ_var * 15), 1)
            result.append({
                'bowler': bowler,
                'matches': len(grp),
                'avg_economy': avg_econ,
                'economy_std': econ_var,
                'wickets_per_game': float(wkts_per_game),
                'consistency_score': consistency
            })

        return sorted(result, key=lambda x: x['consistency_score'], reverse=True)[:25]
    except Exception as e:
        traceback.print_exc()
        return []


# ─────────────────────────────────────────────
# 7. AGE vs STRIKE RATE CURVE
# ─────────────────────────────────────────────
def get_age_vs_sr(DATA, PLAYER_METADATA):
    try:
        deliveries = _deliveries(DATA)
        matches = _matches(DATA)
        df = deliveries[deliveries['wide_runs'] == 0]

        season_sr = df.groupby(['match_id', 'batsman']).agg(
            runs=('batsman_runs', 'sum'),
            balls=('batsman_runs', 'count')
        ).reset_index()
        season_sr = season_sr.merge(matches[['id', 'season']], left_on='match_id', right_on='id')
        season_sr = season_sr[season_sr['balls'] >= 6]
        season_sr['sr'] = season_sr['runs'] * 100 / season_sr['balls']

        # Build age buckets 18-40
        age_data = {a: [] for a in range(18, 41)}
        for _, row in season_sr.iterrows():
            meta = PLAYER_METADATA.get(row['batsman'], {})
            # Estimate age from season (assume avg debut age ~22 for 2008)
            # We don't have DOB so use proxy: seasons_active index
            teams = meta.get('teams', [])
            if not teams:
                continue
            # Rough age estimate: 2008 = base, add season offset
            base_age = 24  # average IPL player age at 2008
            age = base_age + (int(row['season']) - 2008)
            if 18 <= age <= 40:
                age_data[age].append(row['sr'])

        result = []
        for age in range(18, 41):
            vals = age_data[age]
            if len(vals) >= 10:
                result.append({
                    'age': age,
                    'avg_sr': round(float(np.mean(vals)), 2),
                    'sample_size': len(vals)
                })
        return result
    except Exception as e:
        traceback.print_exc()
        return []


# ─────────────────────────────────────────────
# 8. AGE vs ECONOMY CURVE
# ─────────────────────────────────────────────
def get_age_vs_economy(DATA, PLAYER_METADATA):
    try:
        deliveries = _deliveries(DATA)
        matches = _matches(DATA)
        legal = deliveries[deliveries['wide_runs'] == 0]

        match_econ = legal.groupby(['match_id', 'bowler']).agg(
            balls=('total_runs', 'count'),
            runs=('total_runs', 'sum')
        ).reset_index()
        match_econ = match_econ.merge(matches[['id', 'season']], left_on='match_id', right_on='id')
        match_econ = match_econ[match_econ['balls'] >= 6]
        match_econ['economy'] = match_econ['runs'] * 6 / match_econ['balls']

        age_data = {a: [] for a in range(18, 41)}
        for _, row in match_econ.iterrows():
            base_age = 24
            age = base_age + (int(row['season']) - 2008)
            if 18 <= age <= 40:
                age_data[age].append(row['economy'])

        result = []
        for age in range(18, 41):
            vals = age_data[age]
            if len(vals) >= 10:
                result.append({
                    'age': age,
                    'avg_economy': round(float(np.mean(vals)), 2),
                    'sample_size': len(vals)
                })
        return result
    except Exception as e:
        traceback.print_exc()
        return []


# ─────────────────────────────────────────────
# 9. MVP PER SEASON
# ─────────────────────────────────────────────
def get_mvp_per_season(DATA):
    try:
        deliveries = _deliveries(DATA)
        matches = _matches(DATA)

        # Batting points: runs / 10 + (SR - 100) / 20 if SR > 100
        bat = deliveries[deliveries['wide_runs'] == 0].groupby(['match_id', 'batsman']).agg(
            runs=('batsman_runs', 'sum'),
            balls=('batsman_runs', 'count')
        ).reset_index()
        bat['sr'] = bat['runs'] * 100 / bat['balls'].clip(lower=1)
        bat['bat_pts'] = bat['runs'] / 10 + (bat['sr'] - 100).clip(lower=0) / 20

        # Bowling points: wickets * 20 - economy * 2
        dismissed = deliveries[
            deliveries['player_dismissed'].notna() &
            (~deliveries['dismissal_kind'].isin(['run out', 'retired hurt', 'obstructing the field']))
        ]
        wkts = dismissed.groupby(['match_id', 'bowler']).size().reset_index(name='wickets')
        legal = deliveries[deliveries['wide_runs'] == 0].groupby(['match_id', 'bowler']).agg(
            balls=('total_runs', 'count'),
            runs=('total_runs', 'sum')
        ).reset_index()
        legal['economy'] = legal['runs'] * 6 / legal['balls'].clip(lower=1)
        bowl = wkts.merge(legal, on=['match_id', 'bowler'], how='left').fillna(0)
        bowl['bowl_pts'] = bowl['wickets'] * 20 - bowl['economy'] * 2

        # Merge batting and bowling
        bat_s = bat.merge(matches[['id', 'season']], left_on='match_id', right_on='id')
        bowl_s = bowl.merge(matches[['id', 'season']], left_on='match_id', right_on='id')

        bat_season = bat_s.groupby(['season', 'batsman'])['bat_pts'].sum().reset_index()
        bat_season.rename(columns={'batsman': 'player', 'bat_pts': 'points'}, inplace=True)

        bowl_season = bowl_s.groupby(['season', 'bowler'])['bowl_pts'].sum().reset_index()
        bowl_season.rename(columns={'bowler': 'player', 'bowl_pts': 'points'}, inplace=True)

        combined = bat_season.merge(bowl_season, on=['season', 'player'], how='outer').fillna(0)
        combined['total_pts'] = combined['points_x'] + combined['points_y']

        result = []
        for season in sorted(combined['season'].unique()):
            top = combined[combined['season'] == season].sort_values('total_pts', ascending=False).iloc[0]
            result.append({
                'season': int(season),
                'mvp': top['player'],
                'points': round(float(top['total_pts']), 1)
            })
        return result
    except Exception as e:
        traceback.print_exc()
        return []


# ─────────────────────────────────────────────
# 10. PAR SCORE EVOLUTION
# ─────────────────────────────────────────────
def get_par_score_evolution(DATA):
    try:
        deliveries = _deliveries(DATA)
        matches = _matches(DATA)

        inn1 = deliveries[deliveries['inning'] == 1].groupby('match_id')['total_runs'].sum().reset_index()
        inn1.rename(columns={'total_runs': 'first_innings_score'}, inplace=True)
        inn1 = inn1.merge(matches[['id', 'season', 'winner', 'team1', 'team2']], left_on='match_id', right_on='id')

        # Determine if team batting first won
        bat_first = deliveries[deliveries['inning'] == 1].groupby('match_id')['batting_team'].first().reset_index()
        inn1 = inn1.merge(bat_first, on='match_id')
        inn1['bat_first_won'] = inn1['batting_team'] == inn1['winner']

        result = []
        for season in sorted(inn1['season'].unique()):
            s = inn1[inn1['season'] == season]
            result.append({
                'season': int(season),
                'avg_first_innings': round(float(s['first_innings_score'].mean()), 1),
                'winning_avg': round(float(s[s['bat_first_won']]['first_innings_score'].mean()), 1) if s['bat_first_won'].any() else 0,
                'matches': int(len(s))
            })
        return result
    except Exception as e:
        traceback.print_exc()
        return []


# ─────────────────────────────────────────────
# 11. VENUE BATTING vs BOWLING DOMINANCE
# ─────────────────────────────────────────────
def get_venue_dominance(DATA):
    try:
        deliveries = _deliveries(DATA)
        matches = _matches(DATA)

        inn_scores = deliveries.groupby('match_id')['total_runs'].sum().reset_index()
        inn_scores = inn_scores.merge(matches[['id', 'venue']], left_on='match_id', right_on='id')

        venue_stats = inn_scores.groupby('venue').agg(
            avg_score=('total_runs', 'mean'),
            matches=('match_id', 'nunique')
        ).reset_index()
        venue_stats = venue_stats[venue_stats['matches'] >= 5]
        overall_avg = float(venue_stats['avg_score'].mean())
        venue_stats['dominance'] = venue_stats['avg_score'].apply(
            lambda x: 'Batting' if x > overall_avg * 1.05 else ('Bowling' if x < overall_avg * 0.95 else 'Neutral')
        )
        venue_stats['avg_score'] = venue_stats['avg_score'].round(1)
        return venue_stats.sort_values('avg_score', ascending=False).to_dict('records')
    except Exception as e:
        traceback.print_exc()
        return []


# ─────────────────────────────────────────────
# 12. TOSS IMPACT ANALYSIS
# ─────────────────────────────────────────────
def get_toss_impact(DATA):
    try:
        matches = _matches(DATA)
        matches = matches.copy()
        matches['toss_winner_won'] = matches['toss_winner'] == matches['winner']

        overall_toss_win_pct = round(float(matches['toss_winner_won'].mean() * 100), 1)

        by_decision = matches.groupby('toss_decision')['toss_winner_won'].agg(['mean', 'count']).reset_index()
        by_decision['win_pct'] = (by_decision['mean'] * 100).round(1)

        by_venue = matches.groupby('venue').agg(
            toss_win_pct=('toss_winner_won', lambda x: round(x.mean() * 100, 1)),
            matches=('id', 'count')
        ).reset_index()
        by_venue = by_venue[by_venue['matches'] >= 5].sort_values('toss_win_pct', ascending=False)

        return {
            'overall_toss_win_pct': overall_toss_win_pct,
            'by_decision': by_decision[['toss_decision', 'win_pct', 'count']].to_dict('records'),
            'by_venue': by_venue.head(15).to_dict('records')
        }
    except Exception as e:
        traceback.print_exc()
        return {}


# ─────────────────────────────────────────────
# 13. CHASING vs DEFENDING WIN % PER TEAM
# ─────────────────────────────────────────────
def get_chasing_defending(DATA):
    try:
        deliveries = _deliveries(DATA)
        matches = _matches(DATA)

        bat_first = deliveries[deliveries['inning'] == 1].groupby('match_id')['batting_team'].first().reset_index()
        bat_first.rename(columns={'batting_team': 'team_bat_first'}, inplace=True)

        m = matches.merge(bat_first, left_on='id', right_on='match_id', how='left')

        result = []
        teams = sorted(matches['team1'].unique().tolist())
        for team in teams:
            team_m = m[(m['team1'] == team) | (m['team2'] == team)]
            defending = team_m[team_m['team_bat_first'] == team]
            chasing = team_m[team_m['team_bat_first'] != team]

            def_wins = len(defending[defending['winner'] == team])
            cha_wins = len(chasing[chasing['winner'] == team])

            result.append({
                'team': team,
                'defending_matches': int(len(defending)),
                'defending_wins': int(def_wins),
                'defending_win_pct': round(def_wins / len(defending) * 100, 1) if len(defending) > 0 else 0,
                'chasing_matches': int(len(chasing)),
                'chasing_wins': int(cha_wins),
                'chasing_win_pct': round(cha_wins / len(chasing) * 100, 1) if len(chasing) > 0 else 0,
            })
        return result
    except Exception as e:
        traceback.print_exc()
        return []


# ─────────────────────────────────────────────
# 14. BEST ALL-TIME XI
# ─────────────────────────────────────────────
def get_best_xi(DATA, PLAYER_METADATA):
    try:
        deliveries = _deliveries(DATA)

        # Batting scores
        bat = deliveries[deliveries['wide_runs'] == 0].groupby('batsman').agg(
            runs=('batsman_runs', 'sum'),
            balls=('batsman_runs', 'count'),
            matches=('match_id', 'nunique')
        ).reset_index()
        bat = bat[bat['matches'] >= 10]
        bat['sr'] = bat['runs'] * 100 / bat['balls'].clip(lower=1)
        bat['bat_score'] = bat['runs'] / 10 + (bat['sr'] - 100).clip(lower=0) / 20

        # Bowling scores
        dismissed = deliveries[
            deliveries['player_dismissed'].notna() &
            (~deliveries['dismissal_kind'].isin(['run out', 'retired hurt', 'obstructing the field']))
        ]
        wkts = dismissed.groupby('bowler').size().reset_index(name='wickets')
        legal = deliveries[deliveries['wide_runs'] == 0].groupby('bowler').agg(
            balls=('total_runs', 'count'),
            runs=('total_runs', 'sum'),
            matches=('match_id', 'nunique')
        ).reset_index()
        legal['economy'] = legal['runs'] * 6 / legal['balls'].clip(lower=1)
        bowl = wkts.merge(legal, on='bowler')
        bowl = bowl[bowl['matches'] >= 10]
        bowl['bowl_score'] = bowl['wickets'] * 20 - bowl['economy'] * 2

        # Merge
        merged = bat.merge(bowl, left_on='batsman', right_on='bowler', how='outer')
        merged['player'] = merged['batsman'].fillna(merged['bowler'])
        merged['bat_score'] = merged['bat_score'].fillna(0)
        merged['bowl_score'] = merged['bowl_score'].fillna(0)
        merged['total_score'] = merged['bat_score'] + merged['bowl_score']

        # Assign roles from metadata
        def get_role(name):
            meta = PLAYER_METADATA.get(name, {})
            return meta.get('role', 'Batsman')

        merged['role'] = merged['player'].apply(get_role)

        # Select XI: 5 batsmen, 1 wk, 2 all-rounders, 3 bowlers
        batsmen = merged[merged['role'].str.lower().isin(['batsman'])].sort_values('bat_score', ascending=False).head(5)
        wk = merged[merged['role'].str.lower().isin(['wicketkeeper'])].sort_values('total_score', ascending=False).head(1)
        allrounders = merged[merged['role'].str.lower().isin(['all-rounder'])].sort_values('total_score', ascending=False).head(2)
        bowlers = merged[merged['role'].str.lower().isin(['bowler'])].sort_values('bowl_score', ascending=False).head(3)

        xi = []
        for pos, grp in [('Batsman', batsmen), ('Wicketkeeper', wk), ('All-rounder', allrounders), ('Bowler', bowlers)]:
            for _, row in grp.iterrows():
                meta = PLAYER_METADATA.get(row['player'], {})
                xi.append({
                    'player': row['player'],
                    'position': pos,
                    'role': row['role'],
                    'bat_score': round(float(row['bat_score']), 1),
                    'bowl_score': round(float(row['bowl_score']), 1),
                    'total_score': round(float(row['total_score']), 1),
                    'current_team': meta.get('current_team', '—'),
                    'nationality': meta.get('nationality', '—'),
                    'image_url': meta.get('image_url', '')
                })
        return xi
    except Exception as e:
        traceback.print_exc()
        return []
