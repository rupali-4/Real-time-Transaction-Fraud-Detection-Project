"""
Mock producer that reads CSV rows and POSTs transactions to the model API (/predict).
This simulates a streaming ingestion service. Use --rate to control records per second.
"""

import argparse
import time
import requests
import csv
import os
from urllib.parse import urljoin

def stream_csv(datafile, url, rate=1.0):
    # Check whether CSV exists
    if not os.path.exists(datafile):
        print(f"❌ Error: CSV file not found -> {datafile}")
        return

    print(f"📡 Streaming data from: {datafile}")
    print(f"➡️  Posting to API: {url}")
    print(f"⏱  Rate: {rate} record(s) per second\n")

    with open(datafile, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                response = requests.post(url, json=row, timeout=5)

                try:
                    resp_json = response.json()
                except:
                    resp_json = "Invalid JSON response"

                print(f"POST {row.get('transaction_id', '-')} → {response.status_code} → {resp_json}")

            except requests.exceptions.ConnectionError:
                print("❌ ERROR: Cannot connect to API. Make sure FastAPI is running.")
                break
            except Exception as e:
                print(f"❌ ERROR posting row: {e}")

            # Control rate
            time.sleep(1.0 / max(rate, 0.001))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mock Streaming Transaction Producer")

    parser.add_argument("--data", required=True, help="Path to CSV transaction file")
    parser.add_argument("--url", default="http://localhost:8000/predict", help="Prediction API endpoint")
    parser.add_argument("--rate", type=float, default=1.0, help="Records per second")

    args = parser.parse_args()

    stream_csv(args.data, args.url, args.rate)
