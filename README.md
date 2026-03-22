# 🚗💥 AiSeeYou — AI Road Accident Detection System

> *"What if traffic cameras had anxiety and started overthinking everything?"*

A real-time AI-powered road accident detection system that watches traffic footage so humans don't have to stare at CCTV like it's a Netflix thriller. Built for **traffic cameras**, not dashcams — because this system prefers to judge everyone equally from above.

---

## ✨ Features

| Category | Feature |
|---|---|
| **Detection** | YOLOv8 vehicle detection + frame-by-frame tracking |
| **Speed Estimation** | Pixel displacement-based speed calculation |
| **Collision Detection** | IoU overlap + centroid distance + temporal consistency (3-frame minimum) |
| **Severity Grading** | CRITICAL / HIGH / MEDIUM / LOW with impact scoring |
| **Web Dashboard** | Real-time stats, charts, video streaming, accident list |
| **Emergency Alerts** | Email notifications to emergency contacts & family |
| **Emergency Services** | Nearest hospitals, police, fire stations via OpenStreetMap |
| **Weather Data** | Live weather conditions at accident location |
| **PDF Reports** | Professional accident reports with all details |
| **Database** | SQLite storage for all accident records |
| **Excel Export** | Export accident data to styled Excel files |
| **Interactive Maps** | Folium-based maps with accident markers & heatmap |
| **Audio Alerts** | System sounds + text-to-speech announcements |
| **Video Clips** | Auto-save video clips of accident events |
| **Desktop GUI** | Tkinter-based GUI with live video & controls |

---

## 🏗️ Project Structure

```
ACC/
├── main.py                 # Entry point — CLI, API server, GUI launcher
├── detection.py            # Core: YOLO detection, tracking, collision logic
├── config.py               # API keys & thresholds (DO NOT COMMIT)
├── config.example.py       # Template config — copy to config.py
├── alert.py                # Email alert system
├── OSM.py                  # Emergency services locator + weather
├── haversine_gui.py        # Tkinter desktop GUI
├── requirements.txt        # Python dependencies
├── yolov8n.pt              # YOLO model weights
│
├── features/               # Modular optional features
│   ├── __init__.py
│   ├── video_clip.py       # Save accident video clips
│   ├── audio_alert.py      # Audio notifications
│   ├── pdf_report.py       # PDF report generator
│   ├── database.py         # SQLite accident storage
│   ├── excel_export.py     # Excel export
│   └── map_generator.py    # Interactive map generation
│
├── templates/
│   └── dashboard.html      # Web dashboard UI
│
├── data/
│   └── accidents.db        # SQLite database
│
└── uploads/                # Uploaded video files
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/AiSeeYou.git
cd AiSeeYou

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```bash
copy config.example.py config.py   # Windows
# cp config.example.py config.py   # Linux/Mac
```

Edit `config.py` with your API keys:
- **Gmail App Password** for email alerts
- **OpenWeatherMap API key** for weather data

### 3. Run

```bash
# Start the web dashboard (recommended)
python main.py --api

# Process a video file
python main.py --video path/to/video.mp4

# Live camera feed
python main.py --camera

# Desktop GUI
python main.py --gui

# Run tests
python main.py --test
```

Then open **http://127.0.0.1:5000** in your browser for the dashboard.

---

## 🧠 How Detection Works

```
Frame → YOLO Detection → Vehicle Tracking → Speed Estimation
                                                    ↓
                       Alert ← Severity Calc ← Collision Check
                                                    ↑
                                       IoU + Centroid Distance
                                     + Temporal Consistency (3 frames)
                                     + Minimum Speed Filter
```

1. **YOLOv8** detects vehicles (cars, trucks, buses, motorcycles, bicycles)
2. **Tracker** assigns IDs and follows vehicles across frames
3. **Speed estimator** calculates velocity from position history
4. **Collision detector** checks:
    - Bounding box overlap (IoU > 0.20)
    - Centroid distance (< 150 pixels)
    - Temporal consistency (overlap must persist for 3+ consecutive frames)
    - At least one vehicle must be moving (speed > 5 px/frame)
5. **Severity calculator** grades impact as CRITICAL/HIGH/MEDIUM/LOW

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Web dashboard |
| GET | `/health` | System health check |
| GET | `/api/stats` | Detection statistics |
| GET | `/api/accidents` | All accident records |
| GET | `/api/accidents/<id>` | Single accident detail |
| POST | `/api/upload` | Upload video for analysis |
| GET | `/video_feed` | Live video stream (MJPEG) |
| POST | `/api/start_camera` | Start live camera |
| POST | `/api/stop_camera` | Stop live camera |

---

## ⚙️ Configuration

Key settings in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `IOU_THRESHOLD_LOW` | 0.20 | Minimum IoU for collision |
| `CONSECUTIVE_FRAMES_THRESHOLD` | 3 | Frames of overlap before alert |
| `CENTROID_DISTANCE_THRESHOLD` | 150 | Max centroid distance (px) |
| `MIN_SPEED_FOR_ACCIDENT` | 5 | Min speed to filter parked cars |
| `ALERT_COOLDOWN_SECONDS` | 30 | Cooldown between alerts |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **YOLOv8** (Ultralytics) — object detection
- **OpenCV** — video processing
- **Flask** — REST API & web server
- **NumPy** — numerical operations
- **SQLite** — data persistence
- **ReportLab** — PDF generation
- **Folium** — interactive maps
- **OpenStreetMap** — emergency services lookup
- **OpenWeatherMap** — weather data

---

## 📄 License

This project is built for educational purposes as a final year project.

---

*Built with ❤️ and a healthy dose of machine learning anxiety.*
