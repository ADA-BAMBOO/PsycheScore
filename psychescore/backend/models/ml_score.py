import json
import os
import time
import hashlib
import joblib
import numpy as np
import pandas as pd
import warnings  # Required for warning suppression
from pycardano import PaymentSigningKey, PaymentVerificationKey
import argparse

# --- Suppress external library warnings ---
warnings.filterwarnings("ignore", category=DeprecationWarning, module='cryptography.*')
warnings.filterwarnings("ignore", category=DeprecationWarning, module='paramiko.*')

# --- Configuration ---
SCORE_JSON_FILE = "ml-model/score.json"
KEY_DIR = "ml-model"
SKEY_PATH = os.path.join(KEY_DIR, "oracle.skey")
VKEY_PATH = os.path.join(KEY_DIR, "oracle.vkey")

def load_ml_model():
    """Load trained model, scaler, and feature columns."""
    try:
        model = joblib.load("ml-model/model.joblib")
        scaler = joblib.load("ml-model/scaler.joblib")
        with open("ml-model/feature_columns.json", "r") as f:
            feature_cols = json.load(f)
        return model, scaler, feature_cols
    except FileNotFoundError as e:
        print(f"ERROR: Missing model file: {e}")
        print("Run 'python train_model.py' first to train the model.")
        exit(1)

def mock_koios_fetch(address):
    """Generate deterministic mock KOIOS features."""
    hash_val = int(hashlib.sha256(address.encode()).hexdigest(), 16)
    return {
        "tx_count": 10 + (hash_val % 500),
        "avg_tx_size_ada": 50 + (hash_val % 100) / 10.0,
        "days_staked": 30 + (hash_val % 365),
        "tx_freq_daily": (hash_val % 50) / 100.0,
    }

def load_or_generate_keys():
    """Loads existing oracle keys or generates and saves both skey and vkey."""
    if os.path.exists(SKEY_PATH):
        print(f"Loading existing oracle keys from {KEY_DIR}/")
        skey = PaymentSigningKey.load(SKEY_PATH)
        vkey = PaymentVerificationKey.from_signing_key(skey)
    else:
        print(f"Generating new oracle keys in {KEY_DIR}/")
        os.makedirs(KEY_DIR, exist_ok=True)
        
        skey = PaymentSigningKey.generate()
        skey.save(SKEY_PATH)
        
        vkey = PaymentVerificationKey.from_signing_key(skey)
        vkey.save(VKEY_PATH)  # ✅ Saves verification key
        
        print(f"✅ Oracle signing key saved to: {SKEY_PATH}")
        print(f"✅ Oracle verification key saved to: {VKEY_PATH}")
    
    return skey, vkey

def generate_features(wallet_addr: str, feature_cols):
    """
    ✅ FIXED: Returns DataFrame with proper column names to match training format
    """
    koios_data = mock_koios_fetch(wallet_addr)
    features = pd.DataFrame([[koios_data[col] for col in feature_cols]], columns=feature_cols)
    return features, koios_data

def predict_ml_score(wallet_addr: str) -> tuple[dict, PaymentSigningKey]:
    """Fetch features, predict score, and prepare datum."""
    model, scaler, feature_cols = load_ml_model()
    features, koios_data = generate_features(wallet_addr, feature_cols)
    
    # ✅ No more warning: features is now a DataFrame
    features_scaled = scaler.transform(features)
    score = model.predict(features_scaled)[0]
    score = max(0, min(100, round(float(score), 2)))
    
    skey, vkey = load_or_generate_keys()
    
    datum = {
        "address": wallet_addr,
        "score": score,
        "timestamp": int(time.time()),
        "oracle_vkey": vkey.to_cbor_hex(),
        "model_version": "v1.0",
        "koios_data": koios_data
    }
    
    return datum, skey

def sign_datum(datum: dict, tx_hash: str, skey: PaymentSigningKey) -> dict:
    """Construct message and create cryptographic signature."""
    ml_policy = os.getenv("ML_POLICY_ID", "c965889476530cae6fc1b22b4f3c1571fb5d29c09d99529ae5f3046c")
    score_bytes = int(datum["score"]).to_bytes(3, 'big')
    
    message_bytes = (
        ml_policy.encode('utf-8') +
        tx_hash.encode('utf-8') +
        datum['address'].encode('utf-8') +
        score_bytes
    )
    
    signature = skey.sign(message_bytes).hex()
    datum["sig"] = signature
    return datum

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate and sign ML prediction')
    parser.add_argument('wallet_address', type=str, help='Wallet address to analyze')
    parser.add_argument('tx_hash', type=str, help='Transaction hash for signature binding')
    
    args = parser.parse_args()
    datum, skey = predict_ml_score(args.wallet_address)
    signed_datum = sign_datum(datum, args.tx_hash, skey)
    
    os.makedirs(KEY_DIR, exist_ok=True)
    with open(SCORE_JSON_FILE, "w") as f:
        json.dump(signed_datum, f, indent=2)
    
    print(f"\n✅ Score: {signed_datum['score']} | Files: {SCORE_JSON_FILE}, {VKEY_PATH}")