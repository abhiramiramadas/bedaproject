# ==========================================================
# Audio Alert System - Sound notifications for accidents
# ==========================================================

import os
import threading
import logging

logger = logging.getLogger(__name__)

# Windows audio support
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

# Text-to-speech support
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


class AudioAlertSystem:
    """
    Audio alert system for accident notifications
    Supports both system sounds and text-to-speech
    """
    
    def __init__(self):
        self.tts_engine = None
        self.is_speaking = False
        self._init_tts()
    
    def _init_tts(self):
        """Initialize text-to-speech engine"""
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)  # Speed
                self.tts_engine.setProperty('volume', 1.0)  # Volume
                
                # Try to set a clear voice
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                
                logger.info("Text-to-speech engine initialized")
            except Exception as e:
                logger.warning(f"Could not initialize TTS: {e}")
                self.tts_engine = None
    
    def play_alert_sound(self, severity="MEDIUM"):
        """
        Play an alert sound based on severity
        
        Args:
            severity: Accident severity level (CRITICAL, HIGH, MEDIUM, LOW)
        """
        if not WINSOUND_AVAILABLE:
            logger.warning("Windows sound not available")
            return
        
        def _play():
            try:
                if severity == "CRITICAL":
                    # Critical: Long continuous alarm
                    for _ in range(5):
                        winsound.Beep(1000, 300)  # High pitch
                        winsound.Beep(600, 300)   # Low pitch
                elif severity == "HIGH":
                    # High: Rapid beeps
                    for _ in range(4):
                        winsound.Beep(800, 200)
                        winsound.Beep(0, 100)
                elif severity == "MEDIUM":
                    # Medium: Standard alert
                    for _ in range(3):
                        winsound.Beep(700, 300)
                        winsound.Beep(0, 200)
                else:
                    # Low: Single notification
                    winsound.Beep(500, 500)
            except Exception as e:
                logger.error(f"Sound error: {e}")
        
        # Play in background thread
        thread = threading.Thread(target=_play)
        thread.daemon = True
        thread.start()
    
    def play_system_sound(self, sound_type="exclamation"):
        """
        Play a Windows system sound
        
        Args:
            sound_type: Type of sound (exclamation, hand, question, asterisk)
        """
        if not WINSOUND_AVAILABLE:
            return
        
        sound_map = {
            "exclamation": winsound.MB_ICONEXCLAMATION,
            "hand": winsound.MB_ICONHAND,
            "question": winsound.MB_ICONQUESTION,
            "asterisk": winsound.MB_ICONASTERISK,
            "default": winsound.MB_OK
        }
        
        try:
            winsound.MessageBeep(sound_map.get(sound_type, winsound.MB_OK))
        except:
            pass
    
    def speak(self, text):
        """
        Speak text using text-to-speech
        
        Args:
            text: Text to speak
        """
        if not self.tts_engine or self.is_speaking:
            return
        
        def _speak():
            self.is_speaking = True
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS error: {e}")
            finally:
                self.is_speaking = False
        
        thread = threading.Thread(target=_speak)
        thread.daemon = True
        thread.start()
    
    def announce_accident(self, accident_data):
        """
        Make a full accident announcement
        
        Args:
            accident_data: Dictionary with accident information
        """
        severity = accident_data.get('severity', 'UNKNOWN')
        vehicles = accident_data.get('vehicle_types', ['vehicles'])
        
        # Play alert sound first
        self.play_alert_sound(severity)
        
        # Build announcement
        vehicle_text = " and ".join(vehicles) if vehicles else "vehicles"
        
        if severity == "CRITICAL":
            message = f"Critical accident detected! {vehicle_text} involved. Emergency services required immediately."
        elif severity == "HIGH":
            message = f"Serious accident detected involving {vehicle_text}. Please respond immediately."
        elif severity == "MEDIUM":
            message = f"Accident detected. {vehicle_text} involved. Please check the situation."
        else:
            message = f"Minor collision detected between {vehicle_text}."
        
        # Speak after a short delay (let alert sound finish)
        def _delayed_speak():
            import time
            time.sleep(1.5)
            self.speak(message)
        
        thread = threading.Thread(target=_delayed_speak)
        thread.daemon = True
        thread.start()
    
    def test_audio(self):
        """Test the audio system"""
        print("Testing audio system...")
        
        if WINSOUND_AVAILABLE:
            print("  - Windows sound: Available")
            self.play_system_sound("asterisk")
        else:
            print("  - Windows sound: Not available")
        
        if TTS_AVAILABLE and self.tts_engine:
            print("  - Text-to-speech: Available")
            self.speak("Audio system test successful")
        else:
            print("  - Text-to-speech: Not available")


# Global instance
audio_alert = AudioAlertSystem()


def alert_accident(accident_data):
    """
    Convenience function for accident alerts
    
    Args:
        accident_data: Accident information dictionary
    """
    audio_alert.announce_accident(accident_data)


def play_sound(severity="MEDIUM"):
    """
    Convenience function to play alert sound
    
    Args:
        severity: Accident severity level
    """
    audio_alert.play_alert_sound(severity)


def speak_alert(text):
    """
    Convenience function for TTS
    
    Args:
        text: Text to speak
    """
    audio_alert.speak(text)


# Test when run directly
if __name__ == "__main__":
    audio_alert.test_audio()
    
    # Test accident alert
    test_data = {
        "severity": "HIGH",
        "vehicle_types": ["Car", "Motorcycle"]
    }
    
    print("\nTesting accident alert...")
    alert_accident(test_data)
    
    # Keep alive for audio to play
    import time
    time.sleep(5)
