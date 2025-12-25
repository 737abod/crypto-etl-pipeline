import sqlite3
import requests
import pandas as pd
import streamlit as st
import time  # This is built-in, you DO NOT need to install it.

# --- CONFIGURATION ---
DB_NAME = "crypto_history.db"
COINS = ["bitcoin", "ethereum", "solana", "dogecoin"]

# --- 1. BACKEND: DATABASE MANAGER (SQL) ---
def init_db():
    """Creates the SQL database if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # FIX: Ensure table exists before we try to read it
    c.execute('''CREATE TABLE IF NOT EXISTS prices
                 (timestamp TEXT, symbol TEXT, price REAL)''')
    conn.commit()
    conn.close()

# --- CALL INIT_DB HERE TO FIX YOUR ERROR ---
init_db()  # <--- THIS IS THE MISSING LINE

def save_price(symbol, price):
    """Inserts a new data point into SQL."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO prices VALUES (datetime('now', 'localtime'), ?, ?)", 
              (symbol, price))
    conn.commit()
    conn.close()

def load_history(symbol):
    """Reads historical data from SQL using Pandas."""
    conn = sqlite3.connect(DB_NAME)
    # Check if table exists first to avoid crash
    try:
        df = pd.read_sql_query(f"SELECT * FROM prices WHERE symbol='{symbol}'", conn)
    except pd.errors.DatabaseError:
        # If table doesn't exist, return empty dataframe
        df = pd.DataFrame(columns=['timestamp', 'symbol', 'price'])
    conn.close()
    return df

# --- 2. BACKEND: ETL PIPELINE ---
def fetch_live_data():
    """Extracts data from API."""
    try:
        ids = ",".join(COINS)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
        data = requests.get(url).json()
        
        # Transform & Load
        for symbol in COINS:
            if symbol in data:
                price = data[symbol]['usd']
                save_price(symbol, price)
        return True
    except Exception as e:
        return False

# --- 3. FRONTEND: DASHBOARD (Streamlit) ---
st.set_page_config(page_title="CryptoPulse Dashboard", layout="wide")
st.title("⚡ CryptoPulse: Real-Time ETL Pipeline")

# Sidebar controls
st.sidebar.header("Pipeline Controls")
if st.sidebar.button("🔄 Trigger ETL Job (Fetch Data)"):
    with st.spinner("Running ETL process..."):
        success = fetch_live_data()
        if success:
            st.sidebar.success("Data successfully ingested to SQL.")
            time.sleep(1) # Visual pause
            st.rerun()    # Refresh page to show new data
        else:
            st.sidebar.error("API Error.")

# Main Display
col1, col2 = st.columns(2)

# Metric Cards
# Safe loading: If empty, show 0
df_btc = load_history("bitcoin")
if not df_btc.empty:
    current_price = df_btc.tail(1)['price'].values[0]
    col1.metric("Bitcoin (Live)", f"${current_price:,.2f}")
else:
    col1.metric("Bitcoin", "No Data (Click Trigger ETL)")

# Interactive Charts
st.subheader("Historical Price Trends")
selected_coin = st.selectbox("Select Asset to Analyze", COINS)

df = load_history(selected_coin)
if not df.empty:
    # Convert text timestamp to datetime objects for graphing
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    st.line_chart(df.set_index('timestamp')['price'])
    
    st.write("Recent Data Points:")
    st.dataframe(df.sort_values(by='timestamp', ascending=False).head(5))
else:
    st.info("No historical data found. Click 'Trigger ETL Job' in the sidebar.")
    