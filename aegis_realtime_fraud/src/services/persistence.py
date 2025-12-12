"""
Persistence helpers: simple SQLite persistence and alerting placeholder.
"""
import sqlite3, os, json
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "aegis_results.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT,
        timestamp TEXT,
        score REAL,
        action TEXT,
        raw JSON
    )""")
    conn.commit()
    conn.close()

def persist_result(transaction_id, timestamp, score, action, raw):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO results (transaction_id, timestamp, score, action, raw) VALUES (?, ?, ?, ?, ?)",
              (str(transaction_id), str(timestamp), float(score), action, json.dumps(raw)))
    conn.commit()
    conn.close()

def fetch_recent(n=100):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT transaction_id, timestamp, score, action, raw FROM results ORDER BY id DESC LIMIT ?", (n,))
    rows = c.fetchall()
    conn.close()
    return rows

def alert_user(transaction_id, reason):
    # Placeholder for real alerting (SMS/push/email). For demo we just print.
    print(f"[ALERT] Transaction {transaction_id}: {reason}")