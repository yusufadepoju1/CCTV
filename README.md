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

## Configuration
Click the **Settings** tab in the navigation bar to configure the system:
1.  **Video Source**: Type `0` for your laptop webcam, or an `rtsp://...` URL for an IP CCTV camera. 
2.  **Upload Sample Video**: If you don't have a camera, use the uploader to supply an `.mp4` file representing the area you want to test!
3.  **Draw Restricted Area**: Click the UI button to overlay a drawing grid onto your camera feed. Click to define points, and hit save to immediately tell the AI what area is off-limits.

---

##  Deploying to Production (Cloud Servers like Render or Heroku)

It is **possible** to deploy this standard Flask app to Render, but running an AI Computer Vision app in the cloud has specific hardware constraints you need to know about:

### Crucial Changes Required Before Cloud Deployment:

1.  **Headless OpenCV**: Cloud servers don't have built-in Graphical UI libraries. You **must** change `opencv-python` to `opencv-python-headless` inside `requirements.txt`, or Render will crash during the build phase with a `libGL.so.1` missing error.
2.  **Add a WSGI Server**: Flask's built-in server is for development. Add `gunicorn` to your `requirements.txt`. In Render's build settings, set your start command to: `gunicorn app:app -w 1 --threads 4`. 
3.  **No Local Webcams**: Render's servers sit in a data center; they do not have webcams. Setting the source to `0` will fail. You must exclusively use uploaded MP4s or public RTSP IP camera links.
4.  **Ephemeral Disk Warning (CRITICAL)**: Render's free tier has an "ephemeral" filesystem. If the Render server restarts or goes to sleep, your `intrusions.db` and all saved `static/screenshots/` will be **wiped out forever**. To fix this, you either need a paid Render "Disk" allocation, or you must migrate from SQLite to an external database like Render PostgreSQL or Supabase, and save images to AWS S3. 

### Recommended Use Case
Because of bandwidth, latency, and hardware constraints, CCTV processing apps like this are overwhelmingly better suited to **running locally on an on-premise computer** (like a Raspberry Pi 5 or a local mini-PC) attached to the network rather than being deployed to the cloud!
