# ==========================================================
# 🚨 Alert System - Email & SMS Notifications
# ==========================================================

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import json

try:
    from config import (
        SENDER_EMAIL, EMAIL_PASSWORD, EMERGENCY_CONTACTS,
        NOMINEE_CONTACTS, ENABLE_EMAIL_ALERTS
    )
except ImportError:
    print("⚠️ config.py not found. Using default settings.")
    SENDER_EMAIL = ""
    EMAIL_PASSWORD = ""
    EMERGENCY_CONTACTS = []
    NOMINEE_CONTACTS = []
    ENABLE_EMAIL_ALERTS = False


class AlertSystem:
    """Handles all emergency alert notifications"""
    
    def __init__(self):
        self.sender_email = SENDER_EMAIL
        self.email_password = EMAIL_PASSWORD
        self.last_alert_time = None
        self.alert_cooldown = 30  # seconds
        
    def _create_base_message(self, recipient, subject):
        """Create base email message"""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        return msg
    
    def _attach_image(self, msg, image_path):
        """Attach image to email"""
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment', 
                             filename=os.path.basename(image_path))
                msg.attach(img)
        return msg
    
    def _attach_file(self, msg, file_path):
        """Attach any file to email"""
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment',
                              filename=os.path.basename(file_path))
                msg.attach(part)
        return msg
    
    def _send_email(self, msg, recipient):
        """Send email via SMTP"""
        if not ENABLE_EMAIL_ALERTS:
            print(f"📧 [SIMULATED] Email would be sent to: {recipient}")
            return True
            
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.email_password)
            server.sendmail(self.sender_email, recipient, msg.as_string())
            server.quit()
            print(f"✅ Email sent to: {recipient}")
            return True
        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False
    
    def send_accident_alert(self, accident_data, image_path=None, video_path=None):
        """
        Send emergency accident alert
        
        Args:
            accident_data: dict with accident details
            image_path: path to accident frame image
            video_path: path to accident video clip
        """
        subject = f"🚨 ACCIDENT ALERT - {accident_data.get('severity', 'UNKNOWN')} SEVERITY"
        
        body = f"""
═══════════════════════════════════════════════════════
🚨 EMERGENCY ACCIDENT DETECTION ALERT 🚨
═══════════════════════════════════════════════════════

📅 Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📍 LOCATION DETAILS:
   • Latitude: {accident_data.get('latitude', 'N/A')}
   • Longitude: {accident_data.get('longitude', 'N/A')}
   • Address: {accident_data.get('address', 'N/A')}

⚠️ ACCIDENT DETAILS:
   • Severity Level: {accident_data.get('severity', 'UNKNOWN')}
   • Impact Score: {accident_data.get('impact_score', 'N/A')}
   • Vehicles Involved: {accident_data.get('vehicles_count', 'N/A')}
   • Collision IoU: {accident_data.get('iou', 'N/A'):.2%}

🚗 VEHICLE INFORMATION:
   • Vehicle Types: {', '.join(accident_data.get('vehicle_types', ['Unknown']))}
   • Number Plate: {accident_data.get('number_plate', 'Not Detected')}
   • Estimated Speed: {accident_data.get('speed', 'N/A')} km/h

🌤️ WEATHER CONDITIONS:
   • Weather: {accident_data.get('weather', 'N/A')}
   • Temperature: {accident_data.get('temperature', 'N/A')}°C
   • Visibility: {accident_data.get('visibility', 'N/A')}

🏥 NEAREST EMERGENCY SERVICES:
   • Hospital: {accident_data.get('nearest_hospital', 'N/A')}
   • Distance: {accident_data.get('hospital_distance', 'N/A')} km
   • Police Station: {accident_data.get('nearest_police', 'N/A')}
   • Distance: {accident_data.get('police_distance', 'N/A')} km

═══════════════════════════════════════════════════════
⚡ IMMEDIATE ACTION REQUIRED ⚡
═══════════════════════════════════════════════════════

This is an automated alert from the AI Accident Detection System.
Please dispatch emergency services immediately.

---
AI Accident Detection System v1.0
        """
        
        for recipient in EMERGENCY_CONTACTS:
            msg = self._create_base_message(recipient, subject)
            msg.attach(MIMEText(body, 'plain'))
            
            if image_path:
                self._attach_image(msg, image_path)
            if video_path:
                self._attach_file(msg, video_path)
                
            self._send_email(msg, recipient)
    
    def send_nominee_alert(self, accident_data, victim_info=None):
        """Send alert to family members/nominees"""
        
        subject = "🚨 URGENT: Family Member Involved in Accident"
        
        body = f"""
═══════════════════════════════════════════════════════
🚨 URGENT FAMILY NOTIFICATION 🚨
═══════════════════════════════════════════════════════

Dear Family Member,

We regret to inform you that a vehicle registered to your family
has been involved in an accident.

📅 Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📍 LOCATION:
   • Address: {accident_data.get('address', 'N/A')}
   • GPS: {accident_data.get('latitude', 'N/A')}, {accident_data.get('longitude', 'N/A')}

⚠️ ACCIDENT SEVERITY: {accident_data.get('severity', 'UNKNOWN')}

🚗 VEHICLE DETAILS:
   • Number Plate: {accident_data.get('number_plate', 'Not Available')}

🏥 EMERGENCY SERVICES:
   • Nearest Hospital: {accident_data.get('nearest_hospital', 'N/A')}
   • Emergency Contact: {accident_data.get('hospital_phone', 'N/A')}

Please contact the nearest hospital immediately or call emergency
services for more information.

═══════════════════════════════════════════════════════
EMERGENCY HELPLINE: 108 (India) | 911 (USA) | 112 (Europe)
═══════════════════════════════════════════════════════

---
AI Accident Detection System
        """
        
        for recipient in NOMINEE_CONTACTS:
            msg = self._create_base_message(recipient, subject)
            msg.attach(MIMEText(body, 'plain'))
            self._send_email(msg, recipient)
    
    def send_blood_donation_request(self, accident_data, blood_type="Unknown"):
        """Send blood donation request to family members"""
        
        subject = "🩸 URGENT: Blood Donation Required"
        
        body = f"""
═══════════════════════════════════════════════════════
🩸 URGENT BLOOD DONATION REQUEST 🩸
═══════════════════════════════════════════════════════

A severe accident has occurred and immediate blood donation
is required to save a life.

📅 Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🩸 BLOOD REQUIREMENT:
   • Blood Type Needed: {blood_type}
   • Urgency: CRITICAL
   • Units Required: Multiple units needed

🏥 HOSPITAL DETAILS:
   • Hospital: {accident_data.get('nearest_hospital', 'N/A')}
   • Address: {accident_data.get('hospital_address', 'N/A')}

📍 ACCIDENT LOCATION:
   • {accident_data.get('address', 'N/A')}

Please proceed to the nearest blood bank or the hospital
mentioned above if you are a matching donor.

═══════════════════════════════════════════════════════
YOUR DONATION CAN SAVE A LIFE!
═══════════════════════════════════════════════════════

---
AI Accident Detection System
        """
        
        for recipient in NOMINEE_CONTACTS:
            msg = self._create_base_message(recipient, subject)
            msg.attach(MIMEText(body, 'plain'))
            self._send_email(msg, recipient)
    
    def send_organ_donation_alert(self, accident_data):
        """Send organ donation alert in critical cases"""
        
        subject = "💚 Organ Donation Notification - Critical Case"
        
        body = f"""
═══════════════════════════════════════════════════════
💚 ORGAN DONATION NOTIFICATION 💚
═══════════════════════════════════════════════════════

Dear Family Member,

This is a sensitive notification regarding a critical
medical situation following an accident.

The medical team may discuss organ donation options
with you if the situation becomes critical.

📅 Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🏥 HOSPITAL INFORMATION:
   • Hospital: {accident_data.get('nearest_hospital', 'N/A')}
   • Contact: {accident_data.get('hospital_phone', 'N/A')}

Please contact the hospital for more information and
to discuss any decisions that may need to be made.

The organ donation registry has been notified as per
the registered donor's wishes.

═══════════════════════════════════════════════════════
For support: National Organ Donation Helpline
═══════════════════════════════════════════════════════

---
AI Accident Detection System
        """
        
        for recipient in NOMINEE_CONTACTS:
            msg = self._create_base_message(recipient, subject)
            msg.attach(MIMEText(body, 'plain'))
            self._send_email(msg, recipient)
    
    def send_insurance_claim(self, accident_data, damage_assessment):
        """Submit automated insurance claim"""
        
        subject = "📋 Automated Insurance Claim Submission"
        
        claim_data = {
            "claim_type": "accident",
            "timestamp": datetime.now().isoformat(),
            "severity": accident_data.get('severity'),
            "location": {
                "latitude": accident_data.get('latitude'),
                "longitude": accident_data.get('longitude'),
                "address": accident_data.get('address')
            },
            "vehicle": {
                "number_plate": accident_data.get('number_plate'),
                "type": accident_data.get('vehicle_types', [])
            },
            "damage_assessment": damage_assessment,
            "weather_conditions": accident_data.get('weather'),
            "evidence": {
                "images": accident_data.get('image_paths', []),
                "video": accident_data.get('video_path')
            }
        }
        
        body = f"""
═══════════════════════════════════════════════════════
📋 AUTOMATED INSURANCE CLAIM SUBMISSION 📋
═══════════════════════════════════════════════════════

Claim Reference: ACC-{datetime.now().strftime('%Y%m%d%H%M%S')}
Submission Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ACCIDENT DETAILS:
{json.dumps(claim_data, indent=2)}

DAMAGE ASSESSMENT:
   • Estimated Damage Level: {damage_assessment.get('level', 'N/A')}
   • Estimated Cost: ${damage_assessment.get('estimated_cost', 'N/A')}
   • Repair Duration: {damage_assessment.get('repair_days', 'N/A')} days

This claim has been automatically generated by the AI
Accident Detection System based on real-time analysis.

Supporting evidence (images/video) attached.

═══════════════════════════════════════════════════════
        """
        
        print(f"📋 Insurance claim generated: ACC-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        print(f"📊 Damage Assessment: {damage_assessment.get('level', 'N/A')}")
        
        return claim_data


# Create global alert system instance
alert_system = AlertSystem()


def send_emergency_alert(accident_data, image_path=None, video_path=None):
    """Convenience function to send emergency alert"""
    alert_system.send_accident_alert(accident_data, image_path, video_path)


def send_family_notification(accident_data):
    """Convenience function to notify family members"""
    alert_system.send_nominee_alert(accident_data)


if __name__ == "__main__":
    # Test the alert system
    test_data = {
        "severity": "HIGH",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "address": "Chennai, Tamil Nadu, India",
        "impact_score": 85,
        "vehicles_count": 2,
        "iou": 0.65,
        "vehicle_types": ["Car", "Truck"],
        "number_plate": "TN01AB1234",
        "speed": 45,
        "weather": "Clear",
        "temperature": 32,
        "visibility": "Good",
        "nearest_hospital": "Apollo Hospital",
        "hospital_distance": 2.5,
        "nearest_police": "Adyar Police Station",
        "police_distance": 1.8
    }
    
    print("🧪 Testing Alert System...")
    alert_system.send_accident_alert(test_data)
    print("✅ Test complete!")
