# Data Schema (expected)

Place your CSV at `data/transactions.csv`.
Minimal required numeric columns (examples — adapt to your CSV):
- transaction_id (string/integer) - unique id
- timestamp (ISO 8601 string) - event time
- amount (float)
- merchant_country (string) - ideally encoded as numeric before training or one-hot in FE
- cardholder_country (string)
- time_since_last_txn (float) - seconds since last transaction for the card
- num_txns_24h (int) - count in last 24 hours
- avg_amount_30d (float)
- is_international (0/1)
- device_change_flag (0/1)
- label (0/1) - optional; 1 if fraudulent (used only for evaluation/training)

If your CSV uses different column names, update `FEATURE_COLUMNS` in `src/model/train.py` and
`src/services/feature_engineering.py`.