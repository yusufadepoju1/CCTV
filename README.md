# SecureVision AI: CCTV Intrusion Detection System
A complete, end-to-end AI security system built with Python, OpenCV, YOLOv8, and Flask. It provides a real-time responsive dashboard to monitor live camera feeds, dynamically define custom restricted polygon areas, and automatically record intrusions to an SQLite database. 

## Features

*   **YOLOv8 Object Detection**: Uses cutting-edge AI via the `ultralytics` library to instantly recognize people in real-time.
*   **Dynamic Custom Polygons**: Features an HTML5 Canvas interface directly on the dashboard where you can click to draw your own custom protection boundary over the video feed.
*   **Live Stream Backend**: Decoupled MJPEG video streaming via Flask, capable of handling local laptop webcams or uploaded MP4 sample videos.
*   **Database Logging**: Intrusions automatically trigger a snapshot and are recorded into an SQLite `intrusions.db`.
*   **Premium Dark UI**: Glassmorphism aesthetic featuring pulsing micro-animations and lightbox screenshot review.

---

##  Local Installation & Usage

### 1. Prerequisites
Ensure you have Python 3.8+ installed.

```bash
# It is recommended to use a virtual environment
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

### 4. Access the Dashboard
Open your web browser and navigate to:
**http://127.0.0.1:5000**

---

