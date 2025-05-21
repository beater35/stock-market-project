import { indicatorConfig } from './indicatorConfig.js';

document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const debugMode = urlParams.has('debug');
    const apiEndpoint = debugMode ? '/api/indicators' : '/api/signals';
    let allCompanies = []; 

    function downloadTableAsCSV() {
        const button = document.getElementById("downloadCSV");
        if (!button) return;

        button.disabled = false;
        button.addEventListener("click", function () {
            const table = document.querySelector("#indicatorsTable");
            if (!table) {
                alert("Table not found.");
                return;
            }

            let csv = [];
            for (let row of table.rows) {
                let rowData = [];
                for (let cell of row.cells) {
                    rowData.push('"' + cell.innerText.replace(/"/g, '""') + '"');
                }
                csv.push(rowData.join(","));
            }

            const csvContent = csv.join("\n");
            const blob = new Blob([csvContent], { type: "text/csv" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `signals_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        });
    }
    
    const cachedData = sessionStorage.getItem(apiEndpoint);

    // if (cachedData) {
    //     const companies = JSON.parse(cachedData);
    //     allCompanies = companies;
    //     allCompanies.sort((a, b) => a.symbol.localeCompare(b.symbol));
    //     renderTable(allCompanies);
    //     setupFilters();
    //     updateStocksCount(allCompanies.length);
    //     updateLastUpdatedDate(allCompanies);
    // } else {
    //     fetch(apiEndpoint)
    //         .then(response => response.json())
    //         .then(companies => {
    //             sessionStorage.setItem(apiEndpoint, JSON.stringify(companies)); // cache the data
    //             allCompanies = companies;
    //             allCompanies.sort((a, b) => a.symbol.localeCompare(b.symbol));
    //             renderTable(allCompanies);
    //             setupFilters();
    //             updateStocksCount(allCompanies.length);
    //             updateLastUpdatedDate(allCompanies);
    //         })
    //         .catch(error => console.error("Error loading data:", error));
    // }

    const cached = localStorage.getItem(apiEndpoint);
    const cachedTime = localStorage.getItem(apiEndpoint + "_time");

    const now = new Date();
    const isAfter3PM = now.getHours() >= 15;

    if (cached && cachedTime) {
        const cacheDate = new Date(cachedTime);

        const isSameDay = now.toDateString() === cacheDate.toDateString();

        // If it's the same day, use cache
        // If it's a new day and before 3 PM, still use yesterday's data
        // If it's a new day and after 3 PM, refetch
        if (isSameDay || (!isSameDay && !isAfter3PM)) {
            const companies = JSON.parse(cached);
            allCompanies = companies;
            allCompanies.sort((a, b) => a.symbol.localeCompare(b.symbol));
            renderTable(allCompanies);
            setupFilters();
            updateStocksCount(allCompanies.length);
            updateLastUpdatedDate(allCompanies);
        } else {
            fetchAndCache(); // New day + after 3 PM → fetch new data
        }
    } else {
        fetchAndCache(); // No cache → fetch
    }

    function fetchAndCache() {
        fetch(apiEndpoint)
            .then(response => response.json())
            .then(companies => {
                localStorage.setItem(apiEndpoint, JSON.stringify(companies));
                localStorage.setItem(apiEndpoint + "_time", new Date().toISOString());

                allCompanies = companies;
                allCompanies.sort((a, b) => a.symbol.localeCompare(b.symbol));
                renderTable(allCompanies);
                setupFilters();
                updateStocksCount(allCompanies.length);
                updateLastUpdatedDate(allCompanies);
            })
            .catch(error => console.error("Error loading data:", error));
    }

    
    function renderTable(companies) {
        const tableBody = document.querySelector("#indicatorsTable tbody");
        tableBody.innerHTML = ''; 
        
        companies.forEach((company, index) => {
            const row = document.createElement("tr");
            
            const serialCell = document.createElement("td");
            serialCell.textContent = index + 1;
            row.appendChild(serialCell);
            
            const symbolCell = document.createElement("td");
            const link = document.createElement("a");
            link.href = `/company/${company.symbol}`;
            link.textContent = company.symbol;
            symbolCell.appendChild(link);
            row.appendChild(symbolCell);

            const closePriceCell = document.createElement("td");
            closePriceCell.textContent = company.close_price || "N/A";  
            row.appendChild(closePriceCell);
            
            const indicatorsList = ["RSI", "SMA", "OBV", "ADX", "Momentum"];
            indicatorsList.forEach(indicator => {
                const cell = document.createElement("td");
                const signal = company.signals[indicator] || "N/A";

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
                        signalSpan.textContent = "Bullish";
                    } else if (signal === "Sell") {
                        signalSpan.classList.add("sell");
                        signalSpan.textContent = "Bearish";
                    } else if (signal === "Hold") {
                        signalSpan.classList.add("hold");
                        signalSpan.textContent = "Neutral";
                    } else {
                        signalSpan.textContent = signal;
                    }
                }

                const validSignals = ["Buy", "Sell", "Hold", "Strong Trend", "Weak Trend"];
                if (validSignals.includes(signal)) {
                    signalSpan.style.cursor = "pointer";

                    signalSpan.dataset.signalValue = signal;
                    signalSpan.addEventListener("click", () => {
                        showPopup(indicator.toLowerCase(), company.symbol, signalSpan.dataset.signalValue);
                    });

                    const infoIcon = document.createElement("span");
                    infoIcon.textContent = " ⓘ";
                    infoIcon.classList.add("info-icon");
                    infoIcon.title = `More about ${indicator} signal`;

                    signalSpan.appendChild(infoIcon);
                }

                cell.appendChild(signalSpan);
                row.appendChild(cell);
            });

            
            const signalsCountCell = document.createElement("td");
            const signalsCount = company.signals_count || [0, 0, 0]; 
            const buyCount = signalsCount[0];
            const sellCount = signalsCount[1];
            const holdCount = signalsCount[2];

            const pillsContainer = document.createElement("div");
            pillsContainer.style.display = "flex";
            pillsContainer.style.gap = "4px";

            const buyPill = document.createElement("span");
            buyPill.textContent = `${buyCount}`;
            buyPill.classList.add(buyCount > 0 ? "bullish" : "neutral");

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

            
            const actionsCell = document.createElement("td");
            const detailsLink = document.createElement("a");
            detailsLink.href = `/company/${company.symbol}`;
            detailsLink.textContent = "Details";
            detailsLink.classList.add("details-link");
            actionsCell.appendChild(detailsLink);
            row.appendChild(actionsCell);
            
            tableBody.appendChild(row);
        });

        downloadTableAsCSV();
    }
    
    function setupFilters() {
        const filterTabs = document.querySelectorAll('.filter-tab');
        const indicatorFilters = document.querySelectorAll('.filter-option');
        const allStocksBtn = document.querySelector('.filter-tab[data-filter="all"]');
        const activeFiltersContainer = document.getElementById('activeFilters');
        
        let activeFiltersByGroup = {};
        
        filterTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                activeFiltersByGroup = {};
                activeFiltersContainer.innerHTML = '';
                
                filterTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                const filter = this.dataset.filter;
                
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
        
        indicatorFilters.forEach(option => {
            option.addEventListener('click', function() {
                const filter = this.dataset.filter;
                const textToSignal = {
                    'Bullish': 'Buy',
                    'Bearish': 'Sell',
                    'Neutral': 'Hold',
                    'Strong Trend': 'Strong Trend',
                    'Weak Trend': 'Weak Trend'
                };
                const filterName = textToSignal[this.innerText] || this.innerText;
                const filterGroup = this.closest('.dropdown-section').querySelector('.dropdown-header').innerText;
                
                filterTabs.forEach(tab => tab.classList.remove('active'));
                
                if (activeFiltersByGroup[filterGroup]) {
                    const oldFilterTag = document.querySelector(`.active-filter[data-group="${filterGroup}"]`);
                    if (oldFilterTag) {
                        oldFilterTag.remove();
                    }
                }
                
                activeFiltersByGroup[filterGroup] = {
                    filter: filter,
                    name: filterName,
                    group: filterGroup,
                    indicator: filterGroup.toLowerCase(),
                    signal: filterName
                };
                
                createActiveFilterTag(filter, `${filterGroup}: ${this.innerText}`, filterGroup);
                
                applyIndicatorFilters();
            });
        });
        
        function createActiveFilterTag(filter, text, group) {
            const tag = document.createElement('div');
            tag.className = 'active-filter';
            tag.setAttribute('data-group', group);
            tag.innerHTML = `${text} <span class="filter-remove" data-filter="${filter}" data-group="${group}">×</span>`;
            activeFiltersContainer.appendChild(tag);
            
            tag.querySelector('.filter-remove').addEventListener('click', function() {
                const groupToRemove = this.dataset.group;
                
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
        
        function applyIndicatorFilters() {
            if (Object.keys(activeFiltersByGroup).length === 0) {
                renderTable(allCompanies);
                updateStocksCount(allCompanies.length);
                return;
            }
            
            const filteredCompanies = allCompanies.filter(company => {
                return Object.values(activeFiltersByGroup).every(filter => {
                    if (filter.indicator.toUpperCase() === 'ADX') {
                        return company.signals.ADX === filter.signal;
                    }
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
    
    function updateStocksCount(count) {
        document.getElementById('stocksCount').textContent = count;
    }
    
    function updateLastUpdatedDate(companies) {
        const dates = companies.map(company => company.date).filter(date => date);
        const latestDate = new Date(Math.max(...dates.map(date => new Date(date).getTime())));
    
        const formattedDate = latestDate.toLocaleDateString('en-US', {
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric'
        });
    
        document.getElementById('lastUpdated').textContent = formattedDate;
    }


    let chartInstance = null;

    function showPopup(indicator, symbol, signalValue) {
        const url = `/indicator_data/${symbol}/${indicator}`;
        
        const config = indicatorConfig[indicator.toLowerCase()];
        
        document.getElementById('indicatorDescription').innerText = config.description;
        
        fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
            alert(data.error);
            return;
            }
            const sortedData = data.data.sort((a, b) => new Date(a.date) - new Date(b.date));
            
            const labels = sortedData.map(d => d.date);
            const values = sortedData.map(d => d.value);
            const latestValue = values[values.length - 1];

            const priceMap = {};
            data.closing_prices.forEach(p => {
                priceMap[p.date] = p.close;
            });
            
            if (chartInstance) {
            chartInstance.destroy();
            }
            
            const ctx = document.getElementById('indicatorChart').getContext('2d');
            const bgColor  = 'rgba(66, 133, 244, 0.3)';
            
            const datasets = [{
                label: `${indicator.toUpperCase()} - ${symbol}`,
                data: values,
                borderColor: config.borderColor,
                backgroundColor: bgColor,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 2,
                pointHoverRadius: 5
            }];

            let chartOptions = {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
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
            };
        
            if (indicator.toLowerCase() === 'sma') {
                const closingValues = data.closing_prices.map(p => p.close);
            
                datasets.push({
                    label: `Closing Price - ${symbol}`,
                    data: closingValues,
                    borderColor: 'rgba(255, 99, 132, 0.8)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 1,
                    pointHoverRadius: 4
                });
            
            }
            else if (indicator.toLowerCase() === 'obv') {
                const obvValues = data.data.map(d => d.value);
                const closingValues = data.closing_prices.map(p => p.close);
            
                datasets.push({
                    label: 'OBV',
                    data: obvValues,
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.1,
                    fill: true,
                    yAxisID: 'y',
                });
            
                datasets.push({
                    label: 'Close Price',
                    data: closingValues,
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    tension: 0.1,
                    fill: true,
                    yAxisID: 'y1',
                });
            
                chartOptions.scales = {
                    y: {
                        type: 'linear',
                        position: 'left',
                        title: {
                            display: true,
                            text: 'OBV'
                        }
                    },
                    y1: {
                        type: 'linear',
                        position: 'right',
                        grid: {
                            drawOnChartArea: false,
                        },
                        title: {
                            display: true,
                            text: 'Price'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                };
            }
            
        
            chartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: datasets
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

            
            document.getElementById('popupTitle').innerHTML = `${indicator.toUpperCase()} <span class="symbol">(${symbol})</span>`;
            document.getElementById('chartSubtitle').innerText = `${indicator.toUpperCase()} signal for ${symbol}`;
            
            const rule = config.signalRules.find(rule => rule.condition(signalValue, latestValue));
            
            const signal = rule.signal;
            const explanation = rule.explanation(latestValue);
            
            document.getElementById('explanationText').innerText = explanation;
            
            const signalTypeElement = document.getElementById('signalType');
            signalTypeElement.innerText = signal;
            signalTypeElement.className = '';
            
            if (signal.toLowerCase() === 'buy') {
                signalTypeElement.classList.add('signal-type-buy');
                signalTypeElement.innerText = "Bullish";
            } else if (signal.toLowerCase() === 'sell') {
                signalTypeElement.classList.add('signal-type-sell');
                signalTypeElement.innerText = "Bearish";
            } else {
                signalTypeElement.classList.add('signal-type-neutral');
                if (indicator.toLowerCase() === 'adx') {
                    signalTypeElement.innerText = signal;
                } else {
                    signalTypeElement.innerText = "Neutral";
                }
            }
            
            document.getElementById('popupModal').style.display = 'block';
        })
        .catch(err => {
            console.error(err);
            alert("Failed to fetch indicator data.");
        });
    }
    
    document.querySelector('.close').onclick = function () {
        document.getElementById('popupModal').style.display = 'none';
    };
    
    window.onclick = function (event) {
        if (event.target === document.getElementById('popupModal')) {
        document.getElementById('popupModal').style.display = 'none';
        }
    };
});