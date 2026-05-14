/* ═══════════════════════════════════════════════════════════
   IPL Analytics Pro — Main JavaScript
   Plotly dark/light theme helpers + all data loaders
═══════════════════════════════════════════════════════════ */

/* ── Theme ── */
let DARK = true;

function getPlotlyTheme() {
  return DARK ? {
    paper_bgcolor: '#1e293b', plot_bgcolor: '#0f172a',
    font: { color: '#94a3b8', size: 11 },
    gridcolor: '#334155', linecolor: '#334155'
  } : {
    paper_bgcolor: '#ffffff', plot_bgcolor: '#f8fafc',
    font: { color: '#475569', size: 11 },
    gridcolor: '#e2e8f0', linecolor: '#e2e8f0'
  };
}

function layout(title, extra) {
  const t = getPlotlyTheme();
  return Object.assign({
    title: { text: title, font: { size: 14, color: t.font.color } },
    paper_bgcolor: t.paper_bgcolor, plot_bgcolor: t.plot_bgcolor,
    font: t.font,
    xaxis: { gridcolor: t.gridcolor, linecolor: t.linecolor, tickangle: -35 },
    yaxis: { gridcolor: t.gridcolor, linecolor: t.linecolor },
    margin: { t: 50, b: 110, l: 55, r: 20 },
    autosize: true
  }, extra || {});
}

function toggleTheme() {
  DARK = !DARK;
  document.documentElement.setAttribute('data-theme', DARK ? 'dark' : 'light');
  document.getElementById('theme-btn').textContent = DARK ? '☀️ Light' : '🌙 Dark';
  // Re-render any visible charts
  document.querySelectorAll('.js-plotly-plot').forEach(el => {
    try { Plotly.relayout(el, { paper_bgcolor: getPlotlyTheme().paper_bgcolor, plot_bgcolor: getPlotlyTheme().plot_bgcolor }); } catch(e) {}
  });
}

/* ── Colours ── */
const C = {
  gold: '#F5A623', blue: '#004BA0', lblue: '#3b82f6',
  green: '#10b981', orange: '#f59e0b', red: '#ef4444',
  teal: '#06b6d4', purple: '#8b5cf6', pink: '#ec4899'
};
const PALETTE = [C.gold, C.lblue, C.green, C.orange, C.red, C.teal, C.purple, C.pink];

/* ── Helpers ── */
const $ = id => document.getElementById(id);
const api = url => fetch(url).then(r => r.json()).catch(() => []);

function tbl(headers, rows, classes) {
  const cls = classes || [];
  return `<table><thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
  <tbody>${rows.map(r => `<tr>${r.map((c, i) => `<td class="${cls[i] || ''}">${c}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}

function initials(name) {
  return (name || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

function avatar(name, size) {
  const s = size || 48;
  return `<div class="pcc-avatar" style="width:${s}px;height:${s}px;font-size:${Math.round(s*0.35)}px">${initials(name)}</div>`;
}

/* ── Tab switching ── */
const topLoaded = {};

function switchTop(name) {
  document.querySelectorAll('.ttab').forEach(b => b.classList.toggle('active', b.dataset.top === name));
  document.querySelectorAll('.tpane').forEach(p => p.classList.toggle('active', p.id === 'pane-' + name));
  document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
  const nav = $('nav-' + name);
  if (nav) nav.classList.add('active');
  document.querySelector('.main').scrollIntoView({ behavior: 'smooth', block: 'start' });
  if (!topLoaded[name]) {
    topLoaded[name] = true;
    const loaders = {
      advanced: loadAdvancedDefault,
      compare: initCompare,
      rankings: loadRankings,
      records: loadRecords,
      champions: loadChampions,
      bestxi: loadBestXI,
      teams: loadTeamsDefault
    };
    if (loaders[name]) loaders[name]();
  }
}

/* Inner tab switching (generic) */
function setupInnerTabs(containerSelector) {
  document.querySelectorAll(containerSelector + ' .itab').forEach(btn => {
    btn.addEventListener('click', () => {
      const pane = btn.dataset.it;
      const parent = btn.closest('.tpane, .ipane, .card, .top-tab-content');
      parent.querySelectorAll('.itab').forEach(b => b.classList.remove('active'));
      parent.querySelectorAll('.ipane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const el = $('it-' + pane);
      if (el) el.classList.add('active');
    });
  });
}

/* ═══════════════════════════════════════════════════════════
   SUMMARY
═══════════════════════════════════════════════════════════ */
async function loadSummary() {
  const d = await api('/api/summary');
  $('s-matches').textContent    = (d.total_matches    || 0).toLocaleString();
  $('s-deliveries').textContent = (d.total_deliveries || 0).toLocaleString();
  $('s-batsmen').textContent    = (d.total_batsmen    || 0).toLocaleString();
  $('s-bowlers').textContent    = (d.total_bowlers    || 0).toLocaleString();
  $('s-teams').textContent      = (d.total_teams      || 0).toLocaleString();
}

/* ═══════════════════════════════════════════════════════════
   DASHBOARD INNER TABS
═══════════════════════════════════════════════════════════ */
const dashLoaded = {};

function setupDashTabs() {
  document.querySelectorAll('#pane-dashboard .itab').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.it;
      document.querySelectorAll('#pane-dashboard .itab').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('#pane-dashboard .ipane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      $('it-' + tab).classList.add('active');
      if (!dashLoaded[tab]) { dashLoaded[tab] = true; dashLoaders[tab](); }
    });
  });
}

const dashLoaders = {
  batsmen: loadBatsmen, bowlers: loadBowlers, teams: loadTeamStats,
  phases: loadPhases, dismissals: loadDismissals, fielders: loadFielders
};

async function loadBatsmen() {
  const data = await api('/api/top-batsmen');
  if (!data.length) return;
  Plotly.newPlot('ch-batsmen', [{
    type: 'bar', x: data.map(b => b.batsman), y: data.map(b => b.total_runs),
    text: data.map(b => `SR ${b.strike_rate}`),
    hovertemplate: '<b>%{x}</b><br>Runs: %{y}<br>%{text}<extra></extra>',
    marker: { color: C.gold }
  }], layout('Top 20 Batsmen — Total Runs'), { responsive: true });
  $('tb-batsmen').innerHTML = tbl(
    ['#', 'Batsman', 'Runs', 'Balls', 'SR'],
    data.map((b, i) => [i+1, `<span class="player-name">${b.batsman}</span>`, b.total_runs, b.balls_faced, b.strike_rate]),
    ['rank-num', 'player-name']
  );
}

async function loadBowlers() {
  const data = await api('/api/top-bowlers');
  if (!data.length) return;
  Plotly.newPlot('ch-bowlers', [{
    type: 'bar', x: data.map(b => b.bowler), y: data.map(b => b.wickets),
    hovertemplate: '<b>%{x}</b><br>Wickets: %{y}<extra></extra>',
    marker: { color: C.orange }
  }], layout('Top 20 Bowlers — Wickets'), { responsive: true });
  $('tb-bowlers').innerHTML = tbl(
    ['#', 'Bowler', 'Wickets'],
    data.map((b, i) => [i+1, `<span class="player-name">${b.bowler}</span>`, b.wickets])
  );
}

async function loadTeamStats() {
  const data = await api('/api/team-stats');
  if (!data.length) return;
  Plotly.newPlot('ch-teams', [{
    type: 'bar', x: data.map(t => t.batting_team), y: data.map(t => t.run_rate),
    marker: { color: C.lblue },
    hovertemplate: '<b>%{x}</b><br>Run Rate: %{y}<extra></extra>'
  }], layout('Team Run Rate (all seasons)'), { responsive: true });
  $('tb-teams').innerHTML = tbl(
    ['Team', 'Total Runs', 'Bat Runs', 'Extras', 'Run Rate'],
    data.map(t => [`<span class="player-name">${t.batting_team}</span>`, t.total_runs, t.bat_runs, t.extras, `<strong>${t.run_rate}</strong>`])
  );
}

async function loadPhases() {
  const data = await api('/api/phase-analysis');
  if (!data.length) return;
  const phases = ['Powerplay', 'Middle', 'Death'];
  const phColors = [C.green, C.gold, C.red];
  const teams = [...new Set(data.map(p => p.batting_team))].sort();
  Plotly.newPlot('ch-phases',
    phases.map((ph, i) => ({
      type: 'bar', name: ph, x: teams,
      y: teams.map(t => { const it = data.find(d => d.batting_team === t && d.phase === ph); return it ? it.run_rate : 0; }),
      marker: { color: phColors[i] }
    })),
    layout('Run Rate by Phase per Team', { barmode: 'group' }), { responsive: true }
  );
  $('tb-phases').innerHTML = tbl(
    ['Team', 'Phase', 'Runs', 'Balls', 'Wkts Lost', 'RR'],
    data.map(p => [`<span class="player-name">${p.batting_team}</span>`, p.phase, p.runs_scored, p.balls_bowled, p.wickets_lost, p.run_rate])
  );
}

async function loadDismissals() {
  const data = await api('/api/dismissals');
  if (!data.length) return;
  Plotly.newPlot('ch-dismissals', [{
    type: 'pie', labels: data.map(d => d.dismissal_kind), values: data.map(d => d.total_dismissals),
    textinfo: 'label+percent', hole: 0.38,
    marker: { colors: PALETTE },
    hovertemplate: '<b>%{label}</b><br>%{value} (%{percent})<extra></extra>'
  }], Object.assign(layout('Dismissal Types'), { margin: { t: 50, b: 20, l: 20, r: 20 }, height: 420 }), { responsive: true });
  $('tb-dismissals').innerHTML = tbl(
    ['Type', 'Count', '%'],
    data.map(d => [`<span class="player-name">${d.dismissal_kind}</span>`, d.total_dismissals, d.percentage + '%'])
  );
}

async function loadFielders() {
  const data = await api('/api/top-fielders');
  if (!data.length) return;
  Plotly.newPlot('ch-fielders', [{
    type: 'bar', x: data.map(f => f.fielder), y: data.map(f => f.catches_taken),
    marker: { color: C.teal },
    hovertemplate: '<b>%{x}</b><br>Catches: %{y}<extra></extra>'
  }], layout('Top Fielders — Catches'), { responsive: true });
  $('tb-fielders').innerHTML = tbl(
    ['#', 'Fielder', 'Catches'],
    data.map((f, i) => [i+1, `<span class="player-name">${f.fielder}</span>`, f.catches_taken])
  );
}

/* ═══════════════════════════════════════════════════════════
   ADVANCED ANALYTICS
═══════════════════════════════════════════════════════════ */
const advLoaded = {};

function setupAdvTabs() {
  document.querySelectorAll('#pane-advanced .itab').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.it;
      document.querySelectorAll('#pane-advanced > .itabs .itab').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('#pane-advanced > .ipane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      $('it-' + tab).classList.add('active');
      if (!advLoaded[tab]) { advLoaded[tab] = true; advLoaders[tab](); }
    });
  });
  // Phase sub-tabs
  document.querySelectorAll('#it-adv-phase .itabs .itab').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.it;
      document.querySelectorAll('#it-adv-phase .itabs .itab').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('#it-adv-phase .ipane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      $('it-' + tab).classList.add('active');
      if (!advLoaded[tab]) { advLoaded[tab] = true; phaseLoaders[tab](); }
    });
  });
}

function loadAdvancedDefault() {
  if (!advLoaded['adv-playoff']) { advLoaded['adv-playoff'] = true; loadPlayoff(); }
}

const advLoaders = {
  'adv-playoff': loadPlayoff,
  'adv-consistency': loadBatConsistency,
  'adv-bconsistency': loadBowlConsistency,
  'adv-partnership': loadPartnership,
  'adv-phase': loadPhaseDefault,
  'adv-spinfast': loadSpinFast,
  'adv-age': loadAgeCurves,
  'adv-mvp': loadMVP,
  'adv-par': loadParScore,
  'adv-venue': loadVenueDominance,
  'adv-toss': loadTossImpact,
  'adv-chase': loadChaseDefend
};

const phaseLoaders = {
  'ph-pp-bat': () => loadPhaseBat('powerplay-batsmen', 'ch-pp-bat', 'tb-pp-bat', 'Powerplay Batsmen'),
  'ph-pp-bowl': () => loadPhaseBowl('powerplay-bowlers', 'ch-pp-bowl', 'tb-pp-bowl', 'Powerplay Bowlers'),
  'ph-mid-bat': () => loadPhaseBat('middle-batsmen', 'ch-mid-bat', 'tb-mid-bat', 'Middle Overs Batsmen'),
  'ph-mid-bowl': () => loadPhaseBowl('middle-bowlers', 'ch-mid-bowl', 'tb-mid-bowl', 'Middle Overs Bowlers'),
  'ph-death-bat': () => loadPhaseBat('death-batsmen', 'ch-death-bat', 'tb-death-bat', 'Death Overs Batsmen'),
  'ph-death-bowl': () => loadPhaseBowl('death-bowlers', 'ch-death-bowl', 'tb-death-bowl', 'Death Overs Bowlers')
};

function loadPhaseDefault() {
  if (!advLoaded['ph-pp-bat']) { advLoaded['ph-pp-bat'] = true; phaseLoaders['ph-pp-bat'](); }
}

/* Playoff */
async function loadPlayoff() {
  const data = await api('/api/playoff-scorers');
  if (!data.length) return;
  Plotly.newPlot('ch-playoff', [{
    type: 'bar', x: data.map(d => d.batsman), y: data.map(d => d.runs),
    text: data.map(d => `SR ${d.strike_rate}`),
    hovertemplate: '<b>%{x}</b><br>Runs: %{y}<br>%{text}<extra></extra>',
    marker: { color: C.gold }
  }], layout('Playoff Run Scorers (Top 20)'), { responsive: true });
  $('tb-playoff').innerHTML = tbl(
    ['#', 'Batsman', 'Runs', 'Balls', 'Matches', 'SR'],
    data.map((d, i) => [i+1, `<span class="player-name">${d.batsman}</span>`, d.runs, d.balls, d.matches, d.strike_rate])
  );
}

/* Batsman Consistency */
async function loadBatConsistency() {
  const data = await api('/api/batsman-consistency');
  if (!data.length) return;
  Plotly.newPlot('ch-bat-cons', [{
    type: 'scatter', mode: 'markers',
    x: data.map(d => d.std_dev), y: data.map(d => d.consistency_score),
    text: data.map(d => d.batsman),
    hovertemplate: '<b>%{text}</b><br>Consistency: %{y}<br>Std Dev: %{x}<extra></extra>',
    marker: { color: data.map(d => d.consistency_score), colorscale: 'Viridis', size: 10, showscale: true }
  }], layout('Consistency Score vs Std Deviation', { xaxis: { title: 'Std Deviation (runs)', tickangle: 0 }, yaxis: { title: 'Consistency Score' } }), { responsive: true });
  $('tb-bat-cons').innerHTML = tbl(
    ['#', 'Batsman', 'Innings', 'Avg', 'Std Dev', '30+ %', '50+ %', 'Score'],
    data.map((d, i) => [i+1, `<span class="player-name">${d.batsman}</span>`, d.innings, d.avg, d.std_dev, d.freq_30_plus + '%', d.freq_50_plus + '%', `<span class="badge badge-gold">${d.consistency_score}</span>`])
  );
}

/* Bowler Consistency */
async function loadBowlConsistency() {
  const data = await api('/api/bowler-consistency');
  if (!data.length) return;
  Plotly.newPlot('ch-bowl-cons', [{
    type: 'scatter', mode: 'markers',
    x: data.map(d => d.economy_std), y: data.map(d => d.consistency_score),
    text: data.map(d => d.bowler),
    hovertemplate: '<b>%{text}</b><br>Consistency: %{y}<br>Econ Std: %{x}<extra></extra>',
    marker: { color: data.map(d => d.consistency_score), colorscale: 'RdYlGn', size: 10, showscale: true }
  }], layout('Bowler Consistency vs Economy Variance', { xaxis: { title: 'Economy Std Dev', tickangle: 0 }, yaxis: { title: 'Consistency Score' } }), { responsive: true });
  $('tb-bowl-cons').innerHTML = tbl(
    ['#', 'Bowler', 'Matches', 'Avg Econ', 'Econ Std', 'Wkts/Game', 'Score'],
    data.map((d, i) => [i+1, `<span class="player-name">${d.bowler}</span>`, d.matches, d.avg_economy, d.economy_std, d.wickets_per_game, `<span class="badge badge-gold">${d.consistency_score}</span>`])
  );
}

/* Partnership */
async function loadPartnership() {
  const data = await api('/api/partnership-analysis');
  if (!data.length) return;
  const labels = data.map(d => `${d.player1} & ${d.player2}`);
  Plotly.newPlot('ch-partner', [{
    type: 'bar', x: labels, y: data.map(d => d.total_runs),
    text: data.map(d => `Avg ${d.avg_partnership}`),
    hovertemplate: '<b>%{x}</b><br>Total: %{y}<br>%{text}<extra></extra>',
    marker: { color: C.teal }
  }], layout('Best Batting Partnerships — Total Runs'), { responsive: true });
  $('tb-partner').innerHTML = tbl(
    ['Player 1', 'Player 2', 'Total Runs', 'Partnerships', 'Avg'],
    data.map(d => [`<span class="player-name">${d.player1}</span>`, `<span class="player-name">${d.player2}</span>`, d.total_runs, d.partnerships, d.avg_partnership])
  );
}

/* Phase helpers */
async function loadPhaseBat(endpoint, chartId, tableId, title) {
  const data = await api('/api/' + endpoint);
  if (!data.length) return;
  Plotly.newPlot(chartId, [{
    type: 'bar', x: data.map(d => d.batsman), y: data.map(d => d.runs),
    text: data.map(d => `SR ${d.strike_rate}`),
    hovertemplate: '<b>%{x}</b><br>Runs: %{y}<br>%{text}<extra></extra>',
    marker: { color: C.gold }
  }], layout(title), { responsive: true });
  $(tableId).innerHTML = tbl(
    ['#', 'Batsman', 'Runs', 'Balls', 'SR'],
    data.map((d, i) => [i+1, `<span class="player-name">${d.batsman}</span>`, d.runs, d.balls, d.strike_rate])
  );
}

async function loadPhaseBowl(endpoint, chartId, tableId, title) {
  const data = await api('/api/' + endpoint);
  if (!data.length) return;
  Plotly.newPlot(chartId, [{
    type: 'bar', x: data.map(d => d.bowler), y: data.map(d => d.wickets),
    text: data.map(d => `Econ ${d.economy}`),
    hovertemplate: '<b>%{x}</b><br>Wickets: %{y}<br>%{text}<extra></extra>',
    marker: { color: C.orange }
  }], layout(title), { responsive: true });
  $(tableId).innerHTML = tbl(
    ['#', 'Bowler', 'Wickets', 'Economy', 'Balls'],
    data.map((d, i) => [i+1, `<span class="player-name">${d.bowler}</span>`, d.wickets, d.economy, d.balls])
  );
}

/* Spin vs Fast */
async function loadSpinFast() {
  const data = await api('/api/spinner-vs-fast');
  const spinners = data.spinners || [];
  const fast = data.fast || [];
  if (spinners.length) {
    Plotly.newPlot('ch-spinners', [{
      type: 'bar', x: spinners.map(d => d.bowler), y: spinners.map(d => d.wickets),
      marker: { color: C.lblue },
      hovertemplate: '<b>%{x}</b><br>Wickets: %{y}<extra></extra>'
    }], layout('Spinners — Wickets', { margin: { t: 40, b: 110, l: 45, r: 10 } }), { responsive: true });
    $('tb-spinners').innerHTML = tbl(
      ['#', 'Bowler', 'Wickets', 'Economy'],
      spinners.map((d, i) => [i+1, `<span class="player-name">${d.bowler}</span>`, d.wickets, d.economy])
    );
  }
  if (fast.length) {
    Plotly.newPlot('ch-fast', [{
      type: 'bar', x: fast.map(d => d.bowler), y: fast.map(d => d.wickets),
      marker: { color: C.orange },
      hovertemplate: '<b>%{x}</b><br>Wickets: %{y}<extra></extra>'
    }], layout('Fast Bowlers — Wickets', { margin: { t: 40, b: 110, l: 45, r: 10 } }), { responsive: true });
    $('tb-fast').innerHTML = tbl(
      ['#', 'Bowler', 'Wickets', 'Economy'],
      fast.map((d, i) => [i+1, `<span class="player-name">${d.bowler}</span>`, d.wickets, d.economy])
    );
  }
}

/* Age Curves */
async function loadAgeCurves() {
  const [srData, ecoData] = await Promise.all([api('/api/age-vs-sr'), api('/api/age-vs-economy')]);
  if (srData.length) {
    Plotly.newPlot('ch-age-sr', [{
      type: 'scatter', mode: 'lines+markers',
      x: srData.map(d => d.age), y: srData.map(d => d.avg_sr),
      line: { color: C.gold, width: 2.5 }, marker: { color: C.gold, size: 7 },
      hovertemplate: 'Age %{x}<br>Avg SR: %{y}<extra></extra>'
    }], layout('Age vs Strike Rate', { xaxis: { title: 'Age', tickangle: 0 }, yaxis: { title: 'Avg Strike Rate' }, margin: { t: 40, b: 60, l: 55, r: 20 } }), { responsive: true });
  }
  if (ecoData.length) {
    Plotly.newPlot('ch-age-eco', [{
      type: 'scatter', mode: 'lines+markers',
      x: ecoData.map(d => d.age), y: ecoData.map(d => d.avg_economy),
      line: { color: C.orange, width: 2.5 }, marker: { color: C.orange, size: 7 },
      hovertemplate: 'Age %{x}<br>Avg Economy: %{y}<extra></extra>'
    }], layout('Age vs Economy Rate', { xaxis: { title: 'Age', tickangle: 0 }, yaxis: { title: 'Avg Economy' }, margin: { t: 40, b: 60, l: 55, r: 20 } }), { responsive: true });
  }
}

/* MVP */
async function loadMVP() {
  const data = await api('/api/mvp-per-season');
  if (!data.length) return;
  Plotly.newPlot('ch-mvp', [{
    type: 'bar', x: data.map(d => d.season), y: data.map(d => d.points),
    text: data.map(d => d.mvp),
    textposition: 'outside',
    hovertemplate: '<b>%{text}</b><br>Season: %{x}<br>Points: %{y}<extra></extra>',
    marker: { color: PALETTE }
  }], layout('MVP Per Season — Weighted Points', { xaxis: { tickangle: 0, type: 'category' }, margin: { t: 60, b: 60, l: 55, r: 20 } }), { responsive: true });
  $('tb-mvp').innerHTML = tbl(
    ['Season', 'MVP', 'Points'],
    data.map(d => [d.season, `<span class="player-name">${d.mvp}</span>`, `<span class="badge badge-gold">${d.points}</span>`])
  );
}

/* Par Score */
async function loadParScore() {
  const data = await api('/api/par-score-evolution');
  if (!data.length) return;
  Plotly.newPlot('ch-par', [
    { type: 'scatter', mode: 'lines+markers', name: 'Avg 1st Innings', x: data.map(d => d.season), y: data.map(d => d.avg_first_innings), line: { color: C.lblue, width: 2.5 }, marker: { size: 7 } },
    { type: 'scatter', mode: 'lines+markers', name: 'Winning Avg', x: data.map(d => d.season), y: data.map(d => d.winning_avg), line: { color: C.gold, width: 2.5, dash: 'dot' }, marker: { size: 7 } }
  ], layout('Par Score Evolution 2008–2017', { xaxis: { tickangle: 0, type: 'category' }, yaxis: { title: 'Runs' }, margin: { t: 50, b: 60, l: 55, r: 20 }, legend: { x: 0.02, y: 0.98 } }), { responsive: true });
  $('tb-par').innerHTML = tbl(
    ['Season', 'Avg 1st Innings', 'Winning Avg', 'Matches'],
    data.map(d => [d.season, d.avg_first_innings, d.winning_avg, d.matches])
  );
}

/* Venue Dominance */
async function loadVenueDominance() {
  const data = await api('/api/venue-dominance');
  if (!data.length) return;
  const colors = data.map(d => d.dominance === 'Batting' ? C.gold : d.dominance === 'Bowling' ? C.lblue : C.green);
  Plotly.newPlot('ch-venue-dom', [{
    type: 'bar', x: data.map(d => d.venue), y: data.map(d => d.avg_score),
    marker: { color: colors },
    hovertemplate: '<b>%{x}</b><br>Avg Score: %{y}<br>Dominance: ' + data.map(d => d.dominance).join('<extra></extra>') + '<extra></extra>'
  }], layout('Venue Avg Score — Batting vs Bowling Dominance'), { responsive: true });
  $('tb-venue-dom').innerHTML = tbl(
    ['Venue', 'Avg Score', 'Matches', 'Dominance'],
    data.map(d => [d.venue, d.avg_score, d.matches, `<span class="badge ${d.dominance === 'Batting' ? 'badge-gold' : d.dominance === 'Bowling' ? 'badge-blue' : 'badge-green'}">${d.dominance}</span>`])
  );
}

/* Toss Impact */
async function loadTossImpact() {
  const data = await api('/api/toss-impact');
  if (!data || !data.by_decision) return;
  renderTossContent('toss-content', data);
}

function renderTossContent(containerId, data) {
  const byDec = data.by_decision || [];
  const byVenue = data.by_venue || [];
  const html = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem">
      <div class="card" style="text-align:center">
        <div style="font-size:.75rem;color:var(--text3);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.3rem">Overall Toss Win → Match Win %</div>
        <div style="font-size:2.5rem;font-weight:800;color:var(--gold)">${data.overall_toss_win_pct}%</div>
      </div>
      <div class="card">
        <div style="font-size:.8rem;font-weight:600;color:var(--text2);margin-bottom:.6rem">By Decision</div>
        ${byDec.map(d => `<div style="display:flex;justify-content:space-between;padding:.3rem 0;border-bottom:1px solid var(--border);font-size:.85rem"><span style="text-transform:capitalize">${d.toss_decision}</span><span style="color:var(--gold);font-weight:700">${d.win_pct}%</span><span style="color:var(--text3)">${d.count} matches</span></div>`).join('')}
      </div>
    </div>
    <div class="card">
      <div style="font-size:.85rem;font-weight:600;color:var(--text2);margin-bottom:.8rem">Toss Win → Match Win % by Venue (top 15)</div>
      <div class="tbl-wrap">${tbl(['Venue', 'Toss Win %', 'Matches'], byVenue.map(v => [v.venue, `<span class="badge badge-gold">${v.toss_win_pct}%</span>`, v.matches]))}</div>
    </div>`;
  $(containerId).innerHTML = html;
}

/* Chase vs Defend */
async function loadChaseDefend() {
  const data = await api('/api/chasing-defending');
  if (!data.length) return;
  Plotly.newPlot('ch-chase', [
    { type: 'bar', name: 'Defending Win %', x: data.map(d => d.team), y: data.map(d => d.defending_win_pct), marker: { color: C.lblue } },
    { type: 'bar', name: 'Chasing Win %', x: data.map(d => d.team), y: data.map(d => d.chasing_win_pct), marker: { color: C.gold } }
  ], layout('Chasing vs Defending Win % per Team', { barmode: 'group' }), { responsive: true });
  $('tb-chase').innerHTML = tbl(
    ['Team', 'Def Matches', 'Def Wins', 'Def Win%', 'Chase Matches', 'Chase Wins', 'Chase Win%'],
    data.map(d => [
      `<span class="player-name">${d.team}</span>`,
      d.defending_matches, d.defending_wins,
      `<span class="badge badge-blue">${d.defending_win_pct}%</span>`,
      d.chasing_matches, d.chasing_wins,
      `<span class="badge badge-gold">${d.chasing_win_pct}%</span>`
    ])
  );
}

/* ═══════════════════════════════════════════════════════════
   COMPARE PLAYERS
═══════════════════════════════════════════════════════════ */
let allPlayers = [];

async function initCompare() {
  if (allPlayers.length) return;
  const d = await api('/api/player-search?q=');
  allPlayers = d.map(p => p.name);
}

function onSearch(input, listId, hiddenId) {
  const q = input.value.trim().toLowerCase();
  const list = $(listId);
  $(hiddenId).value = '';
  if (q.length < 2) { list.classList.remove('open'); return; }
  const matches = allPlayers.filter(n => n.toLowerCase().includes(q)).slice(0, 12);
  if (!matches.length) { list.classList.remove('open'); return; }
  list.innerHTML = matches.map(n =>
    `<div class="ac-item" onclick="selectPlayer('${n.replace(/'/g, "\\'")}','${listId}','${hiddenId}','${input.id}')">${n}</div>`
  ).join('');
  list.classList.add('open');
}

function selectPlayer(name, listId, hiddenId, inputId) {
  $(inputId).value = name;
  $(hiddenId).value = name;
  $(listId).classList.remove('open');
}

document.addEventListener('click', e => {
  if (!e.target.closest('.search-wrap'))
    document.querySelectorAll('.ac-list').forEach(l => l.classList.remove('open'));
});

async function doCompare() {
  const p1 = $('p1-val').value || $('p1-input').value;
  const p2 = $('p2-val').value || $('p2-input').value;
  const err = $('cmp-error');
  err.style.display = 'none';
  if (!p1 || !p2) { err.textContent = 'Please enter both player names.'; err.style.display = 'block'; return; }
  if (p1 === p2) { err.textContent = 'Please select two different players.'; err.style.display = 'block'; return; }

  const [d1, d2] = await Promise.all([
    fetch(`/api/player/${encodeURIComponent(p1)}`).then(r => r.ok ? r.json() : null),
    fetch(`/api/player/${encodeURIComponent(p2)}`).then(r => r.ok ? r.json() : null)
  ]);
  if (!d1) { err.textContent = `"${p1}" not found.`; err.style.display = 'block'; return; }
  if (!d2) { err.textContent = `"${p2}" not found.`; err.style.display = 'block'; return; }

  renderCompareCards(p1, d1, p2, d2);
  renderCompareChart(p1, d1, p2, d2);
  $('cmp-result').style.display = 'block';
}

function resetCompare() {
  ['p1-input','p2-input'].forEach(id => $(id).value = '');
  ['p1-val','p2-val'].forEach(id => $(id).value = '');
  $('cmp-result').style.display = 'none';
  $('cmp-error').style.display = 'none';
}

function renderCompareCards(n1, d1, n2, d2) {
  const b1 = d1.career_stats?.batting || {}, bw1 = d1.career_stats?.bowling || {};
  const b2 = d2.career_stats?.batting || {}, bw2 = d2.career_stats?.bowling || {};
  function better(v1, v2, hi = true) { return hi ? (v1 > v2 ? 'better' : '') : (v1 < v2 && v1 > 0 ? 'better' : ''); }
  function card(name, d, bat, bowl, bat2, bowl2) {
    const tags = [d.nationality, d.role, d.current_team].filter(Boolean).map(t => `<span class="badge badge-blue" style="margin:.1rem">${t}</span>`).join('');
    return `<div class="player-compare-card">
      <div class="pcc-header">${avatar(name, 52)}<div><div class="pcc-name">${name}</div><div class="pcc-meta">${tags}</div></div></div>
      <div style="font-size:.72rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.5px;margin:.6rem 0 .3rem">Batting</div>
      ${[['Runs', bat.total_runs, bat2.total_runs, true],['Matches', bat.matches, bat2.matches, false],['Average', bat.batting_avg, bat2.batting_avg, true],['Strike Rate', bat.strike_rate, bat2.strike_rate, true],['100s / 50s', `${bat.centuries||0}/${bat.fifties||0}`, null, false]].map(([l,v,v2,hi]) =>
        `<div class="stat-compare-row"><span class="scr-label">${l}</span><span class="scr-val ${v2 !== null ? better(v,v2,hi) : ''}">${v||0}</span></div>`).join('')}
      <div style="font-size:.72rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.5px;margin:.6rem 0 .3rem">Bowling</div>
      ${[['Wickets', bowl.total_wickets, bowl2.total_wickets, true],['Economy', bowl.economy, bowl2.economy, false],['Average', bowl.bowling_avg, bowl2.bowling_avg, false]].map(([l,v,v2,hi]) =>
        `<div class="stat-compare-row"><span class="scr-label">${l}</span><span class="scr-val ${better(v,v2,hi)}">${v||0}</span></div>`).join('')}
    </div>`;
  }
  $('cmp-cards').innerHTML = card(n1, d1, b1, bw1, b2, bw2) + card(n2, d2, b2, bw2, b1, bw1);
}

function renderCompareChart(n1, d1, n2, d2) {
  const b1 = d1.career_stats?.batting || {}, b2 = d2.career_stats?.batting || {};
  const cats = ['Runs', 'Avg', 'SR', '100s', '50s'];
  const v1 = [b1.total_runs||0, b1.batting_avg||0, b1.strike_rate||0, b1.centuries||0, b1.fifties||0];
  const v2 = [b2.total_runs||0, b2.batting_avg||0, b2.strike_rate||0, b2.centuries||0, b2.fifties||0];
  Plotly.newPlot('ch-compare', [
    { type: 'bar', name: n1, x: cats, y: v1, marker: { color: C.gold } },
    { type: 'bar', name: n2, x: cats, y: v2, marker: { color: C.lblue } }
  ], layout('Batting Stats Comparison', { barmode: 'group', xaxis: { tickangle: 0 }, margin: { t: 50, b: 60, l: 55, r: 20 } }), { responsive: true });
}

/* ═══════════════════════════════════════════════════════════
   RANKINGS
═══════════════════════════════════════════════════════════ */
async function loadRankings() {
  const season = $('season-sel').value;
  const data = await api(`/api/seasonal-rankings?season=${season}`);
  const bat = data.top_batsmen || [];
  const bowl = data.top_bowlers || [];
  $('rank-bat').innerHTML = bat.map(p =>
    `<tr><td class="rank-num">${p.rank}</td><td class="player-name">${p.name}</td><td>${p.runs}</td><td>${p.strike_rate}</td></tr>`
  ).join('');
  $('rank-bowl').innerHTML = bowl.map(p =>
    `<tr><td class="rank-num">${p.rank}</td><td class="player-name">${p.name}</td><td>${p.wickets}</td></tr>`
  ).join('');
}

/* ═══════════════════════════════════════════════════════════
   RECORDS
═══════════════════════════════════════════════════════════ */
async function loadRecords() {
  const data = await api('/api/player-records');
  const hi = data.highest_individual_score || {};
  const mc = (data.most_centuries || [])[0] || {};
  const mw = (data.most_wickets || [])[0] || {};
  $('r-hi').textContent = hi.score || '—';   $('r-hi-p').textContent = hi.player || '—';
  $('r-100').textContent = mc.centuries || '—'; $('r-100-p').textContent = mc.player || '—';
  $('r-wkt').textContent = mw.wickets || '—';  $('r-wkt-p').textContent = mw.player || '—';
  function rows(arr, key) {
    return arr.map(r => `<tr><td class="player-name">${r.player}</td><td><strong>${r[key]}</strong></td></tr>`).join('');
  }
  $('r-centuries').innerHTML = rows(data.most_centuries || [], 'centuries');
  $('r-wickets').innerHTML   = rows(data.most_wickets   || [], 'wickets');
  $('r-sixes').innerHTML     = rows(data.most_sixes     || [], 'sixes');
  $('r-catches').innerHTML   = rows(data.most_catches   || [], 'catches');
  $('r-fifties').innerHTML   = rows(data.most_fifties   || [], 'fifties');
  $('r-fours').innerHTML     = rows(data.most_fours     || [], 'fours');
}

/* ═══════════════════════════════════════════════════════════
   CHAMPIONS
═══════════════════════════════════════════════════════════ */
async function loadChampions() {
  const data = await api('/api/ipl-champions');
  if (!data.length) return;
  const latest = data[data.length - 1];
  $('ch-latest-txt').textContent = `${latest.champion} won in ${latest.season}`;
  const titleCount = {}, finalsCount = {};
  data.forEach(d => {
    titleCount[d.champion] = (titleCount[d.champion] || 0) + 1;
    finalsCount[d.champion] = (finalsCount[d.champion] || 0) + 1;
    finalsCount[d.runner_up] = (finalsCount[d.runner_up] || 0) + 1;
  });
  const mostTitle = Object.entries(titleCount).sort((a, b) => b[1] - a[1])[0];
  const mostFinals = Object.entries(finalsCount).sort((a, b) => b[1] - a[1])[0];
  $('cs-seasons').textContent = data.length;
  $('cs-titles').textContent = mostTitle[1]; $('cs-titles-team').textContent = mostTitle[0];
  $('cs-teams').textContent = Object.keys(titleCount).length;
  $('cs-finals').textContent = mostFinals[1]; $('cs-finals-team').textContent = mostFinals[0];
  $('champ-tbody').innerHTML = [...data].reverse().map(d =>
    `<tr><td><strong>${d.season}</strong></td>
     <td><span class="badge badge-green">${d.champion}</span></td>
     <td><span class="badge badge-blue">${d.runner_up}</span></td>
     <td>${d.finals_mvp || '—'}</td></tr>`
  ).join('');
}

/* ═══════════════════════════════════════════════════════════
   BEST XI
═══════════════════════════════════════════════════════════ */
async function loadBestXI() {
  const data = await api('/api/best-xi');
  if (!data.length) { $('xi-container').innerHTML = '<p style="color:var(--text3)">Loading…</p>'; return; }
  const posOrder = ['Batsman', 'Wicketkeeper', 'All-rounder', 'Bowler'];
  const sorted = [...data].sort((a, b) => posOrder.indexOf(a.position) - posOrder.indexOf(b.position));
  $('xi-container').innerHTML = sorted.map(p => {
    const badgeClass = p.position === 'Bowler' ? 'badge-orange' : p.position === 'All-rounder' ? 'badge-green' : p.position === 'Wicketkeeper' ? 'badge-blue' : 'badge-gold';
    return `<div class="xi-card">
      <div class="xi-avatar">${initials(p.player)}</div>
      <div class="xi-name">${p.player}</div>
      <div class="xi-role"><span class="badge ${badgeClass}">${p.position}</span></div>
      <div class="xi-score">Score: ${p.total_score}</div>
      <div style="font-size:.72rem;color:var(--text3);margin-top:.2rem">${p.current_team}</div>
    </div>`;
  }).join('');
}

/* ═══════════════════════════════════════════════════════════
   TEAMS PANE
═══════════════════════════════════════════════════════════ */
const teamsLoaded = {};

function setupTeamsTabs() {
  document.querySelectorAll('#pane-teams .itab').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.it;
      document.querySelectorAll('#pane-teams .itab').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('#pane-teams .ipane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      $('it-' + tab).classList.add('active');
      if (!teamsLoaded[tab]) { teamsLoaded[tab] = true; teamLoaders[tab](); }
    });
  });
}

const teamLoaders = {
  'tm-chase': loadTeamChase,
  'tm-toss': loadTeamToss,
  'tm-venue': loadTeamVenue
};

function loadTeamsDefault() {
  if (!teamsLoaded['tm-chase']) { teamsLoaded['tm-chase'] = true; loadTeamChase(); }
}

async function loadTeamChase() {
  const data = await api('/api/chasing-defending');
  if (!data.length) return;
  Plotly.newPlot('ch-tm-chase', [
    { type: 'bar', name: 'Defending Win %', x: data.map(d => d.team), y: data.map(d => d.defending_win_pct), marker: { color: C.lblue } },
    { type: 'bar', name: 'Chasing Win %', x: data.map(d => d.team), y: data.map(d => d.chasing_win_pct), marker: { color: C.gold } }
  ], layout('Chasing vs Defending Win % per Team', { barmode: 'group' }), { responsive: true });
  $('tb-tm-chase').innerHTML = tbl(
    ['Team', 'Def Win%', 'Chase Win%'],
    data.map(d => [`<span class="player-name">${d.team}</span>`, `<span class="badge badge-blue">${d.defending_win_pct}%</span>`, `<span class="badge badge-gold">${d.chasing_win_pct}%</span>`])
  );
}

async function loadTeamToss() {
  const data = await api('/api/toss-impact');
  if (!data || !data.by_decision) return;
  renderTossContent('toss-content2', data);
}

async function loadTeamVenue() {
  const data = await api('/api/venue-dominance');
  if (!data.length) return;
  const colors = data.map(d => d.dominance === 'Batting' ? C.gold : d.dominance === 'Bowling' ? C.lblue : C.green);
  Plotly.newPlot('ch-tm-venue', [{
    type: 'bar', x: data.map(d => d.venue), y: data.map(d => d.avg_score),
    marker: { color: colors },
    hovertemplate: '<b>%{x}</b><br>Avg Score: %{y}<extra></extra>'
  }], layout('Venue Avg Score'), { responsive: true });
  $('tb-tm-venue').innerHTML = tbl(
    ['Venue', 'Avg Score', 'Matches', 'Dominance'],
    data.map(d => [d.venue, d.avg_score, d.matches, `<span class="badge ${d.dominance === 'Batting' ? 'badge-gold' : d.dominance === 'Bowling' ? 'badge-blue' : 'badge-green'}">${d.dominance}</span>`])
  );
}

/* ═══════════════════════════════════════════════════════════
   INIT
═══════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', async () => {
  loadSummary();
  setupDashTabs();
  setupAdvTabs();
  setupTeamsTabs();
  // Load default dashboard tab
  loadBatsmen();
  dashLoaded['batsmen'] = true;
  topLoaded['dashboard'] = true;
  // Pre-fetch player list for compare
  const d = await api('/api/player-search?q=');
  allPlayers = d.map(p => p.name);
});
