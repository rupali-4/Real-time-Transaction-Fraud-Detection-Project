"""
Simple Streamlit dashboard to show recent flagged transactions.
Run: streamlit run src/dashboard.py
"""
import streamlit as st, requests, pandas as pd, time
API = st.sidebar.text_input("API Base URL", "http://localhost:8000")

st.title("Aegis — Real-time Fraud Dashboard (Mock)")

if st.button("Refresh now"):
    pass

def fetch():
    try:
        r = requests.get(API + "/recent?n=200", timeout=10)
        return r.json()
    except Exception as e:
        st.error("Error fetching: " + str(e))
        return []

data = fetch()
if data:
    df = pd.DataFrame(data)
    st.dataframe(df[["transaction_id","timestamp","score","action"]])
    st.subheader("Blocked Transactions")
    blocked = df[df["action"]=="block"]
    st.dataframe(blocked[["transaction_id","timestamp","score"]])
else:
    st.info("No data yet. Start producer to stream transactions.")