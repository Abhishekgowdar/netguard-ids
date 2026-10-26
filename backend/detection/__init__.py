"""
Detection module for identifying network threats
"""
from .signature_rules import SignatureDetector
from .ml_detector import MLDetector

__all__ = ['SignatureDetector', 'MLDetector']
