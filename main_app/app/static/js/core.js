document.addEventListener("DOMContentLoaded", function () {
    Promise.all([
        fetch('/api/companies').then(response => response.json()),
        fetch('/api/indicators').then(response => response.json())
    ])
    .then(([companies, indicators]) => {
        const tableBody = document.querySelector("#indicatorsTable tbody");

        // Sort companies alphabetically by symbol
        companies.sort((a, b) => a.symbol.localeCompare(b.symbol));

        // Map indicators by stock symbol for easy lookup
        const indicatorsMap = {};
        indicators.forEach(ind => {
            indicatorsMap[ind.symbol] = ind;
        });

        // Iterate over companies and populate the table
        companies.forEach((company, index) => {
            const row = document.createElement("tr");

            // Serial Number (S. No.)
            const serialCell = document.createElement("td");
            serialCell.textContent = index + 1; // Starts from 1
            row.appendChild(serialCell);

            // Company Symbol (Clickable)
            const symbolCell = document.createElement("td");
            const link = document.createElement("a");
            link.href = `/company/${company.symbol}`;
            link.textContent = company.symbol;
            symbolCell.appendChild(link);
            row.appendChild(symbolCell);

            // Find the latest indicator values
            const indicatorData = indicatorsMap[company.symbol] || {};

            // Date Column
            const dateCell = document.createElement("td");
            dateCell.textContent = indicatorData.date || "N/A";
            row.appendChild(dateCell);

            // Technical Indicator Columns
            const indicatorsList = ["RSI", "SMA", "OBV", "ADX", "Momentum"];
            indicatorsList.forEach(indicator => {
                const cell = document.createElement("td");
                cell.textContent = indicatorData[indicator] !== undefined ? indicatorData[indicator] : "N/A";
                row.appendChild(cell);
            });

            tableBody.appendChild(row);
        });

        console.log("Total companies:", companies.length);
    })
    .catch(error => console.error("Error loading data:", error));
});
