document.addEventListener("DOMContentLoaded", function () {
    let allMarketData = []; // Store all market data for filtering
    
    // Load data and initialize
    fetchLiveData();
    
    // Set up auto-refresh every 60 seconds
    setInterval(fetchLiveData, 60000);
    
    function fetchLiveData() {
        // Check if debug mode is enabled in URL
        const urlParams = new URLSearchParams(window.location.search);
        const debugMode = urlParams.get('debug') === 'true';
        
        // Use different endpoint based on debug mode
        const endpoint = debugMode ? '/api/live-indicators' : '/api/live-signals';
        
        fetch(endpoint)
            .then(response => response.json())
            .then(marketData => {
                allMarketData = marketData;
                
                if (debugMode) {
                    // In debug mode, we're using raw indicator values
                    console.log("Debug mode: Using raw indicator values");
                } else {
                    // In normal mode, calculate sentiment based on Buy/Sell signals
                    calculateSentiment(allMarketData);
                }
                
                // Sort by symbol
                allMarketData.sort((a, b) => 
                    a.stock_symbol.localeCompare(b.stock_symbol));
                
                // Render the active filter
                const activeFilter = document.querySelector('.filter-tab.active').dataset.filter;
                applyFilter(activeFilter);
                
                console.log("Data refreshed:", new Date().toLocaleTimeString());
            })
            .catch(error => console.error("Error loading market data:", error));
    }
    
    // Calculate sentiment based on indicator signals
    function calculateSentiment(data) {
        data.forEach(record => {
            // Count buy and sell signals
            const signals = [
                record.RSI || "", 
                record.SMA || "", 
                record.OBV || "", 
                record.Momentum || ""
            ];
            
            const buyCount = signals.filter(signal => signal === "Buy").length;
            const sellCount = signals.filter(signal => signal === "Sell").length;
            
            // Add ADX as a modifying factor
            const adxBoost = (record.ADX === "Strong Trend") ? 0.5 : 0;
            
            // Determine sentiment
            if (buyCount > sellCount + adxBoost) {
                record.sentiment = "Bullish";
            } else if (sellCount > buyCount + adxBoost) {
                record.sentiment = "Bearish";
            } else {
                record.sentiment = "Neutral";
            }
        });
    }
    
    // Render table with given market data
    function renderTable(data) {
        const tableBody = document.querySelector("#indicatorsTable tbody");
        tableBody.innerHTML = ''; // Clear existing rows
        
        // Check if debug mode is enabled
        const urlParams = new URLSearchParams(window.location.search);
        const debugMode = urlParams.get('debug') === 'true';
        
        data.forEach((record, index) => {
            const row = document.createElement("tr");
            
            // Serial Number
            const serialCell = document.createElement("td");
            serialCell.textContent = index + 1;
            row.appendChild(serialCell);
            
            // Company Symbol
            const symbolCell = document.createElement("td");
            const link = document.createElement("a");
            link.href = `/company/${record.stock_symbol}`;
            link.textContent = record.stock_symbol;
            symbolCell.appendChild(link);
            row.appendChild(symbolCell);
            
            // Date Column
            const dateCell = document.createElement("td");
            dateCell.textContent = record.date || "N/A";
            row.appendChild(dateCell);
            
            // Time Column
            const timeCell = document.createElement("td");
            timeCell.classList.add("time-cell");

            const timeIcon = document.createElement("div");
            timeIcon.classList.add("time-icon");
            timeIcon.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
            <path d="M8 4.5a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-.5.5H4.5a.5.5 0 0 1 0-1h3V5a.5.5 0 0 1 .5-.5z"/>
            </svg>
            `;

            const timeText = document.createElement("span");
            timeText.classList.add("time-text");

            // Format time to remove seconds
            const formatTime = (timeString) => {
                if (!timeString) return "N/A";
                return timeString.slice(0, 5); // HH:MM format
            };

            timeText.textContent = formatTime(record.time);

            timeCell.appendChild(timeIcon);
            timeCell.appendChild(timeText);
            row.appendChild(timeCell);
            
            // Technical Indicator Signals
            const indicatorsList = ["RSI", "SMA", "OBV", "ADX", "Momentum"];
            indicatorsList.forEach(indicator => {
                const cell = document.createElement("td");
                const value = record[indicator];
                
                if (debugMode) {
                    // In debug mode, display raw numeric values
                    if (value !== undefined && value !== null) {
                        cell.textContent = typeof value === 'number' ? value.toFixed(2) : value;
                    } else {
                        cell.textContent = "N/A";
                    }
                } else {
                    // In normal mode, display styled Buy/Sell signals
                    const signal = value || "N/A";
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
                }
                
                row.appendChild(cell);
            });
            
            // Sentiment Column
            const sentimentCell = document.createElement("td");
            
            if (debugMode) {
                // In debug mode, don't calculate sentiment
                sentimentCell.textContent = "N/A (Debug)";
            } else {
                // In normal mode, show styled sentiment
                const sentimentSpan = document.createElement("span");
                const sentiment = record.sentiment || "Neutral";
                
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
            }
            
            row.appendChild(sentimentCell);
            
            // Actions Column
            const actionsCell = document.createElement("td");
            const detailsLink = document.createElement("a");
            detailsLink.href = `/company/${record.stock_symbol}`;
            detailsLink.textContent = "Details";
            detailsLink.classList.add("details-link");
            actionsCell.appendChild(detailsLink);
            row.appendChild(actionsCell);
            
            tableBody.appendChild(row);
        });
    }
    
    // Set up filter tab functionality
    const filterTabs = document.querySelectorAll('.filter-tab');
    filterTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            filterTabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            applyFilter(filter);
        });
    });
    
    // Apply filter to the data
    function applyFilter(filter) {
        // Check if in debug mode
        const urlParams = new URLSearchParams(window.location.search);
        const debugMode = urlParams.get('debug') === 'true';
        
        let filteredData;
        
        if (debugMode || filter === 'all') {
            // In debug mode, always show all data regardless of filter
            filteredData = allMarketData;
        } else if (filter === 'bullish') {
            filteredData = allMarketData.filter(record => 
                record.sentiment === 'Bullish');
        } else if (filter === 'bearish') {
            filteredData = allMarketData.filter(record => 
                record.sentiment === 'Bearish');
        }
        
        renderTable(filteredData);
        updateStocksCount(filteredData.length);
    }
    
    // Update the stocks count display
    function updateStocksCount(count) {
        document.getElementById('stocksCount').textContent = count;
    }
});