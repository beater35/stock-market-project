document.addEventListener("DOMContentLoaded", function () {
    let allMarketData = [];
    
    fetchLiveData();
    
    setInterval(fetchLiveData, 300000);
    
    function fetchLiveData() {
        const urlParams = new URLSearchParams(window.location.search);
        const debugMode = urlParams.get('debug') === 'true';
        
        const endpoint = debugMode ? '/api/live-indicators' : '/api/live-signals';
        
        fetch(endpoint)
            .then(response => response.json())
            .then(marketData => {
                allMarketData = marketData;
                
                if (debugMode) {
                    console.log("Debug mode: Using raw indicator values");
                } else {
                    calculateSentiment(allMarketData);
                }

                console.log(allMarketData)
                
                allMarketData.sort((a, b) => 
                    a.stock_symbol.localeCompare(b.stock_symbol));
                
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
    
            const firstRecord = data[0]; 
    
            const dateDisplay = document.getElementById("date-display");
            if (dateDisplay) {
                const date = new Date(firstRecord.date);
                dateDisplay.textContent = date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
            }
    
            const timeDisplay = document.getElementById("time-display");
            if (timeDisplay) {
                timeDisplay.textContent = firstRecord.time; 
            }
    
        } catch (error) {
            console.error("Error fetching live signals:", error);
        }
    }
    
    updateTimestamp();    
    
    window.onload = updateTimestamp;
    
    function calculateSentiment(data) {
        data.forEach(record => {
            const signals = [
                record.RSI || "", 
                record.SMA || "", 
                record.OBV || "", 
                record.Momentum || ""
            ];
            
            const buyCount = signals.filter(signal => signal === "Buy").length;
            const sellCount = signals.filter(signal => signal === "Sell").length;
            
            const adxBoost = (record.ADX === "Strong Trend") ? 0.5 : 0;
            
            if (buyCount > sellCount + adxBoost) {
                record.sentiment = "Bullish";
            } else if (sellCount > buyCount + adxBoost) {
                record.sentiment = "Bearish";
            } else {
                record.sentiment = "Neutral";
            }
        });
    }
    
    function renderTable(data) {
        const tableBody = document.querySelector("#indicatorsTable tbody");
        tableBody.innerHTML = ''; 
        
        const urlParams = new URLSearchParams(window.location.search);
        const debugMode = urlParams.get('debug') === 'true';
        
        data.forEach((record, index) => {
            const row = document.createElement("tr");
            
            const serialCell = document.createElement("td");
            serialCell.textContent = index + 1;
            row.appendChild(serialCell);
            
            const symbolCell = document.createElement("td");
            const link = document.createElement("a");
            link.href = `/company/${record.stock_symbol}`;
            link.textContent = record.stock_symbol;
            symbolCell.appendChild(link);
            row.appendChild(symbolCell);

            const ltpCell = document.createElement("td");
            ltpCell.textContent = record.ltp;  
            row.appendChild(ltpCell);

            const indicatorsList = ["RSI", "SMA", "OBV", "ADX", "Momentum"];
            indicatorsList.forEach(indicator => {
                const cell = document.createElement("td");
                const value = record[indicator];
                
                if (debugMode) {
                    if (value !== undefined && value !== null) {
                        cell.textContent = typeof value === 'number' ? value.toFixed(2) : value;
                    } else {
                        cell.textContent = "N/A";
                    }
                } else {
                    const signal = value || "N/A";
                    const signalSpan = document.createElement("span");
                    
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
            
            const sentimentCell = document.createElement("td");
            
            if (debugMode) {
                sentimentCell.textContent = "N/A (Debug)";
            } else {
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
    
    const filterTabs = document.querySelectorAll('.filter-tab');
    filterTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            filterTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.dataset.filter;
            applyFilter(filter);
        });
    });
    
    function applyFilter(filter) {
        const urlParams = new URLSearchParams(window.location.search);
        const debugMode = urlParams.get('debug') === 'true';
        
        let filteredData;
        
        if (debugMode || filter === 'all') {
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
    
    function updateStocksCount(count) {
        document.getElementById('stocksCount').textContent = count;
    }
});