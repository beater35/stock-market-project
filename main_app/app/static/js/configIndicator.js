const indicatorConfig = {
'rsi': {
    description: 'RSI measures the speed and change of price movements. Values below 30 indicate oversold conditions (buy signal), while values above 70 indicate overbought conditions (sell signal).',
    chartColor: '#4285F4',
    chartBgColor: 'rgba(66, 133, 244, 0.1)',
    signalRules: [
        {
            condition: (signalValue) => signalValue === 'Buy',
            signal: 'Sell',
            borderColor: '#81C784',
            explanation: value => `The RSI is trending upward and currently at ${value.toFixed(2)}, suggesting the asset may be overbought.`
        },
        {
            condition: (signalValue) => signalValue === 'Sell',
            signal: 'Buy',
            borderColor: '#EF5350',
            explanation: value => `The RSI is trending downward and currently at ${value.toFixed(2)}, suggesting the asset may be oversold.`
        },
        {
            condition: value => true, // default case
            signal: 'Hold',
            borderColor: '#FFEB3B',
            explanation: value => `The RSI is at ${value.toFixed(2)}, within the neutral range.`
        }
    ]
},
'obv': {
    description: 'OBV measures buying and selling pressure. Increasing OBV indicates positive volume pressure, which can lead to higher prices.',
    chartColor: '#4285F4',
    chartBgColor: 'rgba(66, 133, 244, 0.1)',
    signalRules: [
        {
            condition: (signalValue) => signalValue === 'Buy',
            signal: 'Buy',
            borderColor: '#81C784',
            explanation: value => `The current OBV value is ${value.toFixed(2)}, suggesting an uptrend and potential buy signal.`
        },
        {
            condition: (signalValue) => signalValue === 'Sell',
            signal: 'Sell',
            borderColor: '#EF5350',
            explanation: value => `The current OBV value is ${value.toFixed(2)}, suggesting a downtrend and potential sell signal.`
        },
        {
            condition: () => true, // default case
            signal: 'Neutral',
            borderColor: '#FFEB3B',
            explanation: () => 'The OBV is stable, indicating no clear trend.'
        }
    ]
},
'sma': {
    description: 'SMA (Simple Moving Average) smooths out price data by creating a constantly updated average price. It is used to identify the direction of the trend.',
    chartColor: '#FF5733',
    chartBgColor: 'rgba(255, 87, 51, 0.1)',
    signalRules: [
        {
            condition: (signalValue) => signalValue === 'Buy',
            signal: 'Buy',
            borderColor: '#81C784',
            explanation: value => `The current SMA value is ${value.toFixed(2)}, suggesting an uptrend and potential buy signal.`
        },
        {
            condition: (signalValue) => signalValue === 'Sell',
            signal: 'Sell',
            borderColor: '#EF5350',
            explanation: value => `The current SMA value is ${value.toFixed(2)}, suggesting a downtrend and potential sell signal.`
        },
        {
            condition: () => true, // default case
            signal: 'Neutral',
            borderColor: '#FFEB3B',
            explanation: () => 'The SMA is stable, indicating no clear trend.'
        }
    ]
},
'adx': {
    description: 'ADX (Average Directional Index) measures trend strength. Values above 25 indicate a strong trend, while values below 20 indicate a weak trend.',
    chartColor: '#FFC300',
    chartBgColor: 'rgba(255, 195, 0, 0.1)',
    signalRules: [
        {
            signal: 'Strong Trend',
            borderColor: '#81C784',
            condition: (signalValue) => signalValue === 'Strong Trend',  
            explanation: value => `The ADX value is ${value.toFixed(2)}, indicating a strong trend in the market. This is a good opportunity to buy.`
        },
        {
            signal: 'Weak Trend',
            borderColor: '#EF5350',
            condition: (signalValue) => signalValue === 'Weak Trend', 
            explanation: value => `The ADX value is ${value.toFixed(2)}, indicating a weak or no trend in the market. This is a good opportunity to sell.`
        },
        {
            signal: 'Neutral',
            borderColor: '#FFEB3B',
            condition: (signalValue) => signalValue === 'neutral',  
            explanation: () => 'The ADX value is neutral, indicating uncertainty in the market trend. It is advisable to hold for now.'
        }
    ]
},
'momentum': {
    description: 'Momentum measures the rate of price change. A rising momentum suggests a strengthening trend, while falling momentum suggests a weakening trend.',
    chartColor: '#8E44AD',
    chartBgColor: 'rgba(142, 68, 173, 0.1)',
    signalRules: [
        {
            condition: (signalValue) => signalValue === 'Buy',
            signal: 'Buy',
            borderColor: '#81C784',
            explanation: value => `The momentum value is ${value.toFixed(2)}, suggesting positive price movement and potential buy signal.`
        },
        {
            condition: (signalValue) => signalValue === 'Sell',
            signal: 'Sell',
            borderColor: '#EF5350',
            explanation: value => `The momentum value is ${value.toFixed(2)}, suggesting negative price movement and potential sell signal.`
        },
        {
            condition: () => true, 
            signal: 'Neutral',
            borderColor: '#FFEB3B',
            explanation: () => 'The momentum is neutral, indicating little to no price movement.'
        }
    ]
},
'macd': {
description: 'MACD shows the relationship between two moving averages of a security\'s price. A bullish signal occurs when MACD crosses above its signal line.',
chartColor: '#4285F4',
chartBgColor: 'rgba(66, 133, 244, 0.1)',
signalRules: [
    {
    condition: (latest, values) => {
        // Simple check if trending up
        const recentValues = values.slice(-5);
        return recentValues[recentValues.length - 1] > recentValues[0];
    },
    signal: 'Buy',
    explanation: () => 'The MACD is trending upward, potentially indicating bullish momentum.'
    },
    {
    condition: () => true, // default case
    signal: 'Sell',
    explanation: () => 'The MACD is trending downward, potentially indicating bearish momentum.'
    }
]
}
};

// Default config for any indicator not specifically defined
const defaultIndicatorConfig = {
description: 'This is a technical indicator used to analyze market trends.',
chartColor: '#4285F4',
chartBgColor: 'rgba(66, 133, 244, 0.1)',
signalRules: [
{
    condition: () => true,
    signal: 'Neutral',
    explanation: (value, indicator) => `Latest ${indicator.toUpperCase()} value: ${value.toFixed(2)}.`
}
]
};

