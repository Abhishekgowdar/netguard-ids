"""
Machine Learning based anomaly detection
Uses Isolation Forest algorithm to detect unusual network patterns
"""
import logging
import pickle
from pathlib import Path
from typing import Dict, Optional
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class MLDetector:
    """
    ML-based anomaly detector using Isolation Forest
    """

    def __init__(self, model_path: Optional[Path] = None, threshold: float = -0.5):
        """
        Initialize ML detector

        Args:
            model_path: Path to trained model file (.pkl)
            threshold: Anomaly score threshold (Isolation Forest score)
        """
        self.model_path = model_path
        self.threshold = threshold
        self.model = None
        self.model_loaded = False

        # Try to load the model
        if model_path and model_path.exists():
            self.load_model(model_path)
        else:
            logger.warning(f"⚠️  ML model not found at {model_path}")
            logger.warning("   ML detection will be disabled until model is trained")
            logger.info("   Run: python ml-training/scripts/train_model.py")

    def load_model(self, model_path: Path):
        """Load trained model from file"""
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            self.model_loaded = True
            logger.info(f"✅ ML model loaded from {model_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load ML model: {e}")
            self.model_loaded = False

    def detect(self, packet_data: Dict) -> Optional[Dict]:
        """
        Detect anomalies using ML model

        Args:
            packet_data: Parsed packet dictionary

        Returns:
            Alert dictionary if anomaly detected, None otherwise
        """
        if not self.model_loaded:
            return None

        try:
            # Extract features for ML
            features = self._extract_features(packet_data)

            if features is None:
                return None

            # Reshape for model prediction (model expects 2D array)
            features_array = np.array([features])

            # Predict anomaly score
            # Isolation Forest returns:
            #  1 = normal
            # -1 = anomaly
            prediction = self.model.predict(features_array)[0]

            # Get anomaly score (more negative = more anomalous)
            anomaly_score = self.model.score_samples(features_array)[0]

            # Check if it's an anomaly
            if prediction == -1 or anomaly_score < self.threshold:
                severity = self._calculate_severity(anomaly_score)

                logger.warning(f"🤖 ML Anomaly detected (score: {anomaly_score:.3f})")

                return {
                    'type': 'Anomaly Detected (ML)',
                    'severity': severity,
                    'source_ip': packet_data.get('src_ip'),
                    'target_ip': packet_data.get('dst_ip'),
                    'target_port': packet_data.get('dst_port'),
                    'protocol': packet_data.get('protocol'),
                    'description': f'ML model detected unusual network behavior (anomaly score: {anomaly_score:.3f})',
                    'anomaly_score': float(anomaly_score),
                    'timestamp': datetime.now().isoformat(),
                    'confidence': self._score_to_confidence(anomaly_score)
                }

            return None

        except Exception as e:
            logger.error(f"Error in ML detection: {e}")
            return None

    def _extract_features(self, packet_data: Dict) -> Optional[list]:
        """
        Extract numerical features from packet for ML model

        This is a simplified feature extraction.
        In production, you'd extract 41 features matching the NSL-KDD dataset
        """
        try:
            protocol_map = {'TCP': 0, 'UDP': 1, 'ICMP': 2}
            protocol = protocol_map.get(packet_data.get('protocol', 'TCP'), 3)

            # Extract basic features (simplified)
            features = [
                0,  # duration (would need connection tracking)
                protocol,  # protocol type
                packet_data.get('length', 0),  # packet size
                packet_data.get('src_port', 0) if packet_data.get('src_port') else 0,
                packet_data.get('dst_port', 0) if packet_data.get('dst_port') else 0,
                1 if packet_data.get('src_ip') == packet_data.get('dst_ip') else 0,  # land attack
                len(packet_data.get('payload', '')),  # payload size
                1 if packet_data.get('flags') and 'SYN' in packet_data.get('flags', '') else 0,
            ]

            # Pad or truncate to match model's expected feature count
            # Most Isolation Forest models expect consistent feature count
            while len(features) < 10:  # Minimum features
                features.append(0)

            return features[:10]  # Use first 10 features

        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None

    def _calculate_severity(self, anomaly_score: float) -> int:
        """
        Calculate alert severity based on anomaly score

        Args:
            anomaly_score: Isolation Forest anomaly score (more negative = more anomalous)

        Returns:
            Severity level (1-10)
        """
        # Isolation Forest scores typically range from -1 to 0 for anomalies
        if anomaly_score < -0.8:
            return 9  # CRITICAL
        elif anomaly_score < -0.6:
            return 7  # HIGH
        elif anomaly_score < -0.4:
            return 5  # MEDIUM
        else:
            return 3  # LOW

    def _score_to_confidence(self, anomaly_score: float) -> float:
        """Convert anomaly score to confidence percentage"""
        # More negative score = higher confidence it's an anomaly
        confidence = min(abs(anomaly_score), 1.0)
        return round(confidence, 2)

    def is_available(self) -> bool:
        """Check if ML detection is available"""
        return self.model_loaded


if __name__ == "__main__":
    # Test ML detector
    logging.basicConfig(level=logging.INFO)

    detector = MLDetector()

    if detector.is_available():
        # Test with sample packet
        packet = {
            'src_ip': '192.168.1.100',
            'dst_ip': '8.8.8.8',
            'src_port': 12345,
            'dst_port': 80,
            'protocol': 'TCP',
            'length': 1500,
            'flags': 'SYN',
            'payload': 'GET / HTTP/1.1'
        }

        alert = detector.detect(packet)
        if alert:
            print(f"🚨 Alert: {alert}")
        else:
            print("✅ No anomaly detected")
    else:
        print("❌ ML detector not available - model not loaded")
