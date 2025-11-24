import pandas as pd
import numpy as np
import hashlib
import json
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib

# --- Configuration ---
N_SAMPLES = 1000  # Increased for better model
RANDOM_SEED = 42
TARGET_TRAIT = 'C'
USE_SURVEY = False  # Set False for blockchain-only oracle
np.random.seed(RANDOM_SEED)

# --- Mock Data (shared) ---
def mock_koios_fetch(address):
    hash_val = int(hashlib.sha256(address.encode()).hexdigest(), 16)
    return {
        "tx_count": 10 + (hash_val % 500),
        "avg_tx_size_ada": 50 + (hash_val % 100) / 10.0,
        "days_staked": 30 + (hash_val % 365),
        "tx_freq_daily": (hash_val % 50) / 100.0,  # Added feature
    }

# --- Generate Data ---
def generate_training_data(n_samples):
    addresses = [f"addr1q{i:010d}..." for i in range(n_samples)]
    data = []
    
    for address in addresses:
        # Generate true trait score
        true_score = np.random.randint(30, 80)
        
        # Generate KOIOS features
        koios_data = mock_koios_fetch(address)
        
        sample = {
            "address": address,
            "true_score": true_score,
            **koios_data  # Flatten features
        }
        data.append(sample)
    
    return pd.DataFrame(data)

# --- Preprocess ---
def preprocess_training_data(df):
    feature_cols = ["tx_count", "avg_tx_size_ada", "days_staked", "tx_freq_daily"]
    X = df[feature_cols]
    y = df["true_score"]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    return X_scaled, y, scaler, feature_cols

# --- Train Model ---
def train_and_save_model():
    print(f"Training model on {N_SAMPLES} samples...")
    
    # Generate and preprocess data
    df = generate_training_data(N_SAMPLES)
    X, y, scaler, feature_cols = preprocess_training_data(df)
    
    # Train
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED
    )
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    print(f"Model R²: {r2:.4f}")
    
    # Save artifacts
    joblib.dump(model, "ml-model/model.joblib")
    joblib.dump(scaler, "ml-model/scaler.joblib")
    with open("ml-model/feature_columns.json", "w") as f:
        json.dump(feature_cols, f)
    
    print("Model saved to ml-model/")

if __name__ == "__main__":
    train_and_save_model()