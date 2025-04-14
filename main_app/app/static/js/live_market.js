document.addEventListener("DOMContentLoaded", function () {
    let allMarketData = []; // Store all market data for filtering
    
    // Load data and initialize
    fetchLiveData();
    
    // Set up auto-refresh every 60 seconds
    setInterval(fetchLiveData, 300000);
    
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

                console.log(allMarketData)
                
                // Sort by symbol
                allMarketData.sort((a, b) => 
                    a.stock_symbol.localeCompare(b.stock_symbol));
                
                // Render the active filter
                const activeFilter = document.querySelector('.filter-tab.active').dataset.filter;
                applyFilter(activeFilter);

                updateTimestamp();
                
                console.log("Data refreshed:", new Date().toLocaleTimeString());
            })
            .catch(error => console.error("Error loading market data:", error));
    }
    
    async function updateTimestamp() {
        try {
            const response = await fetch('/api/live-signals');
            const data = await response.json();
    
            if (data.length === 0) {
                console.error("No live signals data available.");
                return;
            }
    
            // Extract date and time from the first available stock entry
            const firstRecord = data[0]; 
    
            // Update date display
            const dateDisplay = document.getElementById("date-display");
            if (dateDisplay) {
                const date = new Date(firstRecord.date);
                dateDisplay.textContent = date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
            }
    
            // Update time display
            const timeDisplay = document.getElementById("time-display");
            if (timeDisplay) {
                timeDisplay.textContent = firstRecord.time; 
            }
    
        } catch (error) {
            console.error("Error fetching live signals:", error);
        }
    }
    
    // Call the function when the page loads
    updateTimestamp();    
    
    // Call the function when the page loads
    window.onload = updateTimestamp;
    
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

            // LTP (Last Traded Price)
            const ltpCell = document.createElement("td");
            ltpCell.textContent = record.ltp;  
            row.appendChild(ltpCell);

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