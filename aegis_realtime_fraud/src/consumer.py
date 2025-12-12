"""
Example consumer that periodically fetches /recent from API and prints/stores.
This simulates a downstream consumer that might alert operations or enrich other systems.
"""
import time, requests
API_BASE = "http://localhost:8000"

def poll_recent(interval=5):
    while True:
        try:
            r = requests.get(API_BASE + "/recent?n=20", timeout=10)
            rows = r.json()
            print(f"[Consumer] fetched {len(rows)} results — latest:")
            for r in rows[:5]:
                print(r["transaction_id"], r["score"], r["action"])
        except Exception as e:
            print("Consumer error:", e)
        time.sleep(interval)

if __name__ == "__main__":
    poll_recent()