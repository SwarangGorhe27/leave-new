"""
Swipe Log Detection Service - Intelligence for duplicate, spoof, and geofence detection.

Provides:
- Duplicate punch detection
- Spoof/fraud detection
- Geofence validation
- Invalid sequence detection
"""

import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

from apps.attendance.models.punch_and_daily import PunchLog
from apps.attendance.services.swipe_logs.swipe_log_logging_service import SwipeLogLoggingService

logger = logging.getLogger(__name__)


class SwipeLogDetectionService:
    """
    Service for detecting anomalies and fraud in swipe logs.
    
    Implements:
    - Duplicate punch detection (same punch within time window)
    - Spoof detection (face recognition spoofing)
    - Geofence validation (punch within allowed location)
    - Invalid sequence detection (IN/OUT sequence violations)
    """

    def __init__(self):
        """Initialize service."""
        self.logging_service = SwipeLogLoggingService()

    # ─────────────────────────────────────────────────────────────
    # Duplicate Detection
    # ─────────────────────────────────────────────────────────────

    def detect_duplicate_punch(
        self,
        punch_log: PunchLog,
        time_window_seconds: int = 60,
    ) -> Tuple[bool, Optional[float], Optional[Dict[str, Any]]]:
        """
        Detect duplicate punch within time window.
        
        A duplicate is defined as:
        - Same employee
        - Same punch type (IN/OUT)
        - Punch time within specified time window
        - Same device or punch source
        
        Args:
            punch_log: Current punch log
            time_window_seconds: Time window to check for duplicates (default 60s)
        
        Returns:
            Tuple of (is_duplicate: bool, confidence_score: float, details: dict)
        """
        # Look for punches in time window
        time_start = punch_log.punch_time - timedelta(seconds=time_window_seconds)
        time_end = punch_log.punch_time + timedelta(seconds=time_window_seconds)

        duplicates = PunchLog.objects.filter(
            employee=punch_log.employee,
            punch_type=punch_log.punch_type,
            punch_time__gte=time_start,
            punch_time__lte=time_end,
        ).exclude(id=punch_log.id)

        if not duplicates.exists():
            return False, 0.0, None

        # Find closest duplicate
        closest = min(
            duplicates,
            key=lambda p: abs((p.punch_time - punch_log.punch_time).total_seconds())
        )

        time_diff = abs((closest.punch_time - punch_log.punch_time).total_seconds())

        # Calculate confidence score (higher = more likely duplicate)
        # 100% confidence if same device and within 5 seconds
        # Reduce confidence for different devices
        confidence = 1.0

        if punch_log.device_id and closest.device_id:
            if punch_log.device_id != closest.device_id:
                confidence *= 0.7  # Different devices reduce confidence

        # Time-based scoring: closer punches = higher confidence
        if time_diff > 10:
            confidence *= 0.8
        if time_diff > 30:
            confidence *= 0.6

        details = {
            "duplicate_punch_id": str(closest.id),
            "time_difference_seconds": time_diff,
            "confidence_score": confidence,
            "same_device": punch_log.device_id == closest.device_id,
        }

        if confidence > 0.5:
            # Log detection
            self.logging_service.log_duplicate_detected(
                str(punch_log.id),
                str(closest.id),
                confidence,
                str(punch_log.company_id),
            )

        return confidence > 0.5, confidence, details

    # ─────────────────────────────────────────────────────────────
    # Spoof Detection
    # ─────────────────────────────────────────────────────────────

    def detect_spoof_attempt(
        self,
        punch_log: PunchLog,
    ) -> Tuple[bool, Optional[float], Optional[Dict[str, Any]]]:
        """
        Detect potential face spoofing attempt.
        
        Indicators:
        - Face verification failed but punch accepted
        - Unusually high face match score (>95% - might be presentation attack)
        - Rapid multiple punches (>3 in 60 seconds)
        - Face punch with low face_verified flag
        
        Args:
            punch_log: Current punch log
        
        Returns:
            Tuple of (is_spoof: bool, confidence_score: float, details: dict)
        """
        confidence = 0.0
        details = {
            "indicators": [],
        }

        # Check if face punch
        is_face_punch = punch_log.punch_mode and "FACE" in punch_log.punch_mode.upper()

        if not is_face_punch:
            return False, 0.0, details

        # Check face verification status
        if punch_log.face_verified is False:
            confidence += 0.3
            details["indicators"].append("face_verification_failed")

        # Check face match score from metadata
        face_match_score = None
        if punch_log.meta_data and isinstance(punch_log.meta_data, dict):
            face_match_score = punch_log.meta_data.get("face_match_score")

        if face_match_score:
            # Unusually high score might indicate presentation attack
            if face_match_score > 0.99:
                confidence += 0.25
                details["indicators"].append("unusually_high_face_score")
                details["face_match_score"] = face_match_score

            # Low score with high verification is suspicious
            if face_match_score < 0.60 and punch_log.face_verified:
                confidence += 0.2
                details["indicators"].append("low_face_score_but_verified")

        # Check for rapid multiple punches
        recent_punches = PunchLog.objects.filter(
            employee=punch_log.employee,
            punch_time__gte=punch_log.punch_time - timedelta(seconds=60),
            punch_time__lte=punch_log.punch_time,
            punch_mode__icontains="FACE",
        ).count()

        if recent_punches > 3:
            confidence += 0.2
            details["indicators"].append(f"rapid_face_punches_{recent_punches}_in_60s")

        details["confidence_score"] = confidence

        if confidence > 0.4:
            # Log detection
            self.logging_service.log_spoof_detected(
                str(punch_log.id),
                confidence,
                str(punch_log.company_id),
            )

        return confidence > 0.4, confidence, details

    # ─────────────────────────────────────────────────────────────
    # Geofence Validation
    # ─────────────────────────────────────────────────────────────

    def validate_geofence(
        self,
        punch_log: PunchLog,
        office_latitude: Decimal,
        office_longitude: Decimal,
        geofence_radius_meters: int = 500,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate if punch is within geofence (office location).
        
        Args:
            punch_log: Current punch log
            office_latitude: Office latitude
            office_longitude: Office longitude
            geofence_radius_meters: Allowed radius in meters (default 500m)
        
        Returns:
            Tuple of (is_within_geofence: bool, details: dict)
        """
        details = {
            "has_gps_coordinates": punch_log.latitude is not None,
        }

        # If no GPS coordinates, cannot validate
        if punch_log.latitude is None or punch_log.longitude is None:
            details["reason"] = "no_gps_coordinates"
            return None, details

        # Calculate distance using Haversine formula
        distance_meters = self._calculate_distance(
            float(punch_log.latitude),
            float(punch_log.longitude),
            float(office_latitude),
            float(office_longitude),
        )

        is_within = distance_meters <= geofence_radius_meters

        details["distance_meters"] = round(distance_meters, 2)
        details["allowed_radius_meters"] = geofence_radius_meters
        details["is_within_geofence"] = is_within

        if not is_within:
            # Log violation
            self.logging_service.log_geofence_violation(
                str(punch_log.id),
                str(punch_log.employee_id),
                punch_log.latitude,
                punch_log.longitude,
                str(punch_log.company_id),
            )

        return is_within, details

    # ─────────────────────────────────────────────────────────────
    # Sequence Validation
    # ─────────────────────────────────────────────────────────────

    def detect_invalid_sequence(
        self,
        punch_log: PunchLog,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Detect invalid punch sequence.
        
        Valid sequences:
        - IN -> OUT (normal)

        Invalid sequences:
        - OUT without preceding IN
        - Multiple consecutive INs
        - Multiple consecutive OUTs
        
        Args:
            punch_log: Current punch log
        
        Returns:
            Tuple of (is_invalid: bool, details: dict)
        """
        details = {
            "issues": [],
        }

        # Get employee's punches today so far (excluding current)
        today_start = punch_log.punch_time.replace(hour=0, minute=0, second=0, microsecond=0)
        today_punches = list(
            PunchLog.objects.filter(
                employee=punch_log.employee,
                punch_time__gte=today_start,
                punch_time__lt=punch_log.punch_time,
            ).order_by("punch_time").values_list("punch_type", flat=True)
        )

        current_type = punch_log.punch_type

        # No previous punches today
        if not today_punches:
            # First punch must be IN
            if current_type != "IN":
                details["issues"].append("first_punch_must_be_in")
                return True, details
            return False, details

        # Get last punch type
        last_type = today_punches[-1]

        # Validate sequence
        valid_next_punches = self._get_valid_next_punches(last_type)

        if current_type not in valid_next_punches:
            details["issues"].append(
                f"invalid_sequence_{last_type}_to_{current_type}"
            )

            # Log invalid sequence
            self.logging_service.log_invalid_sequence(
                str(punch_log.id),
                str(punch_log.employee_id),
                f"Invalid sequence: {last_type} -> {current_type}",
                str(punch_log.company_id),
            )

            return True, details

        return False, details

    # ─────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────

    def _get_valid_next_punches(self, last_punch_type: str) -> list[str]:
        """
        Get valid punch types after a given punch type.
        
        Args:
            last_punch_type: Previous punch type
        
        Returns:
            List of valid next punch types
        """
        sequence_map = {
            "IN": ["OUT"],
            "OUT": ["IN"],
            "UNKNOWN": ["IN", "OUT"],
        }

        return sequence_map.get(last_punch_type, ["IN"])

    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Calculate distance between two GPS coordinates using Haversine formula.
        
        Args:
            lat1, lon1: First coordinate
            lat2, lon2: Second coordinate
        
        Returns:
            Distance in meters
        """
        import math

        # Earth's radius in meters
        R = 6371000

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )

        c = 2 * math.asin(math.sqrt(a))

        return R * c
