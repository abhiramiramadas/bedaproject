# ==========================================================
# 🔐 Configuration File - API Keys & Settings
# ==========================================================
# Copy this file to config.py and fill in your own values.
# ⚠️ IMPORTANT: Never commit config.py to version control!
# ==========================================================

# Email Configuration (Gmail)
SENDER_EMAIL = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"  # Use App Password, not regular password

# Emergency Contact Emails
EMERGENCY_CONTACTS = [
    "emergency@example.com",
]

# Family/Nominee Contacts
NOMINEE_CONTACTS = [
    "family@example.com",
]

# Weather API (OpenWeatherMap) — get a free key at https://openweathermap.org/api
WEATHER_API_KEY = "your-openweathermap-api-key"

# Default Location (Chennai, India)
DEFAULT_LATITUDE = 13.0827
DEFAULT_LONGITUDE = 80.2707

# YOLO Model Settings
MODEL_PATHS = {
    "light": "models/yolov8n.pt",    # Nano - Low memory systems
    "medium": "models/yolov8s.pt",   # Small - Medium memory
    "heavy": "models/yolov8m.pt"     # Medium - High memory systems
}

# Detection Thresholds
IOU_THRESHOLD_LOW = 0.20      # Minimum IoU for collision detection
IOU_THRESHOLD_MEDIUM = 0.30   # Medium severity threshold
IOU_THRESHOLD_HIGH = 0.40     # High severity threshold

# Minimum speed to consider (filters out parked/stationary cars)
MIN_SPEED_FOR_ACCIDENT = 5    # At least one vehicle must be moving this fast (pixels/frame)

# Temporal consistency — require overlap across N consecutive frames before alerting
CONSECUTIVE_FRAMES_THRESHOLD = 3

# Maximum centroid distance (pixels) for two vehicles to be considered a collision
CENTROID_DISTANCE_THRESHOLD = 150

# Speed Thresholds (pixels per frame)
SPEED_LOW = 15
SPEED_MEDIUM = 30
SPEED_HIGH = 50

# Flask Server Settings
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
DEBUG_MODE = True

# File Storage
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "jpg", "jpeg", "png"}

# Alert Settings
ENABLE_EMAIL_ALERTS = True
ENABLE_SMS_ALERTS = False  # Set to True if SMS configured
ALERT_COOLDOWN_SECONDS = 30  # Prevent spam alerts

# OCR Settings (for Number Plate Recognition)
ENABLE_OCR = True
OCR_CONFIDENCE_THRESHOLD = 0.6

# Insurance API Settings (placeholder)
INSURANCE_API_URL = "https://api.insurance-provider.com/claims"
INSURANCE_API_KEY = "your-insurance-api-key"

# Organ Donation Registry API (placeholder)
ORGAN_DONATION_API_URL = "https://api.organ-registry.com/alert"
BLOOD_BANK_API_URL = "https://api.blood-bank.com/request"
