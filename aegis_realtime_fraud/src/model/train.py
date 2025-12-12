"""
Train baseline IsolationForest and an Autoencoder on historical data.
Saves models into the output directory specified by --out (default: models/).
"""
import argparse, os
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from autoencoder import build_autoencoder

def train_iso(X, out_dir):
    iso = IsolationForest(n_estimators=200, contamination=0.01, random_state=42)
    iso.fit(X)
    joblib.dump(iso, os.path.join(out_dir, "isolation_forest.joblib"))
    print("Saved IsolationForest")

def train_autoencoder(X, out_dir, latent_dim=8, epochs=50, batch_size=256):
    from tensorflow.keras.models import Model
    from tensorflow.keras.callbacks import EarlyStopping
    from tensorflow.keras.optimizers import Adam
    input_dim = X.shape[1]
    model = build_autoencoder(input_dim, latent_dim)
    model.compile(optimizer=Adam(1e-3), loss="mse")
    es = EarlyStopping(monitor="loss", patience=5, restore_best_weights=True)
    model.fit(X, X, epochs=epochs, batch_size=batch_size, callbacks=[es], verbose=1)
    #model.save(os.path.join(out_dir, "autoencoder"))
    model.save(os.path.join(out_dir, "autoencoder.keras"))

    print("Saved Autoencoder")
    
    
FEATURE_COLUMNS = [
    "amount",
    "velocity_1h",
    "is_international",
    "card_present",
    "device_type"
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--out", default="models")
    args = p.parse_args()

    df = pd.read_csv(args.data)
    os.makedirs(args.out, exist_ok=True)

    # Check feature presence
    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing required columns in CSV: {missing}")

    X = df[FEATURE_COLUMNS].fillna(0).astype(float)
    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)
    joblib.dump(scaler, os.path.join(args.out, "scaler.joblib"))
    print("Saved scaler")

    train_iso(Xs, args.out)
    train_autoencoder(Xs, args.out)

if __name__ == "__main__":
    main()