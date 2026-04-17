import cv2
import numpy as np
import time
import os
from ultralytics import YOLO
from database import add_intrusion

class VideoCamera:
    def __init__(self, video_source=0, polygon_points=None):
        # Initialize YOLOv8 model - downloads yolov8n.pt if not exists
        self.model = YOLO('yolov8n.pt')
        
        # Parse video source if it's digit string like "0"
        try:
            if str(video_source).isdigit():
                video_source = int(video_source)
        except:
            pass

        # Load video source
        self.video = cv2.VideoCapture(video_source)
        if not self.video.isOpened():
            print(f"Failed to open video source {video_source}")
            
        self.intrusion_cooldown = 5.0 # seconds
        self.last_intrusion_time = 0
        
        # Ensure screenshot dir exists
        self.screenshot_dir = os.path.join('static', 'screenshots')
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
            
        # Define the restricted polygon
        if polygon_points is not None:
            self.polygon = np.array(polygon_points, np.int32)
        else:
            self.polygon = np.array([[100, 480], [540, 480], [440, 250], [200, 250]], np.int32)
            
    def update_polygon(self, points):
        self.polygon = np.array(points, np.int32)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()
        if not ret:
            # If video ends (e.g., sample file), loop it
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.video.read()
            if not ret:
                return None
        
        # Resize for consistent processing and polygon mapping
        frame = cv2.resize(frame, (640, 480))
        
        # Run YOLOv8 inference, filtering for 'person' (class 0)
        results = self.model(frame, classes=[0], conf=0.4, verbose=False)
        
        intrusion_detected = False
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 165, 0), 2)
                cv2.putText(frame, "Person", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 2)
                
                # Calculate bottom center point
                bottom_center_x = int((x1 + x2) / 2)
                bottom_center_y = int(y2)
                
                # Draw the point
                cv2.circle(frame, (bottom_center_x, bottom_center_y), 5, (0, 0, 255), -1)
                
                # Check if point is inside polygon
                result = cv2.pointPolygonTest(self.polygon, (bottom_center_x, bottom_center_y), False)
                if result >= 0:
                    intrusion_detected = True
        
        # Draw polygon (Red if intrusion, otherwise Green)
        color = (0, 0, 255) if intrusion_detected else (0, 255, 0)
        cv2.polylines(frame, [self.polygon], isClosed=True, color=color, thickness=3)
        
        # Add a text warning if intrusion detected
        if intrusion_detected:
            cv2.putText(frame, "RESTRICTED AREA INTRUSION!", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            # Handle DB logging and screenshot
            current_time = time.time()
            if current_time - self.last_intrusion_time > self.intrusion_cooldown:
                self.last_intrusion_time = current_time
                timestamp_str = time.strftime("%Y%m%d_%H%M%S")
                filename = f"intrusion_{timestamp_str}.jpg"
                filepath = os.path.join(self.screenshot_dir, filename)
                
                # Save just the frame with drawings to disk
                cv2.imwrite(filepath, frame)
                
                # Add to DB (we just store the filename/path)
                try:
                    add_intrusion(f"screenshots/{filename}")
                except Exception as e:
                    print(f"DB Error: {e}")
        
        # Encode as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

