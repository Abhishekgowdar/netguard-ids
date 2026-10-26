"""
Train Isolation Forest model for anomaly detection
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import time
from pathlib import Path


def load_data(file_path: Path):
    """Load NSL-KDD dataset"""
    print(f"Loading data from: {file_path}")

    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {len(df)} samples")
        return df
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None


def preprocess_data(df):
    """Preprocess data for training"""
    print("\nPreprocessing data...")

    # Create a copy
    data = df.copy()

    # Remove difficulty column if present
    if 'difficulty' in data.columns:
        data = data.drop('difficulty', axis=1)

    # Separate features and labels
    X = data.drop('label', axis=1)
    y = data['label']

    # Convert labels to binary (normal = 0, attack = 1)
    y_binary = y.apply(lambda x: 0 if x == 'normal' else 1)

    # Encode categorical features
    categorical_columns = ['protocol_type', 'service', 'flag']

    print("Encoding categorical features...")
    for col in categorical_columns:
        if col in X.columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))

    # Handle any remaining object columns
    for col in X.columns:
        if X[col].dtype == 'object':
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))

    # Fill any missing values
    X = X.fillna(0)

    # Feature scaling
    print("Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print(f"✅ Preprocessing complete")
    print(f"   Features: {X_scaled.shape[1]}")
    print(f"   Samples: {X_scaled.shape[0]}")
    print(f"   Normal: {(y_binary == 0).sum()}")
    print(f"   Attacks: {(y_binary == 1).sum()}")

    return X_scaled, y_binary, scaler


def train_model(X_train, y_train):
    """Train Isolation Forest model"""
    print("\nTraining Isolation Forest model...")
    print("This may take 2-5 minutes...")

    # Calculate contamination (percentage of anomalies in training data)
    contamination = (y_train == 1).sum() / len(y_train)
    print(f"Contamination rate: {contamination:.2%}")

    # Create and train model
    model = IsolationForest(
        contamination=contamination,
        max_samples='auto',
        random_state=42,
        n_estimators=100,
        n_jobs=-1,  # Use all CPU cores
        verbose=1
    )

    start_time = time.time()
    model.fit(X_train)
    training_time = time.time() - start_time

    print(f"✅ Training complete in {training_time:.2f} seconds")

    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate model performance"""
    print("\nEvaluating model...")

    # Predict
    predictions = model.predict(X_test)

    # Convert predictions: -1 (anomaly) to 1, 1 (normal) to 0
    predictions_binary = np.where(predictions == -1, 1, 0)

    # Get anomaly scores
    scores = model.score_samples(X_test)

    # Calculate metrics
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)

    print("\nClassification Report:")
    print(classification_report(y_test, predictions_binary, target_names=['Normal', 'Attack']))

    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, predictions_binary)
    print(cm)
    print(f"\nTrue Negatives:  {cm[0][0]}")
    print(f"False Positives: {cm[0][1]}")
    print(f"False Negatives: {cm[1][0]}")
    print(f"True Positives:  {cm[1][1]}")

    # Calculate accuracy
    accuracy = (cm[0][0] + cm[1][1]) / cm.sum()
    print(f"\nAccuracy: {accuracy:.2%}")

    # Detection rate
    detection_rate = cm[1][1] / (cm[1][0] + cm[1][1]) if (cm[1][0] + cm[1][1]) > 0 else 0
    print(f"Detection Rate: {detection_rate:.2%}")

    # False Positive Rate
    fpr = cm[0][1] / (cm[0][0] + cm[0][1]) if (cm[0][0] + cm[0][1]) > 0 else 0
    print(f"False Positive Rate: {fpr:.2%}")

    return {
        'accuracy': accuracy,
        'detection_rate': detection_rate,
        'fpr': fpr,
        'confusion_matrix': cm
    }


def save_model(model, scaler, output_dir: Path):
    """Save trained model and scaler"""
    print(f"\nSaving model to: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save model
    model_path = output_dir / 'isolation_forest.pkl'
    joblib.dump(model, model_path)
    print(f"✅ Model saved: {model_path}")

    # Save scaler
    scaler_path = output_dir / 'scaler.pkl'
    joblib.dump(scaler, scaler_path)
    print(f"✅ Scaler saved: {scaler_path}")

    return model_path, scaler_path


def main():
    """Main training pipeline"""
    print("=" * 60)
    print("NetGuard IDS - ML Model Training")
    print("=" * 60)

    # Paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data' / 'raw'
    model_dir = script_dir.parent / 'models'

    train_file = data_dir / 'KDDTrain+.csv'
    test_file = data_dir / 'KDDTest+.csv'

    # Check if data files exist
    if not train_file.exists():
        print(f"\n❌ Training data not found: {train_file}")
        print("Please run: python ml-training/scripts/download_dataset.py")
        return

    # Load data
    train_df = load_data(train_file)
    if train_df is None:
        return

    # Use smaller subset for faster training (optional)
    print(f"\nUsing subset of data for faster training...")
    train_df = train_df.sample(n=min(50000, len(train_df)), random_state=42)
    print(f"Training samples: {len(train_df)}")

    # Preprocess training data
    X_train, y_train, scaler = preprocess_data(train_df)

    if X_train is None:
        return

    # Train model
    model = train_model(X_train, y_train)

    # Load test data if available
    if test_file.exists():
        test_df = load_data(test_file)
        if test_df is not None:
            # Use subset for testing
            test_df = test_df.sample(n=min(20000, len(test_df)), random_state=42)
            X_test, y_test, _ = preprocess_data(test_df)

            # Scale test data using training scaler
            X_test_scaled = scaler.transform(X_test.reshape(X_test.shape[0], -1) if len(X_test.shape) == 1 else X_test)

            # Evaluate
            metrics = evaluate_model(model, X_test_scaled, y_test)

    # Save model
    model_path, scaler_path = save_model(model, scaler, model_dir)

    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    print(f"\nModel saved to: {model_path}")
    print(f"Scaler saved to: {scaler_path}")
    print("\nNext steps:")
    print("  1. Start the backend: python backend/main.py")
    print("  2. The model will be automatically loaded")
    print("=" * 60)


if __name__ == "__main__":
    main()
