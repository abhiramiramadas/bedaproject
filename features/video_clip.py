# ==========================================================
# Video Clip Saver - Saves accident video clips
# ==========================================================

import cv2
import os
import threading
from collections import deque
from datetime import datetime


class VideoClipSaver:
    """
    Saves video clips around accident events
    Maintains a rolling buffer of frames before the accident
    and captures frames after the accident
    """
    
    def __init__(self, buffer_seconds=5, after_seconds=5, output_dir="uploads/clips"):
        """
        Initialize the video clip saver
        
        Args:
            buffer_seconds: Seconds of video to save before accident
            after_seconds: Seconds of video to save after accident
            output_dir: Directory to save clips
        """
        self.buffer_seconds = buffer_seconds
        self.after_seconds = after_seconds
        self.output_dir = output_dir
        self.frame_buffer = deque()
        self.fps = 30  # Will be updated from video
        self.is_recording = False
        self.recording_frames = []
        self.frames_to_capture = 0
        
        os.makedirs(output_dir, exist_ok=True)
    
    def set_fps(self, fps):
        """Set the FPS for buffer size calculation"""
        self.fps = max(fps, 15)  # Minimum 15 FPS
        max_buffer_size = self.fps * self.buffer_seconds
        self.frame_buffer = deque(maxlen=max_buffer_size)
    
    def add_frame(self, frame):
        """
        Add a frame to the rolling buffer
        
        Args:
            frame: OpenCV frame (BGR)
        """
        # Add to rolling buffer
        self.frame_buffer.append(frame.copy())
        
        # If recording, add to recording buffer
        if self.is_recording:
            self.recording_frames.append(frame.copy())
            self.frames_to_capture -= 1
            
            if self.frames_to_capture <= 0:
                self._finish_recording()
    
    def trigger_save(self, accident_data=None):
        """
        Trigger saving a video clip
        Called when an accident is detected
        
        Args:
            accident_data: Optional accident information for filename
        """
        if self.is_recording:
            return None  # Already recording
        
        self.is_recording = True
        self.frames_to_capture = self.fps * self.after_seconds
        
        # Copy buffer frames to recording
        self.recording_frames = list(self.frame_buffer)
        self.current_accident_data = accident_data
        
        return True
    
    def _finish_recording(self):
        """Finish recording and save the clip"""
        self.is_recording = False
        
        if len(self.recording_frames) < 10:
            self.recording_frames = []
            return
        
        # Save in background thread
        frames = self.recording_frames.copy()
        accident_data = getattr(self, 'current_accident_data', None)
        self.recording_frames = []
        
        thread = threading.Thread(
            target=self._save_clip,
            args=(frames, accident_data)
        )
        thread.daemon = True
        thread.start()
    
    def _save_clip(self, frames, accident_data=None):
        """Save the video clip to disk"""
        if not frames:
            return
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        severity = accident_data.get('severity', 'UNKNOWN') if accident_data else 'UNKNOWN'
        filename = f"accident_clip_{severity}_{timestamp}.mp4"
        filepath = os.path.join(self.output_dir, filename)
        
        # Get frame dimensions
        height, width = frames[0].shape[:2]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(filepath, fourcc, self.fps, (width, height))
        
        # Add timestamp overlay to frames
        for i, frame in enumerate(frames):
            # Add frame number
            cv2.putText(frame, f"Frame: {i+1}/{len(frames)}", 
                       (10, height - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Add accident marker at the buffer point
            buffer_frames = self.fps * self.buffer_seconds
            if i == min(buffer_frames, len(frames) - 1):
                cv2.putText(frame, ">> ACCIDENT POINT <<",
                           (width // 2 - 100, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            writer.write(frame)
        
        writer.release()
        
        print(f"Video clip saved: {filepath}")
        print(f"  Duration: {len(frames) / self.fps:.1f}s | Frames: {len(frames)}")
        
        return filepath


# Global instance
clip_saver = VideoClipSaver()


def save_accident_clip(frame, accident_data=None):
    """
    Convenience function to save accident clip
    
    Args:
        frame: Current frame (not used directly, but for API consistency)
        accident_data: Accident information
    
    Returns:
        True if recording started, None if already recording
    """
    return clip_saver.trigger_save(accident_data)


def add_frame_to_buffer(frame, fps=30):
    """
    Add frame to rolling buffer
    
    Args:
        frame: OpenCV frame
        fps: Video FPS for buffer calculation
    """
    clip_saver.set_fps(fps)
    clip_saver.add_frame(frame)
