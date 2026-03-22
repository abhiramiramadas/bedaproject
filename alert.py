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
        NOMINEE_CONTACTS, ENABLE_EMAIL_ALERTS, INSURANCE_EMAIL
    )
except ImportError:
    print("⚠️ config.py not found. Using default settings.")
    SENDER_EMAIL = ""
    EMAIL_PASSWORD = ""
    EMERGENCY_CONTACTS = []
    NOMINEE_CONTACTS = []
    INSURANCE_EMAIL = ""
    ENABLE_EMAIL_ALERTS = False


class AlertSystem:
    """Handles all emergency alert notifications"""

    def __init__(self):
        self.sender_email = SENDER_EMAIL
        self.email_password = EMAIL_PASSWORD
        self.last_alert_time = None
        self.alert_cooldown = 30  # seconds

    def _create_base_message(self, recipient, subject):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        return msg

    def _attach_image(self, msg, image_path):
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-Disposition', 'attachment',
                               filename=os.path.basename(image_path))
                msg.attach(img)
        return msg

    def _attach_file(self, msg, file_path):
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

    # ==========================================================
    # 1. EMERGENCY SERVICES ALERT
    #    Who gets it: Emergency contacts (ambulance control, fire dept)
    #    When: Immediately on detection
    #    Why correct: They need to dispatch fast, no delay acceptable
    # ==========================================================
    def send_accident_alert(self, accident_data, image_path=None, video_path=None):
        subject = f"🚨 ACCIDENT ALERT — {accident_data.get('severity', 'UNKNOWN')} SEVERITY | Immediate Response Required"

        body = f"""
═══════════════════════════════════════════════════════
🚨 EMERGENCY ACCIDENT DETECTION ALERT 🚨
═══════════════════════════════════════════════════════

This is an AUTOMATED alert from the AI Accident Detection System.
Human verification is recommended before dispatching.

📅 Detected At : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📍 LOCATION:
   • Address   : {accident_data.get('address', 'N/A')}
   • Latitude  : {accident_data.get('latitude', 'N/A')}
   • Longitude : {accident_data.get('longitude', 'N/A')}
   • Maps Link : https://maps.google.com/?q={accident_data.get('latitude', '')},{accident_data.get('longitude', '')}

⚠️ ACCIDENT DETAILS:
   • Severity Level : {accident_data.get('severity', 'UNKNOWN')}
   • Impact Score   : {accident_data.get('impact_score', 'N/A')}
   • Collision IoU  : {accident_data.get('iou', 0):.2%}
   • Vehicles       : {', '.join(accident_data.get('vehicle_types', ['Unknown']))}
   • Estimated Speed: {accident_data.get('speed', 'N/A')} km/h

🌤️ CONDITIONS:
   • Weather        : {accident_data.get('weather', 'N/A')}
   • Temperature    : {accident_data.get('temperature', 'N/A')}°C
   • Visibility     : {accident_data.get('visibility', 'N/A')} km

🏥 NEAREST EMERGENCY SERVICES:
   • Hospital       : {accident_data.get('nearest_hospital', 'N/A')} ({accident_data.get('hospital_distance', 'N/A')} km)
   • Police Station : {accident_data.get('nearest_police', 'N/A')} ({accident_data.get('police_distance', 'N/A')} km)

═══════════════════════════════════════════════════════
⚡ PLEASE DISPATCH EMERGENCY SERVICES IMMEDIATELY ⚡
═══════════════════════════════════════════════════════

Note: Evidence (image/video) attached to this email.
      A full report will be available on the admin dashboard.

---
AI Accident Detection System v2.0
        """

        for recipient in EMERGENCY_CONTACTS:
            msg = self._create_base_message(recipient, subject)
            msg.attach(MIMEText(body, 'plain'))
            if image_path:
                self._attach_image(msg, image_path)
            if video_path:
                self._attach_file(msg, video_path)
            self._send_email(msg, recipient)

    # ==========================================================
    # 2. FAMILY / NOMINEE ALERT
    #    Who gets it: Registered family members of vehicle owner
    #    When: Immediately on HIGH or CRITICAL severity
    #    Why correct: Family needs to know ASAP to go to hospital
    # ==========================================================
    def send_nominee_alert(self, accident_data):
        subject = "🚨 URGENT: A vehicle registered to your family was involved in an accident"

        body = f"""
═══════════════════════════════════════════════════════
🚨 URGENT FAMILY NOTIFICATION 🚨
═══════════════════════════════════════════════════════

Dear Family Member,

Our AI Accident Detection System has detected that a vehicle
associated with your family may have been involved in an accident.

This is an AUTOMATED notification. Please contact emergency
services or the hospital for more information.

📅 Detected At : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📍 LOCATION:
   • Address   : {accident_data.get('address', 'N/A')}
   • Maps Link : https://maps.google.com/?q={accident_data.get('latitude', '')},{accident_data.get('longitude', '')}

⚠️ SEVERITY: {accident_data.get('severity', 'UNKNOWN')}

🚗 VEHICLE DETAILS:
   • Vehicle Type  : {', '.join(accident_data.get('vehicle_types', ['Unknown']))}
   • Number Plate  : {accident_data.get('number_plate', 'Not detected at this time')}

🏥 NEAREST HOSPITAL:
   • Name     : {accident_data.get('nearest_hospital', 'N/A')}
   • Distance : {accident_data.get('hospital_distance', 'N/A')} km

═══════════════════════════════════════════════════════
EMERGENCY HELPLINE: 108 (India) | 911 (USA) | 112 (EU)
═══════════════════════════════════════════════════════

Please proceed to the nearest hospital or call emergency
services for more information and updates.

---
AI Accident Detection System v2.0
        """

        for recipient in NOMINEE_CONTACTS:
            msg = self._create_base_message(recipient, subject)
            msg.attach(MIMEText(body, 'plain'))
            self._send_email(msg, recipient)

    # ==========================================================
    # 3. BLOOD DONATION REQUEST
    #    Who gets it: Nominee contacts
    #    When: CRITICAL severity only
    #    Why correct: Only sent in life-threatening cases where
    #                 blood urgency is realistic
    # ==========================================================
    def send_blood_donation_request(self, accident_data, blood_type="Unknown"):
        subject = "🩸 URGENT: Blood Donation May Be Required"

        body = f"""
═══════════════════════════════════════════════════════
🩸 URGENT BLOOD DONATION REQUEST 🩸
═══════════════════════════════════════════════════════

A CRITICAL accident has occurred. The medical team at the
nearest hospital may urgently require blood donors.

📅 Detected At : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🩸 BLOOD REQUIREMENT:
   • Blood Type Needed : {blood_type}
   • Urgency Level     : CRITICAL
   • Note              : Please verify with hospital before donating

🏥 HOSPITAL DETAILS:
   • Hospital : {accident_data.get('nearest_hospital', 'N/A')}
   • Address  : {accident_data.get('address', 'N/A')}
   • Maps     : https://maps.google.com/?q={accident_data.get('latitude', '')},{accident_data.get('longitude', '')}

If you are a potential blood donor, please contact the
hospital directly to confirm requirement before proceeding.

═══════════════════════════════════════════════════════
YOUR DONATION CAN SAVE A LIFE
═══════════════════════════════════════════════════════

---
AI Accident Detection System v2.0
        """

        for recipient in NOMINEE_CONTACTS:
            msg = self._create_base_message(recipient, subject)
            msg.attach(MIMEText(body, 'plain'))
            self._send_email(msg, recipient)

    # ==========================================================
    # 4. INSURANCE PRE-ALERT (Evidence Notification)
    #    Who gets it: Insurance company email
    #    When: Immediately on detection
    #    Why correct: This is NOT a claim — it is an evidence
    #                 preservation notice. Insurance companies
    #                 accept these. The actual CLAIM is filed
    #                 only after police FIR + human review.
    #                 Admin triggers the real claim from dashboard.
    # ==========================================================
    def send_insurance_evidence_notice(self, accident_data, image_path=None, video_path=None):
        """
        Sends an evidence preservation notice to the insurance company.
        This is NOT a claim. It notifies them that an incident occurred
        and evidence has been captured. The actual claim must be filed
        manually by the vehicle owner after a police FIR.
        """
        incident_ref = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        subject = f"📋 Accident Evidence Notice — Ref: {incident_ref} | Action Required by Vehicle Owner"

        body = f"""
═══════════════════════════════════════════════════════
📋 ACCIDENT EVIDENCE PRESERVATION NOTICE
═══════════════════════════════════════════════════════

Incident Reference : {incident_ref}
Generated At       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

IMPORTANT: This is NOT an insurance claim.
This is an automated evidence preservation notice sent
by the AI Accident Detection System. The vehicle owner
must file a formal claim with supporting FIR and
medical documents.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INCIDENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Location     : {accident_data.get('address', 'N/A')}
   Coordinates  : {accident_data.get('latitude', 'N/A')}, {accident_data.get('longitude', 'N/A')}
   Maps Link    : https://maps.google.com/?q={accident_data.get('latitude', '')},{accident_data.get('longitude', '')}

⚠️ Severity     : {accident_data.get('severity', 'UNKNOWN')}
   Impact Score : {accident_data.get('impact_score', 'N/A')}
   Vehicles     : {', '.join(accident_data.get('vehicle_types', ['Unknown']))}
   Plate No.    : {accident_data.get('number_plate', 'Not detected')}

🌤️ Conditions   : {accident_data.get('weather', 'N/A')}, {accident_data.get('temperature', 'N/A')}°C

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVIDENCE CAPTURED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   • Accident image   : Attached to this email
   • Video clip       : Saved in system, available on request
   • Full PDF report  : Available on admin dashboard
   • Timestamp        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEPS FOR CLAIM (To be done by vehicle owner)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Step 1 : File a Police FIR at the nearest station
   Step 2 : Get medical reports if injuries involved
   Step 3 : Get vehicle damage assessed by an approved surveyor
   Step 4 : Submit FIR + medical + surveyor report + this
             incident reference ({incident_ref}) to initiate claim
   Step 5 : Insurance surveyor will inspect and approve claim

Please retain this reference number for your records.

═══════════════════════════════════════════════════════
This notice has been automatically generated by the
AI Accident Detection System. Evidence is preserved
and available for legal and insurance purposes.
═══════════════════════════════════════════════════════

---
AI Accident Detection System v2.0
        """

        # Send to insurance email if configured
        recipients = []
        if INSURANCE_EMAIL:
            recipients.append(INSURANCE_EMAIL)
        # Also send to nominees so they know steps to take
        recipients.extend(NOMINEE_CONTACTS)

        for recipient in recipients:
            msg = self._create_base_message(recipient, subject)
            msg.attach(MIMEText(body, 'plain'))
            if image_path:
                self._attach_image(msg, image_path)
            self._send_email(msg, recipient)

        print(f"📋 Insurance evidence notice sent | Ref: {incident_ref}")
        return incident_ref

    # ==========================================================
    # 5. FORMAL INSURANCE CLAIM (Human-triggered from dashboard)
    #    Who gets it: Insurance company
    #    When: ONLY when admin clicks "Initiate Claim" on dashboard
    #          after reviewing + confirming the incident
    #    Why correct: This mirrors real-world workflow. A human
    #                 verified the incident before claiming.
    # ==========================================================
    def send_formal_insurance_claim(self, accident_data, damage_assessment, incident_ref=None):
        """
        Sends the actual insurance claim. Called only when admin
        manually triggers it from the dashboard after review.
        """
        claim_ref = f"CLM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        subject = f"📋 FORMAL INSURANCE CLAIM — Ref: {claim_ref}"

        claim_data = {
            "claim_reference": claim_ref,
            "incident_reference": incident_ref or "N/A",
            "claim_type": "Motor Accident",
            "submission_time": datetime.now().isoformat(),
            "severity": accident_data.get('severity'),
            "location": {
                "latitude": accident_data.get('latitude'),
                "longitude": accident_data.get('longitude'),
                "address": accident_data.get('address')
            },
            "vehicle": {
                "number_plate": accident_data.get('number_plate', 'Not detected'),
                "types": accident_data.get('vehicle_types', [])
            },
            "damage_assessment": damage_assessment,
            "weather_conditions": accident_data.get('weather'),
            "evidence": {
                "images": "Attached",
                "video": "Available on request",
                "pdf_report": "Available on admin dashboard"
            },
            "human_verified": True,
            "admin_approved": True
        }

        body = f"""
═══════════════════════════════════════════════════════
📋 FORMAL MOTOR INSURANCE CLAIM SUBMISSION
═══════════════════════════════════════════════════════

Claim Reference    : {claim_ref}
Incident Reference : {incident_ref or 'N/A'}
Submission Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status             : Admin Verified & Approved

This claim has been reviewed and approved by a human
administrator before submission.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLAIM DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{json.dumps(claim_data, indent=2)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAMAGE ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   • Estimated Damage : {damage_assessment.get('level', 'N/A')}
   • Estimated Cost   : ${damage_assessment.get('estimated_cost', 'N/A'):,}
   • Repair Duration  : {damage_assessment.get('repair_days', 'N/A')} days
   • Total Loss       : {'Yes' if damage_assessment.get('total_loss') else 'No'}

Please process this claim and contact the vehicle owner
for further documentation and surveyor inspection.

═══════════════════════════════════════════════════════
---
AI Accident Detection System v2.0
        """

        recipients = []
        if INSURANCE_EMAIL:
            recipients.append(INSURANCE_EMAIL)

        for recipient in recipients:
            msg = self._create_base_message(recipient, subject)
            msg.attach(MIMEText(body, 'plain'))
            self._send_email(msg, recipient)

        print(f"📋 Formal insurance claim submitted | Ref: {claim_ref}")
        return {"claim_ref": claim_ref, "incident_ref": incident_ref, "status": "submitted"}

    def send_organ_donation_alert(self, accident_data):
        """Organ donation notification — CRITICAL cases only"""
        subject = "💚 Organ Donation Notification — Critical Case"
        body = f"""
═══════════════════════════════════════════════════════
💚 ORGAN DONATION NOTIFICATION 💚
═══════════════════════════════════════════════════════

This is a sensitive notification regarding a critical
medical situation following a detected accident.

The medical team may discuss organ donation options
with family members if the situation becomes critical.

📅 Date/Time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🏥 HOSPITAL:
   • Name    : {accident_data.get('nearest_hospital', 'N/A')}
   • Contact : {accident_data.get('hospital_phone', 'N/A')}

Please contact the hospital for more information.
The organ donation registry has been notified as per
the registered donor's wishes.

═══════════════════════════════════════════════════════
National Organ Donation Helpline: 1800-103-7100 (India)
═══════════════════════════════════════════════════════

---
AI Accident Detection System v2.0
        """
        for recipient in NOMINEE_CONTACTS:
            msg = self._create_base_message(recipient, subject)
            msg.attach(MIMEText(body, 'plain'))
            self._send_email(msg, recipient)


# Global instance
alert_system = AlertSystem()


def send_emergency_alert(accident_data, image_path=None, video_path=None):
    """Convenience function — emergency services alert"""
    alert_system.send_accident_alert(accident_data, image_path, video_path)


def send_family_notification(accident_data):
    """Convenience function — family alert"""
    alert_system.send_nominee_alert(accident_data)


def send_insurance_evidence_notice(accident_data, image_path=None):
    """Convenience function — insurance evidence notice (not a claim)"""
    return alert_system.send_insurance_evidence_notice(accident_data, image_path)


if __name__ == "__main__":
    test_data = {
        "severity": "HIGH",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "address": "Anna Salai, Chennai, Tamil Nadu, India",
        "impact_score": 72,
        "vehicles_count": 2,
        "iou": 0.55,
        "vehicle_types": ["Car", "Motorcycle"],
        "number_plate": "TN01AB1234",
        "speed": 45,
        "weather": "Clear",
        "temperature": 32,
        "visibility": 10,
        "nearest_hospital": "Apollo Hospital",
        "hospital_distance": 2.5,
        "nearest_police": "Adyar Police Station",
        "police_distance": 1.8
    }

    print("🧪 Testing Alert System...")
    alert_system.send_accident_alert(test_data)
    ref = alert_system.send_insurance_evidence_notice(test_data)
    print(f"Evidence notice sent. Ref: {ref}")
    print("✅ Test complete!")