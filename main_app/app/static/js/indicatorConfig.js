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
            condition: value => true, 
            signal: 'Hold',
            borderColor: '#FFEB3B',
            explanation: value => `The RSI is at ${value.toFixed(2)}, within the neutral range.`
        }
    ]
},
'obv': {
    description: 'OBV (On-Balance Volume) compares volume flow with price movement. A "Buy" signal occurs when both OBV and price rise, indicating strong upward pressure. A "Sell" occurs when both decline, signaling downward momentum. Otherwise, the trend is unclear.',
    chartColor: '#4285F4',
    chartBgColor: 'rgba(66, 133, 244, 0.1)',
    signalRules: [
        {
            condition: (signalValue) => signalValue === 'Buy',
            signal: 'Buy',
            borderColor: '#81C784',
            explanation: value => `OBV and price are both rising. OBV value: ${value.toFixed(2)}. Indicates buying pressure and potential uptrend.`
        },
        {
            condition: (signalValue) => signalValue === 'Sell',
            signal: 'Sell',
            borderColor: '#EF5350',
            explanation: value => `OBV and price are both falling. OBV value: ${value.toFixed(2)}. Suggests selling pressure and potential downtrend.`
        },
        {
            condition: () => true, 
            signal: 'Neutral',
            borderColor: '#FFEB3B',
            explanation: () => 'OBV and price are diverging. Trend direction is unclear — signal is Hold.'
        }
    ]
},
'sma': {
    description: 'The 20-day SMA acts as a trend-following indicator. When the current price is above the SMA, it may indicate upward momentum; when below, it may signal downward movement.',
    chartColor: '#FF5733',
    chartBgColor: 'rgba(255, 87, 51, 0.1)',
    signalRules: [
        {
            condition: (signalValue) => signalValue === 'Buy',
            signal: 'Buy',
            borderColor: '#81C784',
            explanation: value => `The price is currently above the 20-day SMA of ${value.toFixed(2)}, indicating upward momentum and a potential buy signal.`
        },
        {
            condition: (signalValue) => signalValue === 'Sell',
            signal: 'Sell',
            borderColor: '#EF5350',
            explanation: value => `The price is currently below the 20-day SMA of ${value.toFixed(2)}, suggesting downward pressure and a possible sell signal.`
        },
        {
            condition: () => true, 
            signal: 'Neutral',
            borderColor: '#FFEB3B',
            explanation: () => 'The price and SMA are closely aligned, indicating no clear trend.'
        }
    ]
},
'adx': {
    description: 'ADX (Average Directional Index) measures the strength of a trend, regardless of direction. Values above 25 suggest a strong trend, while lower values suggest a weak or sideways market.',
    chartColor: '#FFC300',
    chartBgColor: 'rgba(255, 195, 0, 0.1)',
    signalRules: [
        {
            signal: 'Strong Trend',
            borderColor: '#81C784',
            condition: (signalValue) => signalValue === 'Strong Trend',  
            explanation: value => `The ADX value is ${value.toFixed(2)}, indicating a strong trend. This may support continuing with the current position.`
        },
        {
            signal: 'Weak Trend',
            borderColor: '#EF5350',
            condition: (signalValue) => signalValue === 'Weak Trend', 
            explanation: value => `The ADX value is ${value.toFixed(2)}, indicating a weak or range-bound market. Caution is advised before entering a trade.`
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
    description: 'Momentum compares current price to a previous price to gauge the speed and strength of movement. Positive values suggest upward pressure; negative values suggest downward pressure.',
    chartColor: '#8E44AD',
    chartBgColor: 'rgba(142, 68, 173, 0.1)',
    signalRules: [
        {
            condition: (signalValue) => signalValue === 'Buy',
            signal: 'Buy',
            borderColor: '#81C784',
            explanation: value => `The momentum value is ${value.toFixed(2)}, indicating upward price momentum and a potential buy signal.`
        },
        {
            condition: (signalValue) => signalValue === 'Sell',
            signal: 'Sell',
            borderColor: '#EF5350',
            explanation: value => `The momentum value is ${value.toFixed(2)}, suggesting negative price movement and a potential sell signal.`
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
        const recentValues = values.slice(-5);
        return recentValues[recentValues.length - 1] > recentValues[0];
    },
    signal: 'Buy',
    explanation: () => 'The MACD is trending upward, potentially indicating bullish momentum.'
    },
    {
    condition: () => true, 
    signal: 'Sell',
    explanation: () => 'The MACD is trending downward, potentially indicating bearish momentum.'
    }
]
}
};

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
    
    

export { indicatorConfig };