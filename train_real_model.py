# train_real_model.py
import psycopg2
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

def train_model_from_database():
    # Connect to database
    conn = psycopg2.connect('postgresql://postgres:12345@localhost:5432/placeiq')
    
    # Fetch colleges with valid placement data
    query = """
        SELECT 
            tier, 
            nirf_rank, 
            avg_ctc,
            placement_pct
        FROM colleges 
        WHERE avg_ctc IS NOT NULL AND avg_ctc > 0
        AND tier IS NOT NULL
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"📊 Loaded {len(df)} colleges with placement data")
    
    if len(df) < 50:
        print("⚠️ Not enough data for training. Using fallback.")
        return None
    
    # Features: tier, nirf_rank (fill missing nirf_rank with 500)
    df['nirf_rank'] = df['nirf_rank'].fillna(500)
    
    X = df[['tier', 'nirf_rank']].values
    y = df['avg_ctc'].values
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, min_samples_split=5, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"✅ Model trained on {len(X_train)} colleges")
    print(f"   Test MAE: ₹{mae:.2f}L")
    print(f"   Test R² Score: {r2:.3f}")
    
    # Save model
    joblib.dump(model, 'college_ctc_model.pkl')
    print("💾 Model saved as 'college_ctc_model.pkl'")
    
    return model

if __name__ == "__main__":
    train_model_from_database()