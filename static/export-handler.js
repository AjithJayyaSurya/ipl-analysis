/**
 * Export Handler - Handle PDF, CSV, JSON exports
 */

class ExportHandler {
    /**
     * Export player profile as JSON
     */
    static async exportPlayerJSON(playerName) {
        try {
            const response = await fetch(`/export/player/${encodeURIComponent(playerName)}/json`);
            const data = await response.json();
            const json = JSON.stringify(data, null, 2);
            this.downloadFile(json, `${playerName}_profile.json`, 'application/json');
        } catch (err) {
            console.error('Error exporting JSON:', err);
            alert('Failed to export player profile');
        }
    }

    /**
     * Export player profile as CSV
     */
    static async exportPlayerCSV(playerName) {
        try {
            const response = await fetch(`/export/player/${encodeURIComponent(playerName)}/csv`);
            const csv = await response.text();
            this.downloadFile(csv, `${playerName}_profile.csv`, 'text/csv');
        } catch (err) {
            console.error('Error exporting CSV:', err);
            alert('Failed to export player profile');
        }
    }

    /**
     * Export season rankings as JSON
     */
    static async exportRankingsJSON(season) {
        try {
            const response = await fetch(`/export/season-rankings/json`);
            const data = await response.json();
            const filtered = season ? data[season] || {} : data;
            const json = JSON.stringify(filtered, null, 2);
            this.downloadFile(json, `ipl_rankings_${season || 'all'}.json`, 'application/json');
        } catch (err) {
            console.error('Error exporting rankings:', err);
            alert('Failed to export rankings');
        }
    }

    /**
     * Export records as JSON
     */
    static async exportRecordsJSON() {
        try {
            const response = await fetch(`/export/top-records/json`);
            const data = await response.json();
            const json = JSON.stringify(data, null, 2);
            this.downloadFile(json, 'ipl_records.json', 'application/json');
        } catch (err) {
            console.error('Error exporting records:', err);
            alert('Failed to export records');
        }
    }

    /**
     * Helper to download file
     */
    static downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }

    /**
     * Generate CSV from JSON data
     */
    static jsonToCSV(data) {
        if (!Array.isArray(data) || data.length === 0) return '';

        const headers = Object.keys(data[0]);
        const csv = [headers.join(','), ...data.map(row =>
            headers.map(header => `"${row[header] || ''}"`.replace(/"/g, '""')).join(',')
        )].join('\n');

        return csv;
    }

    /**
     * Generate simple PDF (text-based for now)
     */
    static generatePDF(title, content) {
        // For now, return formatted text that can be printed
        const pdf = `
${title}
${'='.repeat(title.length)}

${content}

Generated on: ${new Date().toLocaleString()}
`;
        return pdf;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExportHandler;
}
