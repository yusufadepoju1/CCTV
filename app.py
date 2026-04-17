from flask import Flask, render_template, Response, jsonify
from camera import VideoCamera
from database import get_recent_intrusions, init_db, get_config, update_config
import os
import werkzeug.utils
import json

app = Flask(__name__)

# To avoid starting multiple cameras if hot-reloading
camera_instance = None

def get_camera():
    global camera_instance
    if camera_instance is None:
        cfg = get_config()
        src = cfg.get('video_source', 'sample.mp4')
        poly = cfg.get('polygon_points')
        try:
            camera_instance = VideoCamera(src, poly)
        except Exception as e:
            print(f"Fallback to webcam... {e}")
            camera_instance = VideoCamera(0, poly)
            
    # Always ensure polygon is most up to date from DB without restarting feed if possible
    # (Though we mainly update it via API now)
    return camera_instance

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    import time
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            time.sleep(0.1)  # Prevent infinite tight loop if camera fails

@app.route('/video_feed')
def video_feed():
    cam = get_camera()
    return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/history')
def history():
    intrusions = get_recent_intrusions(limit=20)
    return jsonify(intrusions)

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    from flask import request
    global camera_instance
    if request.method == 'GET':
        return jsonify(get_config())
    else:
        # POST
        data = request.json
        new_source = data.get('video_source')
        new_polygon = data.get('polygon_points')
        if new_source is not None:
            update_config(video_source=new_source)
            # Re-init camera on next frame
            camera_instance = None
        if new_polygon is not None:
            update_config(polygon_points=new_polygon)
            if camera_instance:
                camera_instance.update_polygon(new_polygon)
        return jsonify({"status": "success"})

@app.route('/api/upload_video', methods=['POST'])
def upload_video():
    from flask import request
    global camera_instance
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    upload_dir = 'static/uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    filename = werkzeug.utils.secure_filename(file.filename)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    
    # Update config
    update_config(video_source=filepath)
    camera_instance = None # reset camera to use new source
    return jsonify({"status": "success", "file": filepath})

if __name__ == '__main__':
    # Initialize the database
    init_db()
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=False)

