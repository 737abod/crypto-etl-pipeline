# ⚡ CryptoPulse: Real-Time ETL Pipeline

A Full-Stack Data Engineering project that tracks cryptocurrency prices, stores them in a SQL database, and visualizes trends.

## 🏗 Architecture
* **ETL Engine:** Python & Pandas
* **Database:** SQLite (Persistent Storage)
* **API:** CoinGecko (Live Financial Data)
* **Frontend:** Streamlit (Interactive Dashboard)

## 🚀 How to Run
1.  Install dependencies:
    `pip install -r requirements.txt`
2.  Run the application:
    `streamlit run app.py`

## 📊 Features
* **Automated Extraction:** Fetches live data for Bitcoin, Ethereum, Solana, and Dogecoin.
* **Historical Tracking:** Saves every price check to a local database to build a history over time.
* **Data Visualization:** Interactive charts to analyze price volatility.