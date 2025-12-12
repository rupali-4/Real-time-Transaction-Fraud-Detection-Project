"""
FastAPI model deployment API.
Endpoints:
- POST /predict   : score a single transaction JSON (calls FE + model)
- GET /recent     : fetch last N records
- GET /health     : basic healthcheck
"""

from fastapi import FastAPI
from pydantic import BaseModel
import joblib, os, numpy as np, json
from datetime import datetime
import uuid

from src.services.feature_engineering import transform_single
from src.services.persistence import init_db, persist_result, alert_user, fetch_recent

app = FastAPI(title="Aegis Model API")

# -------------------------------------------------------
# FIXED MODEL DIRECTORY (ALWAYS POINTS TO /aegis_realtime_fraud/models)
# -------------------------------------------------------
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_DIR = os.path.join(project_root, "models")

# global model refs
scaler = None
isof = None
ae_model = None


# -------------------------------------------------------
# FIXED INPUT MODEL (No more 422 errors)
#--------------------------------------------------------
class Txn(BaseModel):
    transaction_id: str | None = None
    timestamp: str | None = None

    class Config:
        extra = "allow"      # allow extra CSV fields


# -------------------------------------------------------
# LOAD MODELS AT STARTUP
# -------------------------------------------------------
@app.on_event("startup")
def load_models():
    global scaler, isof, ae_model

    init_db()

    # correct file names
    scaler_path = os.path.join(MODEL_DIR, "scaler.joblib")
    iso_path = os.path.join(MODEL_DIR, "isolation_forest.joblib")
    ae_path = os.path.join(MODEL_DIR, "autoencoder.keras")

    # load scaler
    if not os.path.exists(scaler_path):
        raise RuntimeError(f"Scaler not found at {scaler_path}. Run training first.")

    scaler = joblib.load(scaler_path)

    # load isolation forest
    if os.path.exists(iso_path):
        isof = joblib.load(iso_path)
    else:
        isof = None

    # load autoencoder
    try:
        from tensorflow.keras.models import load_model
        if os.path.exists(ae_path):
            ae_model = load_model(ae_path)
        else:
            ae_model = None
    except Exception:
        ae_model = None


# -------------------------------------------------------
# SCORING FUNCTION
# -------------------------------------------------------
def score_features(X_scaled: np.ndarray):
    """Return combined fraud score (0..1). Higher = more likely fraud."""
    scores = []

    if isof is not None:
        iso_pred = isof.predict(X_scaled)  # -1 = fraud
        iso_score = (iso_pred == -1).astype(float)
        scores.append(iso_score)

    if ae_model is not None:
        recon = ae_model.predict(X_scaled)
        mse = ((X_scaled - recon) ** 2).mean(axis=1)
        ae_score = (mse - mse.min()) / (mse.max() - mse.min() + 1e-9)
        scores.append(ae_score)

    if not scores:
        return float(0.0)

    avg = sum(scores) / len(scores)
    return float(avg[0])


# -------------------------------------------------------
# PREDICT ENDPOINT (used by producer)
# -------------------------------------------------------
@app.post("/predict")
def predict(txn: Txn):

    d = txn.dict()

    # auto-generate missing fields (fixes 422)
    txid = d.get("transaction_id") or str(uuid.uuid4())
    ts = d.get("timestamp") or datetime.utcnow().isoformat()

    # feature engineering
    X = transform_single(d)
    Xs = scaler.transform(X)

    # score
    score = score_features(Xs)

    # decision
    action = "block" if score >= 0.7 else "allow"
    reason = f"score={score:.3f}"

    # save in DB
    persist_result(txid, ts, score, action, d)

    # send SMS alert when blocked
    if action == "block":
        alert_user(txid, reason)

    return {
        "transaction_id": txid,
        "timestamp": ts,
        "score": score,
        "action": action,
        "reason": reason
    }


# -------------------------------------------------------
# FETCH RECENT SCORED TRANSACTIONS
# -------------------------------------------------------
@app.get("/recent")
def recent(n: int = 50):
    rows = fetch_recent(n)
    out = []
    for r in rows:
        out.append({
            "transaction_id": r[0],
            "timestamp": r[1],
            "score": r[2],
            "action": r[3],
            "raw": json.loads(r[4])
        })
    return out


# -------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
