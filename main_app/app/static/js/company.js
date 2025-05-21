document.addEventListener("DOMContentLoaded", () => {
    let signalRSI;
    let signalSMA;
    let signalOBV;
    let signalADX;
    let signalMOMENTUM;

    const pathParts = window.location.pathname.split('/');
    const symbol = pathParts[pathParts.length - 1];
    const exportBtn = document.querySelector(".export-btn");

    exportBtn.addEventListener("click", function () {
        const element = document.getElementById("pdfContent");
        const opt = {
            margin:       0.5,
            filename:     'stock_signals.pdf',
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2 },
            jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
        };
        html2pdf().from(element).set(opt).save();
    });

    fetch(`/api/company/${symbol}/data`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (!data || !data.stock_data || !data.indicator_data) return;

            const stockData = data.stock_data;
            const indicatorData = data.indicator_data;
            const companyData = data.company_data;
            const latestSignals = data.latest_signals;
            const lastStock = stockData[stockData.length - 1];

            const lastDate = stockData.at(-1)?.date || new Date().toISOString().slice(0, 10);
            const formattedDate = new Date(lastDate).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            document.querySelector(".date-updated").textContent = `Last updated on: ${formattedDate}`;
            document.querySelector(".company-name").textContent = companyData.company_name || 'Unknown Company';
            document.querySelector(".company-symbol").textContent = symbol;
            document.querySelector(".company-sector").textContent = companyData.sector || 'Unknown Sector';

            const currentPrice = lastStock.close;  
            const previousClose = stockData[stockData.length - 2]?.close || currentPrice; 
            const priceChangeVal = currentPrice - previousClose;
            const priceChange = priceChangeVal.toFixed(2);
            const priceChangePercentage = ((priceChangeVal / previousClose) * 100).toFixed(2);
            const high52Week = Math.max(...stockData.map(data => data.high)); 
            const low52Week = Math.min(...stockData.map(data => data.low));  
            const volume = (lastStock.volume / 1_000).toFixed(2); 

            document.querySelector(".price-value.current-price").textContent = `${currentPrice.toFixed(2)}`;
            document.querySelector(".price-value.previous-close").textContent = `${previousClose.toFixed(2)}`;
            const sign = priceChangeVal >= 0 ? "+" : "";
            document.querySelector(".price-value.price-change").textContent = `${sign}${priceChange} (${sign}${priceChangePercentage}%)`;
            document.querySelector(".price-value.high-52week").textContent = `${high52Week.toFixed(2)}`;
            document.querySelector(".price-value.low-52week").textContent = `${low52Week.toFixed(2)}`;
            document.querySelector(".price-value.volume").textContent = `${volume}k`;
            
            if (priceChange > 0) {
                document.querySelector(".price-value.price-change").classList.add("price-up");
                document.querySelector(".price-value.price-change").classList.remove("price-down");
            } else {
                document.querySelector(".price-value.price-change").classList.add("price-down");
                document.querySelector(".price-value.price-change").classList.remove("price-up");
            }


            function renderPriceChart(stockData, period = 30) {
                const filteredData = filterDataByDateRange(stockData, period);
                
                const ctx = document.getElementById('priceChart').getContext('2d');
                
                if (window.priceChart instanceof Chart) {
                    window.priceChart.destroy();
                }
                
                const labels = filteredData.map(d => {
                    return new Date(d.date || d.x).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                    });
                });
                
                const closePrices = filteredData.map(data => data.close);
                const volumeData = filteredData.map(data => data.volume);

                window.priceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                    {
                        label: 'Price',
                        data: closePrices,
                        borderColor: '#36caad',
                        backgroundColor: 'rgba(54, 202, 173, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.2,
                        pointRadius: 3,
                        pointHoverRadius: 5,
                        yAxisID: 'y',
                    }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    
                    plugins: {
                    legend: {
                        display: false 
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                        label: function(context) {
                            return `Price: $${context.raw.toFixed(2)}`;
                        }
                        }
                    }
                    },
                    interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                    },
                    scales: {
                    x: {
                        grid: {
                        display: false
                        },
                        ticks: {
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 10
                        }
                    },
                    y: {
                        position: 'right',
                        grid: {
                        color: 'rgba(200, 200, 200, 0.2)'
                        },
                        ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                        }
                    }
                    }
                }
                });
                
                return window.priceChart;
            }

            function filterDataByDateRange(data, months) {
                if (!months) return data;
            
                const cutoffDate = luxon.DateTime.now().minus({ months: months });
                
                return data.filter(d => {
                    const entryDate = luxon.DateTime.fromISO(d.date || d.x); 
                    return entryDate >= cutoffDate;
                });
            }
            

            function setupPeriodSelectors() {
                const tabElements = document.querySelectorAll('.tabs .tab');
                const periodsInMonths = [3, 2, 1]; 
            
                tabElements.forEach((tab, index) => {
                    tab.addEventListener('click', function () {
                        tabElements.forEach(t => t.classList.remove('active'));
                        this.classList.add('active');
            
                        const filteredData = filterDataByDateRange(stockData, periodsInMonths[index]);
                        renderPriceChart(filteredData); 
                    });
                });
            }
            
            setupPeriodSelectors();
            renderPriceChart(stockData);


            // RSI
            const lastIndicator = indicatorData[indicatorData.length - 1];
            const lastRSI = lastIndicator.rsi;
            const rsiSignal = latestSignals.RSI;            
            
            const rsiConfig = indicatorConfigure['rsi'];
            
            document.getElementById('indicator-description-rsi').textContent = rsiConfig.description;
            
            document.querySelector('.indicator-name').textContent = "RSI (Relative Strength Index)";
            document.getElementById('indicator-value-rsi').textContent = lastRSI.toFixed(1);            

            let rsiExplanation = "";
            for (let rule of rsiConfig.signalRules) {
                if (rule.condition.length === 1 && typeof rule.condition(rsiSignal) === 'boolean') {
                    if (rule.condition(rsiSignal)) {
                        rsiExplanation = rule.explanation(lastRSI);
                        break;
                    }
                } else if (rule.condition(lastRSI)) {
                    rsiExplanation = rule.explanation(lastRSI);
                    break;
                }
            }
            
            document.getElementById("rsi-summary").textContent = rsiExplanation;

            const rsiBadge = document.getElementById('rsi-badge');
            if (rsiSignal === "Buy") {
                rsiBadge.textContent = "Bullish";
                rsiBadge.className = "signal-badge signal-buy";
                signalRSI = { label: "bullish", value: 1 };
            } else if (lastRSI === "Bearish") {
                rsiBadge.textContent = "Sell";
                rsiBadge.className = "signal-badge signal-sell";
                signalRSI = { label: "bearish", value: -1 };
            } else {
                rsiBadge.textContent = "Neutral";
                rsiBadge.className = "signal-badge signal-hold";
                signalRSI = { label: "neutral", value: 0 };
            }

            const rsiLabels = stockData.map(data => data.date); 
            const rsiValues = indicatorData.map(data => data.rsi); 

            const ctx = document.getElementById('rsiChart').getContext('2d');
            const rsiChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: rsiLabels,
                    datasets: [
                        {
                            label: 'RSI',
                            data: rsiValues,
                            borderColor: '#4285F4',
                            backgroundColor: 'rgba(66, 133, 244, 0.1)',
                            tension: 0,
                            fill: true,
                            pointRadius: 3,
                        },
                        {
                            label: 'Overbought (70)',
                            data: new Array(rsiLabels.length).fill(70),
                            borderColor: 'rgba(255, 99, 132, 0.5)',
                            borderDash: [5, 5],
                            pointRadius: 0,
                            fill: false
                        },
                        {
                            label: 'Oversold (30)',
                            data: new Array(rsiLabels.length).fill(30),
                            borderColor: 'rgba(75, 192, 192, 0.5)',
                            borderDash: [5, 5],
                            pointRadius: 0,
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            min: 0,
                            max: 100,
                            title: {
                                display: true,
                                text: 'RSI Value'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            });

            // SMA 20
            const lastSMA = lastIndicator.sma;
            const smaSignal = latestSignals.SMA;
            
            const smaConfig = indicatorConfigure['sma'];
            
            document.getElementById('indicator-description-sma').textContent = smaConfig.description;
            document.getElementById('indicator-value-sma').textContent = lastSMA.toFixed(1);            
                        
            let smaExplanation = "";
            for (let rule of smaConfig.signalRules) {
                if (rule.condition.length === 1 && typeof rule.condition(smaSignal) === 'boolean') {
                    if (rule.condition(smaSignal)) {
                        smaExplanation = rule.explanation(lastSMA);
                        break;
                    }
                } else if (rule.condition(lastSMA)) {
                    smaExplanation = rule.explanation(lastSMA);
                    break;
                }
            }
            
            document.getElementById("sma-summary").textContent = smaExplanation;

            const smaBadge = document.getElementById('sma-badge');
            if (smaSignal === "Buy") {
                smaBadge.textContent = "Bullish";
                smaBadge.className = "signal-badge signal-buy";
                signalSMA = { label: "bullish", value: 1 };
            } else if (smaSignal === "Sell") {
                smaBadge.textContent = "Bearish";
                smaBadge.className = "signal-badge signal-sell";
                signalSMA = { label: "bearish", value: -1 };
            } else {
                smaBadge.textContent = "Neutral";
                smaBadge.className = "signal-badge signal-hold";
                signalSMA = { label: "neutral", value: 0 };
            }

            const smaLabels = stockData.map(data => data.date); 
            const priceValues = stockData.map(data => data.close); 
            const smaValues = indicatorData.map(data => data.sma); 

            const smaCtx = document.getElementById('smaChart').getContext('2d');
            const smaChart = new Chart(smaCtx, {
                type: 'line',
                data: {
                    labels: smaLabels,
                    datasets: [
                        {
                            label: 'Closing Price',
                            data: priceValues,
                            borderColor: '#1E88E5',
                            backgroundColor: 'rgba(30, 136, 229, 0.1)',
                            tension: 0.3,
                            fill: true,
                            pointRadius: 2
                        },
                        {
                            label: 'SMA (20)',
                            data: smaValues,
                            borderColor: '#43A047',
                            backgroundColor: 'rgba(67, 160, 71, 0.1)',
                            tension: 0.3,
                            fill: false,
                            pointRadius: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Price'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            });

            // OBV
            const lastOBV = lastIndicator.obv;
            const obvSignal = latestSignals.OBV;
            
            const obvConfig = indicatorConfigure['obv'];
            
            document.getElementById('indicator-description-obv').textContent = obvConfig.description;

            let value;
            if (obvSignal === 'Buy') {
                value = "Rising"
            } else if (obvSignal === 'Sell') {
                value = "Falling"
            } else {
                value = "Neutral"
            }
            document.getElementById('indicator-value-obv').textContent = value;
            
            // document.querySelector('.indicator-value').textContent = lastOBV.toFixed(1);
            
            let obvExplanation = "";
            for (let rule of obvConfig.signalRules) {
                if (rule.condition.length === 1 && typeof rule.condition(obvSignal) === 'boolean') {
                    if (rule.condition(obvSignal)) {
                        obvExplanation = rule.explanation(lastOBV);
                        break;
                    }
                } else if (rule.condition(lastOBV)) {
                    obvExplanation = rule.explanation(lastOBV);
                    break;
                }
            }
            
            document.getElementById("obv-summary").textContent = obvExplanation;

            const obvBadge = document.getElementById('obv-badge');
            if (obvSignal === "Buy") {
                obvBadge.textContent = "Bullish";
                obvBadge.className = "signal-badge signal-buy";
                signalOBV = { label: "bullish", value: 1 };
            } else if (obvSignal === "Sell") {
                obvBadge.textContent = "Bearish";
                obvBadge.className = "signal-badge signal-sell";
                signalOBV = { label: "bearish", value: -1 };
            } else {
                obvBadge.textContent = "Neutral";
                obvBadge.className = "signal-badge signal-hold";
                signalOBV = { label: "neutral", value: 0 };
            }

            const obvLabels = stockData.map(data => data.date);
            const obvValues = indicatorData.map(data => data.obv);
            const closePrices = stockData.map(data => data.close);

            const obvCtx = document.getElementById('obvChart').getContext('2d');
            const obvChart = new Chart(obvCtx, {
                type: 'line',
                data: {
                    labels: obvLabels,
                    datasets: [
                        {
                            label: 'OBV',
                            data: obvValues,
                            borderColor: '#4CAF50',
                            backgroundColor: 'rgba(76, 175, 80, 0.1)',
                            tension: 0,
                            fill: true,
                            yAxisID: 'y',
                        },
                        {
                            label: 'Close Price',
                            data: closePrices,
                            borderColor: '#2196F3',
                            backgroundColor: 'rgba(33, 150, 243, 0.1)',
                            tension: 0,
                            fill: true,
                            yAxisID: 'y1',
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
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
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            });

            // ADX
            const lastADX = lastIndicator.adx;
            const adxSignal = latestSignals.ADX;
            
            const adxConfig = indicatorConfigure['adx'];
            
            document.getElementById('indicator-description-adx').textContent = adxConfig.description;
            
            document.getElementById('indicator-value-adx').textContent = lastADX.toFixed(1);
            
            let adxExplanation = "";
            for (let rule of adxConfig.signalRules) {
                if (rule.condition.length === 1 && typeof rule.condition(adxSignal) === 'boolean') {
                    if (rule.condition(adxSignal)) {
                        adxExplanation = rule.explanation(lastADX);
                        break;
                    }
                } else if (rule.condition(lastADX)) {
                    adxExplanation = rule.explanation(lastADX);
                    break;
                }
            }
            
            document.getElementById("adx-summary").textContent = adxExplanation;

            const adxBadge = document.getElementById('adx-badge');
            if (adxSignal === "Strong Trend") {
                adxBadge.textContent = "Strong Trend";
                adxBadge.className = "signal-badge signal-buy";
                signalADX = {
                    label: lastRSI > 50 ? "bullish" : "bearish",
                    value: lastRSI > 50 ? 1 : -1
                };
            } else if (adxSignal === "Weak Trend") {
                adxBadge.textContent = "Weak Trend";
                adxBadge.className = "signal-badge signal-sell";
                signalADX = { label: "neutral", value: 0 };
            } else {
                adxBadge.textContent = "Hold";
                adxBadge.className = "signal-badge signal-hold";
                signalADX = { label: "neutral", value: 0 };
            }

            const adxLabels = stockData.map(data => data.date);  
            const adxValues = indicatorData.map(data => data.adx); 

            const adxCtx = document.getElementById('adxChart').getContext('2d');
            const adxChart = new Chart(adxCtx, {
                type: 'line',
                data: {
                    labels: adxLabels,
                    datasets: [
                        {
                            label: 'ADX',
                            data: adxValues,
                            borderColor: '#f39c12',
                            backgroundColor: 'rgba(243, 156, 18, 0.1)',
                            tension: 0.3,
                            fill: true,
                            pointRadius: 2,
                        },
                        {
                            label: 'Threshold (25)',
                            data: new Array(adxLabels.length).fill(25),
                            borderColor: 'rgba(231, 76, 60, 0.5)',
                            borderDash: [5, 5],
                            pointRadius: 0,
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        },
                        y: {
                            min: 0,
                            max: 100,
                            title: {
                                display: true,
                                text: 'ADX Value'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    }
                }
            });

            // Momentum
            const lastMomentum = lastIndicator.momentum;
            const momentumSignal = latestSignals.Momentum;

            const momentumConfig = indicatorConfigure['momentum'];
            
            document.getElementById('indicator-description-momentum').textContent = momentumConfig.description;
            
            document.getElementById('indicator-value-momentum').textContent = lastMomentum.toFixed(1);
            
            let momentumExplanation = "";
            for (let rule of momentumConfig.signalRules) {
                if (rule.condition.length === 1 && typeof rule.condition(momentumSignal) === 'boolean') {
                    if (rule.condition(momentumSignal)) {
                        momentumExplanation = rule.explanation(lastMomentum);
                        break;
                    }
                } else if (rule.condition(lastMomentum)) {
                    momentumExplanation = rule.explanation(lastMomentum);
                    break;
                }
            }
            
            document.getElementById("momentum-summary").textContent = momentumExplanation;

            const momentumBadge = document.getElementById('momentum-badge');
            if (momentumSignal === "Buy") {
                momentumBadge.textContent = "Bullish";
                momentumBadge.className = "signal-badge signal-buy";
                signalMOMENTUM = { label: "bullish", value: 1 };
            } else if (momentumSignal === "Sell") {
                momentumBadge.textContent = "Bearish";
                momentumBadge.className = "signal-badge signal-sell";
                signalMOMENTUM = { label: "bearish", value: -1 };
            } else {
                momentumBadge.textContent = "Neutral";
                momentumBadge.className = "signal-badge signal-hold";
                signalMOMENTUM = { label: "neutral", value: 0 };
            }

            const momentumLabels = stockData.map(data => data.date); 
            const momentumData = indicatorData.map(data => data.momentum);   

            const momentumCtx = document.getElementById('momentumChart').getContext('2d');
        
            const momentumChart = new Chart(momentumCtx, {
                type: 'line',
                data: {
                    labels: momentumLabels,
                    datasets: [{
                        label: 'Momentum',
                        data: momentumData,
                        borderColor: '#8E44AD',
                        backgroundColor: 'rgba(142, 68, 173, 0.1)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 3,
                        pointBackgroundColor: '#8E44AD',
                        pointHoverRadius: 5,
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Momentum Indicator Over Time',
                            font: {
                                size: 18
                            }
                        },
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: 'Momentum Value'
                            },
                            grid: {
                                drawBorder: false
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            },
                            ticks: {
                                maxRotation: 45,
                                minRotation: 0
                            }
                        }
                    }
                }
            });

            let signals = {
                rsi: { ...signalRSI, weight: 20 },
                sma: { ...signalSMA, weight: 20 },
                obv: { ...signalOBV, weight: 20 },
                adx: { ...signalADX, weight: 20 },
                momentum: { ...signalMOMENTUM, weight: 20 }
            };

            const indicators = ['rsi', 'sma', 'obv', 'adx', 'momentum'];

            indicators.forEach(indicator => {
            const badgeElement = document.getElementById(`${indicator}-signal`);
            
            if (badgeElement && signals[indicator]) {
                const signal = signals[indicator];
                let arrowSymbol = '';
                
                if (signal.label === 'bullish') {
                arrowSymbol = '↑';
                } else if (signal.label === 'bearish') {
                arrowSymbol = '↓';
                } else {
                arrowSymbol = '→'; 
                }
                
                badgeElement.textContent = `${arrowSymbol} ${signal.label}`;
                badgeElement.className = `indicator-badge ${signal.label}`;
            }
            });
            
            function updateSummarySignal() {
                const result = calculateFinalSignal(signals);
            
                const signalIcon = document.querySelector(".signal-icon");
                const signalTitle = document.querySelector(".signal-title");
                const signalDescription = document.querySelector(".signal-description");
            
                // Update icon and color based on signal
                if (result.label === "bullish") {
                    signalIcon.textContent = "↑";
                    signalIcon.style.color = "green";
                    signalTitle.style.color = "green";
                } else if (result.label === "bearish") {
                    signalIcon.textContent = "↓";
                    signalIcon.style.color = "red";
                    signalTitle.style.color = "red";
                } else {
                    signalIcon.textContent = "—";
                    signalIcon.style.color = "gray";
                    signalTitle.style.color = "gray";
                }
            
                // Update text content
                signalTitle.textContent = result.title;
                signalDescription.textContent = result.description;
            }
            
            
            function calculateFinalSignal(signals) {
                let totalWeight = 0;
                let bullishWeight = 0;
                let bearishWeight = 0;
                let neutralWeight = 0;
            
                for (let key in signals) {
                    const signal = signals[key];
                    const weight = signal.weight || 0;
                    totalWeight += weight;
            
                    if (signal.label === "bullish") bullishWeight += weight;
                    else if (signal.label === "bearish") bearishWeight += weight;
                    else neutralWeight += weight;
                }
            
                if (totalWeight === 0) {
                    return { label: "neutral", title: "NEUTRAL SIGNAL", description: "No valid data to determine sentiment." };
                }
            
                const bullishPct = bullishWeight / totalWeight;
                const bearishPct = bearishWeight / totalWeight;
            
                if (bullishPct > 0.6) {
                    return { label: "bullish", title: "BULLISH SIGNAL", description: "Market sentiment is leaning bullish." };
                } else if (bearishPct > 0.6) {
                    return { label: "bearish", title: "BEARISH SIGNAL", description: "Market sentiment is leaning bearish." };
                } else {
                    return { label: "neutral", title: "NEUTRAL SIGNAL", description: "The overall market sentiment is undecided." };
                }
            }
            
            
            document.querySelectorAll(".slider").forEach(slider => {
                slider.addEventListener("input", function () {
                    const card = this.closest(".indicator-card");
                    const indicatorName = card.dataset.indicator;
                    const newWeight = parseInt(this.value);
            
                    console.log("Slider moved:", indicatorName, "New weight:", newWeight);
            
                    const weightDisplay = card.querySelector(".indicator-weight span:last-child");
                    weightDisplay.textContent = `${newWeight}%`;
            
                    if (signals[indicatorName]) {
                        signals[indicatorName].weight = newWeight;
                    } else {
                        console.warn("Indicator not found in signals:", indicatorName); 
                    }
            
                    updateSummarySignal();
                });
            });

            updateSummarySignal();
            
            
        })
        .catch(error => console.error("Failed to load company data:", error));
});
