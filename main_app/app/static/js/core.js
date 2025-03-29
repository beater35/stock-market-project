document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const debugMode = urlParams.has('debug');
    const apiEndpoint = debugMode ? '/api/indicators' : '/api/signals';
    let allCompanies = []; // Store all companies data for filtering
    
    // Load data and initialize
    fetch(apiEndpoint)
        .then(response => response.json())
        .then(companies => {
            allCompanies = companies;
            // Sort companies alphabetically by symbol
            allCompanies.sort((a, b) => a.symbol.localeCompare(b.symbol));
            renderTable(allCompanies);
            setupFilters();
            updateStocksCount(allCompanies.length);
            updateLastUpdatedDate(allCompanies);
        })
        .catch(error => console.error("Error loading data:", error));
    
    // Render table with given companies data
    function renderTable(companies) {
        const tableBody = document.querySelector("#indicatorsTable tbody");
        tableBody.innerHTML = ''; // Clear existing rows
        
        companies.forEach((company, index) => {
            const row = document.createElement("tr");
            
            // Serial Number
            const serialCell = document.createElement("td");
            serialCell.textContent = index + 1;
            row.appendChild(serialCell);
            
            // Company Symbol (Clickable)
            const symbolCell = document.createElement("td");
            const link = document.createElement("a");
            link.href = `/company/${company.symbol}`;
            link.textContent = company.symbol;
            symbolCell.appendChild(link);
            row.appendChild(symbolCell);

            // Closing Price Column
            const closePriceCell = document.createElement("td");
            closePriceCell.textContent = company.close_price || "N/A";  
            row.appendChild(closePriceCell);
            
            // Technical Indicator Signals
            const indicatorsList = ["RSI", "SMA", "OBV", "ADX", "Momentum"];
            indicatorsList.forEach(indicator => {
                const cell = document.createElement("td");
                const signal = company.signals[indicator] || "N/A";
                
                // Create a span for styled indicators
                const signalSpan = document.createElement("span");
                
                // Assign class based on signal type
                if (indicator === "ADX") {
                    if (signal === "Strong Trend") {
                        signalSpan.classList.add("strong-trend");
                        signalSpan.textContent = "Strong Trend";
                    } else if (signal === "Weak Trend") {
                        signalSpan.classList.add("weak-trend");
                        signalSpan.textContent = "Weak Trend";
                    } else {
                        signalSpan.textContent = signal;
                    }
                } else {
                    if (signal === "Buy") {
                        signalSpan.classList.add("buy");
                        signalSpan.textContent = "Buy";
                    } else if (signal === "Sell") {
                        signalSpan.classList.add("sell");
                        signalSpan.textContent = "Sell";
                    } else if (signal === "Hold") {
                        signalSpan.classList.add("hold");
                        signalSpan.textContent = "Hold";
                    } else {
                        signalSpan.textContent = signal;
                    }
                }
                
                cell.appendChild(signalSpan);
                row.appendChild(cell);
            });
            
            // Sentiment Column
            const sentimentCell = document.createElement("td");
            const sentimentSpan = document.createElement("span");
            const sentiment = company.sentiment || "Neutral";
            
            if (sentiment === "Bullish") {
                sentimentSpan.classList.add("bullish");
                sentimentSpan.textContent = "Bullish";
            } else if (sentiment === "Bearish") {
                sentimentSpan.classList.add("bearish");
                sentimentSpan.textContent = "Bearish";
            } else {
                sentimentSpan.classList.add("neutral");
                sentimentSpan.textContent = "Neutral";
            }
            
            sentimentCell.appendChild(sentimentSpan);
            row.appendChild(sentimentCell);
            
            // Actions Column
            const actionsCell = document.createElement("td");
            const detailsLink = document.createElement("a");
            detailsLink.href = `/company/${company.symbol}`;
            detailsLink.textContent = "Details";
            detailsLink.classList.add("details-link");
            actionsCell.appendChild(detailsLink);
            row.appendChild(actionsCell);
            
            tableBody.appendChild(row);
        });
    }
    
    // Set up filter tab functionality
    function setupFilters() {
        const filterTabs = document.querySelectorAll('.filter-tab');
        
        filterTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Remove active class from all tabs
                filterTabs.forEach(t => t.classList.remove('active'));
                // Add active class to clicked tab
                this.classList.add('active');
                
                const filter = this.dataset.filter;
                
                // Apply filter
                let filteredCompanies;
                if (filter === 'all') {
                    filteredCompanies = allCompanies;
                } else if (filter === 'bullish') {
                    filteredCompanies = allCompanies.filter(company => 
                        company.sentiment === 'Bullish');
                } else if (filter === 'bearish') {
                    filteredCompanies = allCompanies.filter(company => 
                        company.sentiment === 'Bearish');
                }
                
                renderTable(filteredCompanies);
                updateStocksCount(filteredCompanies.length);
            });
        });
    }
    
    // Update the stocks count display
    function updateStocksCount(count) {
        document.getElementById('stocksCount').textContent = count;
    }
    
    function updateLastUpdatedDate(companies) {
        // Find the most recent date from the companies (assuming dates are in "YYYY-MM-DD" format)
        const dates = companies.map(company => company.date).filter(date => date);
        const latestDate = new Date(Math.max(...dates.map(date => new Date(date).getTime())));
    
        // Format the date
        const formattedDate = latestDate.toLocaleDateString('en-US', {
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric'
        });
    
        // Update the last updated text
        document.getElementById('lastUpdated').textContent = formattedDate;
    }
});