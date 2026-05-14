/* IPL Analytics - Dashboard JavaScript (FIXED) */

// Ensure Plotly is available
if (typeof Plotly === 'undefined') {
    console.error('[ERROR] Plotly.js not loaded! Make sure script tag is in dashboard.html');
}

// Load summary statistics
async function loadSummary() {
    try {
        console.log('[INFO] Loading summary...');
        const response = await fetch('/api/summary');

        if (!response.ok) {
            console.error('[ERROR] Summary API error:', response.status, response.statusText);
            document.getElementById('total-matches').textContent = 'Error';
            document.getElementById('total-teams').textContent = 'Error';
            document.getElementById('total-batsmen').textContent = 'Error';
            document.getElementById('total-bowlers').textContent = 'Error';
            return;
        }

        const data = await response.json();
        console.log('[OK] Summary data:', data);

        document.getElementById('total-matches').textContent = data.total_matches || 0;
        document.getElementById('total-teams').textContent = data.total_teams || 0;
        document.getElementById('total-batsmen').textContent = data.total_batsmen || 0;
        document.getElementById('total-bowlers').textContent = data.total_bowlers || 0;
    } catch (e) {
        console.error('[ERROR] Exception loading summary:', e);
        document.getElementById('total-matches').textContent = 'Error';
    }
}

// Load top batsmen data and chart
async function loadBatsmen() {
    try {
        console.log('[INFO] Loading batsmen...');
        const response = await fetch('/api/top-batsmen');

        if (!response.ok) {
            console.error('[ERROR] Batsmen API error:', response.status);
            document.getElementById('batsmen-chart').innerHTML = '<p>Failed to load data (Error ' + response.status + ')</p>';
            return;
        }

        const data = await response.json();
        console.log('[OK] Batsmen data loaded:', data.length, 'records');

        if (!data || data.length === 0) {
            document.getElementById('batsmen-chart').innerHTML = '<p>No data available</p>';
            return;
        }

        // Chart
        const chartData = [{
            type: 'bar',
            x: data.map(b => b.batsman),
            y: data.map(b => parseInt(b.total_runs) || 0),
            name: 'Runs',
            marker: { color: '#ff6b35' }
        }];

        const layout = {
            title: 'Top 20 Batsmen by Runs',
            xaxis: { title: 'Batsman', tickangle: -45 },
            yaxis: { title: 'Runs' },
            margin: { b: 120, l: 60, t: 60, r: 40 },
            autosize: true
        };

        if (typeof Plotly !== 'undefined') {
            Plotly.newPlot('batsmen-chart', chartData, layout, { responsive: true });
        }

        // Table
        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Batsman</th>
                        <th>Total Runs</th>
                        <th>Balls Faced</th>
                        <th>Strike Rate</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map((b, i) => `
                        <tr>
                            <td><strong>${b.batsman || 'N/A'}</strong></td>
                            <td>${b.total_runs || 0}</td>
                            <td>${b.balls_faced || 0}</td>
                            <td>${b.strike_rate || 0}%</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('batsmen-table').innerHTML = tableHTML;
    } catch (e) {
        console.error('[ERROR] Exception loading batsmen:', e);
        document.getElementById('batsmen-chart').innerHTML = '<p>Error: ' + e.message + '</p>';
    }
}

// Load top bowlers data and chart
async function loadBowlers() {
    try {
        console.log('[INFO] Loading bowlers...');
        const response = await fetch('/api/top-bowlers');

        if (!response.ok) {
            console.error('[ERROR] Bowlers API error:', response.status);
            document.getElementById('bowlers-chart').innerHTML = '<p>Failed to load data</p>';
            return;
        }

        const data = await response.json();
        console.log('[OK] Bowlers data loaded:', data.length, 'records');

        if (!data || data.length === 0) {
            document.getElementById('bowlers-chart').innerHTML = '<p>No data available</p>';
            return;
        }

        // Chart
        const chartData = [{
            type: 'bar',
            x: data.map(b => b.bowler),
            y: data.map(b => parseInt(b.wickets) || 0),
            name: 'Wickets',
            marker: { color: '#2a5298' }
        }];

        const layout = {
            title: 'Top 20 Bowlers by Wickets',
            xaxis: { title: 'Bowler', tickangle: -45 },
            yaxis: { title: 'Wickets' },
            margin: { b: 120, l: 60, t: 60, r: 40 },
            autosize: true
        };

        if (typeof Plotly !== 'undefined') {
            Plotly.newPlot('bowlers-chart', chartData, layout, { responsive: true });
        }

        // Table
        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Bowler</th>
                        <th>Wickets</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map((b, i) => `
                        <tr>
                            <td><strong>${b.bowler || 'N/A'}</strong></td>
                            <td>${b.wickets || 0}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('bowlers-table').innerHTML = tableHTML;
    } catch (e) {
        console.error('[ERROR] Exception loading bowlers:', e);
        document.getElementById('bowlers-chart').innerHTML = '<p>Error: ' + e.message + '</p>';
    }
}

// Load team stats data and chart
async function loadTeams() {
    try {
        console.log('[INFO] Loading teams...');
        const response = await fetch('/api/team-stats');

        if (!response.ok) {
            console.error('[ERROR] Teams API error:', response.status);
            return;
        }

        const data = await response.json();
        console.log('[OK] Teams data loaded:', data.length, 'records');

        if (!data || data.length === 0) {
            document.getElementById('teams-chart').innerHTML = '<p>No data available</p>';
            return;
        }

        // Chart
        const chartData = [{
            type: 'bar',
            x: data.map(t => t.batting_team),
            y: data.map(t => parseFloat(t.run_rate) || 0),
            name: 'Run Rate',
            marker: { color: '#1e3c72' }
        }];

        const layout = {
            title: 'Team Run Rate',
            xaxis: { title: 'Team', tickangle: -45 },
            yaxis: { title: 'Run Rate' },
            margin: { b: 120, l: 60, t: 60, r: 40 },
            autosize: true
        };

        if (typeof Plotly !== 'undefined') {
            Plotly.newPlot('teams-chart', chartData, layout, { responsive: true });
        }

        // Table
        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Team</th>
                        <th>Total Runs</th>
                        <th>Bat Runs</th>
                        <th>Extras</th>
                        <th>Run Rate</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map((t, i) => `
                        <tr>
                            <td><strong>${t.batting_team || 'N/A'}</strong></td>
                            <td>${t.total_runs || 0}</td>
                            <td>${t.bat_runs || 0}</td>
                            <td>${t.extras || 0}</td>
                            <td><strong>${t.run_rate || 0}</strong></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('teams-table').innerHTML = tableHTML;
    } catch (e) {
        console.error('[ERROR] Exception loading teams:', e);
    }
}

// Load phase analysis data and chart
async function loadPhases() {
    try {
        console.log('[INFO] Loading phases...');
        const response = await fetch('/api/phase-analysis');

        if (!response.ok) {
            console.error('[ERROR] Phases API error:', response.status);
            return;
        }

        const data = await response.json();
        console.log('[OK] Phases data loaded:', data.length, 'records');

        if (!data || data.length === 0) {
            document.getElementById('phases-chart').innerHTML = '<p>No data available</p>';
            return;
        }

        // Chart
        const phases = ['Powerplay', 'Middle', 'Death'];
        const teams = [...new Set(data.map(p => p.batting_team))];

        const chartData = phases.map(phase => ({
            type: 'bar',
            x: teams,
            y: teams.map(team => {
                const item = data.find(d => d.batting_team === team && d.phase === phase);
                return item ? parseFloat(item.run_rate) || 0 : 0;
            }),
            name: phase
        }));

        const layout = {
            title: 'Run Rate by Phase and Team',
            xaxis: { title: 'Team', tickangle: -45 },
            yaxis: { title: 'Run Rate' },
            barmode: 'group',
            margin: { b: 120, l: 60, t: 60, r: 40 },
            autosize: true
        };

        if (typeof Plotly !== 'undefined') {
            Plotly.newPlot('phases-chart', chartData, layout, { responsive: true });
        }

        // Table
        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Team</th>
                        <th>Phase</th>
                        <th>Runs</th>
                        <th>Balls</th>
                        <th>Wickets Lost</th>
                        <th>Run Rate</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map((p, i) => `
                        <tr>
                            <td><strong>${p.batting_team || 'N/A'}</strong></td>
                            <td>${p.phase || 'N/A'}</td>
                            <td>${p.runs_scored || 0}</td>
                            <td>${p.balls_bowled || 0}</td>
                            <td>${p.wickets_lost || 0}</td>
                            <td>${p.run_rate || 0}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('phases-table').innerHTML = tableHTML;
    } catch (e) {
        console.error('[ERROR] Exception loading phases:', e);
    }
}

// Load dismissals data and chart
async function loadDismissals() {
    try {
        console.log('[INFO] Loading dismissals...');
        const response = await fetch('/api/dismissals');

        if (!response.ok) {
            console.error('[ERROR] Dismissals API error:', response.status);
            return;
        }

        const data = await response.json();
        console.log('[OK] Dismissals data loaded:', data.length, 'records');

        if (!data || data.length === 0) {
            document.getElementById('dismissals-chart').innerHTML = '<p>No data available</p>';
            return;
        }

        // Pie chart
        const chartData = [{
            type: 'pie',
            labels: data.map(d => d.dismissal_kind || 'Unknown'),
            values: data.map(d => parseInt(d.total_dismissals) || 0),
            textposition: 'inside',
            textinfo: 'label+percent'
        }];

        const layout = {
            title: 'Dismissal Types Distribution',
            autosize: true,
            height: 500
        };

        if (typeof Plotly !== 'undefined') {
            Plotly.newPlot('dismissals-chart', chartData, layout, { responsive: true });
        }

        // Table
        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Dismissal Type</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map((d, i) => `
                        <tr>
                            <td><strong>${d.dismissal_kind || 'N/A'}</strong></td>
                            <td>${d.total_dismissals || 0}</td>
                            <td>${d.percentage || 0}%</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('dismissals-table').innerHTML = tableHTML;
    } catch (e) {
        console.error('[ERROR] Exception loading dismissals:', e);
    }
}

// Load fielders data and chart
async function loadFielders() {
    try {
        console.log('[INFO] Loading fielders...');
        const response = await fetch('/api/top-fielders');

        if (!response.ok) {
            console.error('[ERROR] Fielders API error:', response.status);
            return;
        }

        const data = await response.json();
        console.log('[OK] Fielders data loaded:', data.length, 'records');

        if (!data || data.length === 0) {
            document.getElementById('fielders-chart').innerHTML = '<p>No data available</p>';
            return;
        }

        // Chart
        const chartData = [{
            type: 'bar',
            x: data.map(f => f.fielder),
            y: data.map(f => parseInt(f.catches_taken) || 0),
            name: 'Catches',
            marker: { color: '#ff9500' }
        }];

        const layout = {
            title: 'Top Fielders by Catches',
            xaxis: { title: 'Fielder', tickangle: -45 },
            yaxis: { title: 'Catches' },
            margin: { b: 120, l: 60, t: 60, r: 40 },
            autosize: true
        };

        if (typeof Plotly !== 'undefined') {
            Plotly.newPlot('fielders-chart', chartData, layout, { responsive: true });
        }

        // Table
        const tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Fielder</th>
                        <th>Catches</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map((f, i) => `
                        <tr>
                            <td><strong>${f.fielder || 'N/A'}</strong></td>
                            <td>${f.catches_taken || 0}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        document.getElementById('fielders-table').innerHTML = tableHTML;
    } catch (e) {
        console.error('[ERROR] Exception loading fielders:', e);
    }
}

// Tab switching
function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');

    const tabData = {
        'batsmen': loadBatsmen,
        'bowlers': loadBowlers,
        'teams': loadTeams,
        'phases': loadPhases,
        'dismissals': loadDismissals,
        'fielders': loadFielders
    };

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            console.log('[INFO] Switching to tab:', tabName);

            // Update active button
            tabButtons.forEach(b => b.classList.remove('active'));
            button.classList.add('active');

            // Update active pane
            tabPanes.forEach(pane => pane.classList.remove('active'));
            const targetPane = document.getElementById(tabName + '-tab');
            if (targetPane) {
                targetPane.classList.add('active');
            }

            // Load data
            if (tabData[tabName]) {
                tabData[tabName]();
            }
        });
    });
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('[INFO] Initializing dashboard...');
    console.log('[INFO] Plotly available:', typeof Plotly !== 'undefined');

    loadSummary();
    setupTabs();

    // Load first tab by default
    setTimeout(() => {
        console.log('[INFO] Loading default tab...');
        loadBatsmen();
    }, 100);
});
