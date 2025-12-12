# Aegis — Real-time Fraud Detection (Mock Streaming)

This repository implements a full **real-time** fraud detection prototype called **Aegis**:
- Stream ingestion (mock HTTP stream + optional Kafka instructions)
- Real-time feature engineering module
- Model training (IsolationForest baseline + Keras Autoencoder)
- FastAPI Model Deployment API
- Mock producer (streaming simulator)
- Consumer that calls the Model API and persists results (SQLite)
- Streamlit dashboard to visualize flagged transactions

> **Important**: You said you already pre-processed the dataset. Place your CSV at `data/transactions.csv` (see below).
> The project includes a `train.py` script that trains models from `data/transactions.csv` and writes `models/`.

---

## Folder layout (created by this package)
```
aegis_realtime_fraud/
├─ data/transactions.csv      # *Your* dataset (PLACE HERE)
├─ models/                    # models written by train script
├─ src/
│  ├─ model/
│  │  ├─ train.py
│  │  └─ autoencoder.py
│  ├─ api/
│  │  └─ main.py
│  ├─ services/
│  │  ├─ feature_engineering.py
│  │  └─ persistence.py
│  ├─ producer.py
│  ├─ consumer.py
│  └─ dashboard.py
├─ requirements.txt
├─ docker-compose-kafka.yml   # optional instructions (Kafka) — not required for mock mode
└─ README.md
```

## Quick start (mock streaming mode) — recommended for local testing
1. Create a virtualenv and install dependencies:
   ```bash
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Place your preprocessed CSV at `data/transactions.csv`. The script expects one transaction per row with numeric features.
   See `data/schema.md` for expected columns and minimal required columns.
3. Train models (this writes `models/isoforest.joblib` and `models/autoencoder/`):
   ```bash
   python src/model/train.py --data data/transactions.csv --out models
   ```
4. Start the FastAPI model server (it loads models from `models/`):
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```
5. In another terminal, start the mock producer to stream transactions (it POSTs to the API):
   ```bash
   python src/producer.py --data data/transactions.csv --rate 2
   ```
   `--rate` = records per second
6. Start the consumer (optionally; the simple producer already requests scoring and stores results locally):
   ```bash
   python src/consumer.py
   ```
7. Start the dashboard (Streamlit):
   ```bash
   streamlit run src/dashboard.py
   ```

## Production notes
- The mock pipeline demonstrates real-time behavior. For production switch `producer/consumer` to use Kafka by following `docker-compose-kafka.yml` and modifying `producer.py`/`consumer.py` to use Kafka producer/consumer (instructions inside).
- The API exposes `/predict` endpoint which accepts a single transaction JSON and returns a fraud score and action (block/allow).
- Alerts: The API returns `action` and `reason`. You can integrate Twilio/Push notifications in `services/persistence.py` `alert_user()`.

## Where to initialize dataset
Place your CSV file at `data/transactions.csv`. The training script expects the CSV including the features used for modeling. If your preprocessed dataset uses a different filename or columns, open `src/model/train.py` and update `FEATURE_COLUMNS` and `TARGET_COLUMN` as needed.

## No hallucination / transparency
- All code is included and deterministic. I did not invent dataset values — training uses whatever CSV you place in `data/transactions.csv`.
- If your dataset has categorical columns, either encode them beforehand (preferred) or extend `src/services/feature_engineering.py` to encode them appropriately.

---