import { indicatorConfig } from './indicatorConfig.js';

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

                // ✅ Add click listener if it's a real signal
                const validSignals = ["Buy", "Sell", "Hold", "Strong Trend", "Weak Trend"];
                if (validSignals.includes(signal)) {
                    signalSpan.style.cursor = "pointer";

                    // Bind signal and indicator value to the element
                    signalSpan.dataset.signalValue = signal;
                    signalSpan.addEventListener("click", () => {
                        showPopup(indicator.toLowerCase(), company.symbol, signalSpan.dataset.signalValue);
                    });

                    // ➕ Add visual-only info icon
                    const infoIcon = document.createElement("span");
                    infoIcon.textContent = " ⓘ";
                    infoIcon.classList.add("info-icon");
                    infoIcon.title = `More about ${indicator} signal`;

                    signalSpan.appendChild(infoIcon);
                }

                cell.appendChild(signalSpan);
                row.appendChild(cell);
            });

            
            // Signals Count Column
            const signalsCountCell = document.createElement("td");
            // Assuming `company.signals_count` is the array with [buy_count, sell_count, hold_count]
            const signalsCount = company.signals_count || [0, 0, 0]; 
            const buyCount = signalsCount[0];
            const sellCount = signalsCount[1];
            const holdCount = signalsCount[2];

            // Create container for the pills
            const pillsContainer = document.createElement("div");
            pillsContainer.style.display = "flex";
            pillsContainer.style.gap = "4px";

            // Create buy pill (green)
            const buyPill = document.createElement("span");
            buyPill.textContent = `${buyCount}`;
            buyPill.classList.add(buyCount > 0 ? "bullish" : "neutral");

            // Create sell pill (red)
            const sellPill = document.createElement("span");
            sellPill.textContent = `${sellCount}`;
            sellPill.classList.add(sellCount > 0 ? "bearish" : "neutral");

            pillsContainer.appendChild(buyPill);
            pillsContainer.appendChild(sellPill);

            if (holdCount > 0) {
            const holdPill = document.createElement("span");
            holdPill.textContent = `${holdCount}`;
            holdPill.classList.add("neutral");
            holdPill.classList.add("hold");
            holdPill.style.backgroundColor = "rgba(255, 193, 7, 0.1)";
            holdPill.style.color = "#ff9800";
            pillsContainer.appendChild(holdPill);
            }

            signalsCountCell.appendChild(pillsContainer);

            row.appendChild(signalsCountCell);

            
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
        const indicatorFilters = document.querySelectorAll('.filter-option');
        const allStocksBtn = document.querySelector('.filter-tab[data-filter="all"]');
        const activeFiltersContainer = document.getElementById('activeFilters');
        
        // Object to store active filters by indicator group
        let activeFiltersByGroup = {};
        
        // Basic tab filters
        filterTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Clear any active indicator filters
                activeFiltersByGroup = {};
                activeFiltersContainer.innerHTML = '';
                
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
        
        // Indicator filters
        indicatorFilters.forEach(option => {
            option.addEventListener('click', function() {
                const filter = this.dataset.filter;
                const filterName = this.innerText;
                const filterGroup = this.closest('.dropdown-section').querySelector('.dropdown-header').innerText;
                
                // Remove active class from all basic tabs
                filterTabs.forEach(tab => tab.classList.remove('active'));
                
                // Check if this group already has an active filter
                if (activeFiltersByGroup[filterGroup]) {
                    // Remove the old filter tag
                    const oldFilterTag = document.querySelector(`.active-filter[data-group="${filterGroup}"]`);
                    if (oldFilterTag) {
                        oldFilterTag.remove();
                    }
                }
                
                // Update the active filters object with the new selection
                activeFiltersByGroup[filterGroup] = {
                    filter: filter,
                    name: filterName,
                    group: filterGroup,
                    indicator: filterGroup.toLowerCase(),
                    signal: filterName
                };
                
                // Create active filter tag
                createActiveFilterTag(filter, `${filterGroup}: ${filterName}`, filterGroup);
                
                // Apply filters
                applyIndicatorFilters();
            });
        });
        
        // Create active filter tag
        function createActiveFilterTag(filter, text, group) {
            const tag = document.createElement('div');
            tag.className = 'active-filter';
            tag.setAttribute('data-group', group);
            tag.innerHTML = `${text} <span class="filter-remove" data-filter="${filter}" data-group="${group}">×</span>`;
            activeFiltersContainer.appendChild(tag);
            
            // Add event listener to remove button
            tag.querySelector('.filter-remove').addEventListener('click', function() {
                const groupToRemove = this.dataset.group;
                
                // Remove from active filters object
                delete activeFiltersByGroup[groupToRemove];
                tag.remove();
                
                if (Object.keys(activeFiltersByGroup).length === 0) {
                    allStocksBtn.classList.add('active');
                    renderTable(allCompanies);
                    updateStocksCount(allCompanies.length);
                } else {
                    applyIndicatorFilters();
                }
            });
        }
        
        // Apply indicator filters with AND condition
        function applyIndicatorFilters() {
            if (Object.keys(activeFiltersByGroup).length === 0) {
                renderTable(allCompanies);
                updateStocksCount(allCompanies.length);
                return;
            }
            
            // Filter companies based on indicator signals with AND condition
            const filteredCompanies = allCompanies.filter(company => {
                // Company must match ALL active filters (AND condition)
                return Object.values(activeFiltersByGroup).every(filter => {
                    // For ADX, handle "Strong Trend" and "Weak Trend"
                    if (filter.indicator.toUpperCase() === 'ADX') {
                        return company.signals.ADX === filter.signal;
                    }
                    // For other indicators
                    const indicatorKey = Object.keys(company.signals).find(
                        key => key.toLowerCase() === filter.indicator.toLowerCase()
                    );
                    return (company.signals[indicatorKey] || '').toLowerCase() === filter.signal.toLowerCase();
                    
                });
            });
            
            renderTable(filteredCompanies);
            updateStocksCount(filteredCompanies.length);
        }
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


    let chartInstance = null;

    function showPopup(indicator, symbol, signalValue) {
        const url = `/indicator_data/${symbol}/${indicator}`;
        
        // Get indicator configuration (or use default if not found)
        const config = indicatorConfig[indicator.toLowerCase()] || defaultIndicatorConfig;
        
        // Set indicator description
        document.getElementById('indicatorDescription').innerText = config.description;
        
        fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
            alert(data.error);
            return;
            }
            
            const labels = data.data.map(d => d.date);
            const values = data.data.map(d => d.value);
            const latestValue = values[values.length - 1];
            
            // Destroy previous chart if it exists
            if (chartInstance) {
            chartInstance.destroy();
            }
            
            const ctx = document.getElementById('indicatorChart').getContext('2d');
            const bgColor  = 'rgba(66, 133, 244, 0.3)';
            
            chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                label: `${indicator.toUpperCase()} - ${symbol}`,
                data: values,
                borderColor: config.borderColor,
                backgroundColor: bgColor,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 2,
                pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                legend: {
                    display: true,
                    position: 'top',
                }
                },
                scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                    display: false
                    }
                }
                }
            }
            });

            
            // Update modal content
            document.getElementById('popupTitle').innerHTML = `${indicator.toUpperCase()} <span class="symbol">(${symbol})</span>`;
            document.getElementById('chartSubtitle').innerText = `${indicator.toUpperCase()} signal for ${symbol}`;
            
            // Find applicable rule from config
            const rule = config.signalRules.find(rule => rule.condition(signalValue, latestValue));
            
            // Apply the rule to generate signal and explanation
            const signal = rule.signal;
            const explanation = rule.explanation(latestValue);
            
            // Update explanation text
            document.getElementById('explanationText').innerText = explanation;
            
            // Update signal type
            const signalTypeElement = document.getElementById('signalType');
            signalTypeElement.innerText = signal;
            signalTypeElement.className = '';
            
            if (signal.toLowerCase() === 'buy') {
            signalTypeElement.classList.add('signal-type-buy');
            } else if (signal.toLowerCase() === 'sell') {
            signalTypeElement.classList.add('signal-type-sell');
            } else {
            signalTypeElement.classList.add('signal-type-neutral');
            }
            
            // Show the modal
            document.getElementById('popupModal').style.display = 'block';
        })
        .catch(err => {
            console.error(err);
            alert("Failed to fetch indicator data.");
        });
    }
    
    // Close modal
    document.querySelector('.close').onclick = function () {
        document.getElementById('popupModal').style.display = 'none';
    };
    
    window.onclick = function (event) {
        if (event.target === document.getElementById('popupModal')) {
        document.getElementById('popupModal').style.display = 'none';
        }
    };
});