# 📈 Stock Market Technical Indicator Analysis System

A real-time, web-based platform that helps traders and investors make data-driven decisions using a combination of widely used technical indicators. This system automates the fetching of stock data, calculates multiple indicators, and generates buy/sell/hold signals based on standard thresholds and custom user-defined strategies.

---

## 🚀 Features

- Fetches real-time or daily stock data and stores it in PostgreSQL
- Calculates key technical indicators:
  - RSI (Relative Strength Index)
  - SMA (Simple Moving Average)
  - ADX (Average Directional Index)
  - OBV (On-Balance Volume)
  - Momentum
- Generates Bullish/Bearish/Neutral signals based on industry-standard rules
- Users can combine indicators with custom weightages to form personalized strategies
- Dynamic and responsive web interface with:
  - Table showing bullish/bearish indicator values
  - Company-specific technical insights
  - Interactive chart view with price and indicator overlays
- Automatically deletes older data (older than 10–30 days) to save space
- Scheduled backend processes for scraping and indicator calculation

---

## 🌐 Live Demo 

> _Note: This project was developed as a final year academic submission and is currently not deployed online._

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript (Fetch API)
- **Database:** PostgreSQL
- **Scheduling:** Cron / APScheduler (for automated scraping and calculations)
- **Data Source:** Custom scraper for daily stock data (due to lack of local APIs)
- **Libraries Used:**
  - `pandas`, `numpy`, `sqlalchemy`
  - Technical analysis functions (custom implementations or TA-Lib if supported)

---

## 🧠 Key Concepts

- **Multi-indicator analysis**: Combine several indicators to reduce noise and improve signal clarity.
- **Swing trading strategy**: Signals designed to assist in short- to medium-term trading decisions.
- **Real-time data pipeline**: Backend fetches and analyzes stock data on schedule, making insights readily available.
- **Custom signal generation**: Combine indicator outputs with weightages to define your own strategies.

---

## 📷 UI Overview

- `Landing Page`: Project introduction and navigation
- `Core Page`: Table view showing multiple companies and their bullish/bearish signals
- `Company Page`: Detailed view of indicator values and explanation
- `Chart Popup`: Interactive charts showing price and technical indicators over time

---

<pre lang="no-highlight"><code>```text ## 📁 Folder Structure . ├── database │   ├── db_setup.py │   ├── finddups.py │   ├── insert_and_replace_merged_csv.py │   ├── insert_company.py │   ├── insert_data(all).py │   ├── insert_each_csv.py │   ├── insert_merged_data.py │   ├── merge_csv.py │   ├── stock_price_data_export.csv │   ├── tocsv.py │   └── venv │   ├── bin │   ├── include │   ├── lib │   ├── lib64 -> lib │   ├── pyvenv.cfg │   └── share ├── main_app │   ├── app │   │   ├── calculate_indicators.py │   │   ├── calculations.py │   │   ├── email_service.py │   │   ├── __init__.py │   │   ├── live_market │   │   ├── models.py │   │   ├── old_models.py │   │   ├── old_routes.py │   │   ├── __pycache__ │   │   ├── routes.py │   │   ├── scraper.py │   │   ├── static │   │   └── templates │   ├── checkkk.py │   ├── config.py │   ├── instance │   ├── main.py │   ├── migrations │   │   ├── alembic.ini │   │   ├── env.py │   │   ├── __pycache__ │   │   ├── README │   │   ├── script.py.mako │   │   └── versions │   ├── __pycache__ │   │   └── config.cpython-38.pyc │   ├── requirements.txt │   └── venv │   ├── bin │   ├── include │   ├── lib │   ├── lib64 -> lib │   ├── pyvenv.cfg │   └── share └── scraping ├── README.md ├── stockscraper │   ├── scrapy.cfg │   └── stockscraper └── venv ├── bin ├── include ├── lib ├── lib64 -> lib ├── pyvenv.cfg └── share ```</code></pre>

## 📚 References

- TA-Lib & Python TA Libraries
- Academic research papers on trading strategies

---
