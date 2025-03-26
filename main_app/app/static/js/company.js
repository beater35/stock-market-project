document.addEventListener('DOMContentLoaded', function() {
    // Extract symbol from the URL
    const pathParts = window.location.pathname.split('/');
    const symbol = pathParts[pathParts.length - 1];

    // Fetch company data
    fetch(`/api/company/${symbol}/data`)
        .then(response => response.json())
        .then(data => {
            // Update Stock Header
            updateStockHeader(symbol, data);

            // Create Price Chart
            createPriceChart(data.stock_data);

            // Update Technical Indicators
            updateTechnicalIndicators(data.indicator_data);

            // Update Signal Summary
            updateSignalSummary(data.indicator_data);
        })
        .catch(error => console.error('Error fetching company data:', error));

    function updateStockHeader(symbol, data) {
        // Update stock symbol
        document.querySelector('.stock-title').textContent = symbol;

        // Update last updated date (using the most recent date in stock data)
        if (data.stock_data.length > 0) {
            const lastUpdatedDate = data.stock_data[data.stock_data.length - 1].date;
            document.querySelector('.last-updated').innerHTML = `
                <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Last updated: ${lastUpdatedDate}
            `;
        }
    }

    function createPriceChart(stockData) {
        const ctx = document.createElement('canvas');
        document.querySelector('.price-chart').innerHTML = ''; // Clear placeholder SVG
        document.querySelector('.price-chart').appendChild(ctx);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: stockData.map(item => item.date),
                datasets: [{
                    label: 'Closing Price',
                    data: stockData.map(item => item.close),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }

    function updateTechnicalIndicators(indicatorData) {
        // Use the most recent indicator data
        if (indicatorData.length === 0) return;
        
        const latestIndicators = indicatorData[indicatorData.length - 1];
        const signals = latestIndicators.signals;

        // Update RSI Indicator
        updateIndicator('RSI', signals.RSI, 
            `The RSI is currently ${signals.RSI}. ${signals.RSI === 'Buy' ? 'This is traditionally seen as a buying opportunity.' : ''}`);

        // Update ADX Indicator
        updateIndicator('ADX', signals.ADX, 
            `The ADX indicates a ${signals.ADX} in the market.`);

        // Update Momentum Indicator
        updateIndicator('Momentum', signals.Momentum, 
            `The Momentum indicator suggests a ${signals.Momentum} signal.`);
    }

    function updateIndicator(name, signal, description) {
        const indicatorElement = Array.from(document.querySelectorAll('.indicator'))
            .find(el => el.querySelector('.indicator-title').textContent.includes(name));

        if (indicatorElement) {
            // Update signal
            const signalElement = indicatorElement.querySelector('.indicator-signal');
            signalElement.textContent = signal;
            signalElement.classList.remove('buy-signal', 'sell-signal', 'trend-signal');
            signalElement.classList.add(
                signal.toLowerCase().includes('buy') ? 'buy-signal' :
                signal.toLowerCase().includes('sell') ? 'sell-signal' : 
                'trend-signal'
            );

            // Update description
            const descriptionElement = indicatorElement.querySelector('.indicator-description');
            if (descriptionElement) {
                descriptionElement.textContent = description;
            }
        }
    }

    function updateSignalSummary(indicatorData) {
        if (indicatorData.length === 0) return;

        const latestIndicators = indicatorData[indicatorData.length - 1];
        const signals = latestIndicators.signals;

        // Count signals
        const signalCounts = {
            buy: 0,
            sell: 0,
            other: 0
        };

        Object.values(signals).forEach(signal => {
            if (signal.toLowerCase().includes('buy')) signalCounts.buy++;
            else if (signal.toLowerCase().includes('sell')) signalCounts.sell++;
            else signalCounts.other++;
        });

        // Update signal counts
        document.querySelector('.signal-list .signal-item:nth-child(1) .signal-count').textContent = signalCounts.buy;
        document.querySelector('.signal-list .signal-item:nth-child(2) .signal-count').textContent = signalCounts.sell;
        document.querySelector('.signal-list .signal-item:nth-child(3) .signal-count').textContent = signalCounts.other;

        // Determine overall sentiment
        const sentimentElement = document.querySelector('.sentiment .bullish-pill');
        if (signalCounts.buy > signalCounts.sell) {
            sentimentElement.textContent = 'Bullish';
            sentimentElement.classList.remove('bearish-pill');
            sentimentElement.classList.add('bullish-pill');
        } else if (signalCounts.buy < signalCounts.sell) {
            sentimentElement.textContent = 'Bearish';
            sentimentElement.classList.remove('bullish-pill');
            sentimentElement.classList.add('bearish-pill');
        } else {
            sentimentElement.textContent = 'Neutral';
            sentimentElement.classList.remove('bullish-pill', 'bearish-pill');
        }
    }
});