function fetchCompanyData(companyName) {
  const stockPriceData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
      label: 'Stock Price',
      data: [120, 125, 130, 135, 140],
      borderColor: 'rgb(75, 192, 192)',
      fill: false,
    }]
  };

  const indicatorData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
      label: 'RSI Indicator',
      data: [50, 60, 45, 55, 70],
      borderColor: 'rgb(255, 159, 64)',
      fill: false,
    }]
  };

  const indicators = [
    { name: 'RSI', signal: 'Buy', strength: 8 },
    { name: 'MACD', signal: 'Neutral', strength: 5 },
    { name: 'Bollinger Bands', signal: 'Sell', strength: 3 }
  ];

  // Display stock price chart
  createPriceChart(stockPriceData);

  // Display indicator chart
  createIndicatorChart(indicatorData);

  // Display signals
  displaySignals(indicators);
}

// Create Stock Price Chart
function createPriceChart(data) {
  const ctx = document.getElementById('priceChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: data,
    options: {
      scales: {
        x: {
          title: {
            display: true,
            text: 'Month'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Price (USD)'
          }
        }
      }
    }
  });
}

// Create Indicator Chart
function createIndicatorChart(data) {
  const ctx = document.getElementById('indicatorChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: data,
    options: {
      scales: {
        x: {
          title: {
            display: true,
            text: 'Month'
          }
        },
        y: {
          title: {
            display: true,
            text: 'RSI Value'
          }
        }
      }
    }
  });
}

// Display Buy/Sell Signals
function displaySignals(indicators) {
  const signalsList = document.getElementById('signals-list');
  signalsList.innerHTML = '';

  indicators.forEach(indicator => {
    const listItem = document.createElement('li');
    listItem.textContent = `${indicator.name} - Signal: ${indicator.signal} (Strength: ${indicator.strength})`;

    if (indicator.signal === 'Buy') {
      listItem.classList.add('buy');
    } else if (indicator.signal === 'Sell') {
      listItem.classList.add('sell');
    } else {
      listItem.classList.add('neutral');
    }

    signalsList.appendChild(listItem);
  });
}

// Handle Search Button Click
document.getElementById('search-btn').addEventListener('click', () => {
  const companyName = document.getElementById('company-search').value;
  if (companyName) {
    fetchCompanyData(companyName);
  }
});
