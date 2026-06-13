import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# 1. Load the ML-ready dataset
print("Loading ML-ready dataset...")
df = pd.read_csv('./data/ml_ready_dataset/ml_ready_dataset.csv')

# 2. Define Targets (y) and Features (X)
# What we want to predict:
y_duration = df['duration_ms']
y_cost = df['cost_usd']

# What we use to make the predictions (Drop the targets AND 'memory_mb' to prevent data leakage)
X = df.drop(columns=['duration_ms', 'cost_usd', 'memory_mb'])

# 3. Train-Test Split (80% of data for training, 20% for testing)
print("Splitting data into 80% training and 20% testing...")
X_train, X_test, y_train_dur, y_test_dur = train_test_split(X, y_duration, test_size=0.2, random_state=42)
_, _, y_train_cost, y_test_cost = train_test_split(X, y_cost, test_size=0.2, random_state=42)

# 4. Train the Performance (Duration) Model
print("Training the Performance Model... (This may take a few seconds)")
# n_jobs=-1 tells your computer to use all CPU cores to train faster
rf_duration = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_duration.fit(X_train, y_train_dur)

# 5. Train the Cost Model
print("Training the Cost Model...")
rf_cost = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_cost.fit(X_train, y_train_cost)

# 6. Evaluate the Models on the unseen Test data
print("\n=== MODEL EVALUATION RESULTS ===")
dur_preds = rf_duration.predict(X_test)
cost_preds = rf_cost.predict(X_test)

# Calculate metrics
dur_r2 = r2_score(y_test_dur, dur_preds)
dur_mae = mean_absolute_error(y_test_dur, dur_preds)

cost_r2 = r2_score(y_test_cost, cost_preds)
cost_mae = mean_absolute_error(y_test_cost, cost_preds)

print(f"Performance Predictor | R² Score: {dur_r2:.4f} | Mean Absolute Error: {dur_mae:.2f} ms")
print(f"Cost Predictor        | R² Score: {cost_r2:.4f} | Mean Absolute Error: ${cost_mae:.8f}")

# ==========================================
# 7. SAVE THE MODELS FOR THE CLI TOOL
# ==========================================

# Create the 'models' folder if it doesn't exist yet
os.makedirs('./models', exist_ok=True)

# Save BOTH trained models to physical files
joblib.dump(rf_duration, './models/serverless_duration_model.joblib')
joblib.dump(rf_cost, './models/serverless_cost_model.joblib')

# Save the column structure (CRITICAL for the CLI tool to know the 58 columns)
joblib.dump(list(X.columns), './models/model_features.joblib')

print("\n✅ Physical models and features successfully saved to disk in the './models' folder!")