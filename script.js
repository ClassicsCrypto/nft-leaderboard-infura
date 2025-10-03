document.addEventListener('DOMContentLoaded', () => {
    const leaderboardBody = document.getElementById('leaderboard-body');
    const lastUpdatedEl = document.getElementById('last-updated');

    // This fetch call remains the same, it just loads the local JSON file.
    fetch('leaderboard.json')
        .then(response => response.json())
        .then(data => {
            lastUpdatedEl.textContent = `Last Updated: ${new Date(data.last_updated).toLocaleString()}`;
            leaderboardBody.innerHTML = ''; // Clear previous entries
            
            data.leaderboard.forEach((entry, index) => {
                const row = document.createElement('tr');
                const shortAddress = `${entry.address.substring(0, 6)}...${entry.address.substring(entry.address.length - 4)}`;
                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${shortAddress}</td>
                    <td>${entry.count}</td>
                `;
                leaderboardBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error("Failed to load leaderboard data:", error);
            leaderboardBody.innerHTML = '<tr><td colspan="3">Could not load leaderboard data.</td></tr>';
        });
});
