import cv2
import time
import torch
import os
import supervision as sv
from ultralytics import YOLO
from datetime import datetime
from models import SessionLocal, Log
from logic import check_compliance 

class SafetyEngine:
    def __init__(self, model_path, pose_path, source):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Loading models on {self.device}...")
        
        # Load Your Models
        self.model = YOLO(model_path)
        self.pose_model = YOLO(pose_path)
        
        # Video Capture
        self.cap = cv2.VideoCapture(source)
        
        # Tracking & Annotation
        self.tracker = sv.ByteTrack()
        self.box_annotator = sv.BoxAnnotator()
        self.last_log_time = {} # Throttle logs (1 per 5s per worker)

    def log_to_db(self, worker_id, violations, frame):
        """Saves violation to SQLite and Image file"""
        now = time.time()
        
        # Prevent spamming: Only log same worker every 5 seconds
        if worker_id in self.last_log_time:
            if now - self.last_log_time[worker_id] < 5:
                return

        self.last_log_time[worker_id] = now
        
        # 1. Save Image
        os.makedirs("alerts", exist_ok=True)
        filename = f"alerts/Worker{worker_id}_{int(now)}.jpg"
        cv2.imwrite(filename, frame)

        # 2. Save to DB
        db = SessionLocal()
        new_log = Log(
            worker_id=f"Worker {worker_id}",
            violation=",".join(violations),
            snapshot_path=filename
        )
        db.add(new_log)
        db.commit()
        db.close()
        print(f"[DB] Logged violation for Worker {worker_id}")

    def generate_frames(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                # Loop video for demo purposes
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # 1. Run Inference
            results_gear = self.model(frame, verbose=False, conf=0.15, device=self.device)[0]
            results_pose = self.pose_model(frame, verbose=False, conf=0.5, device=self.device)[0]

            # 2. Convert to Supervision Detections
            detections_gear = sv.Detections.from_ultralytics(results_gear)
            
            # 3. Track People (Class 0)
            # This assigns ID to people so we know "Worker 1" is "Worker 1"
            person_detections = detections_gear[detections_gear.class_id == 0]
            person_detections = self.tracker.update_with_detections(person_detections)

            if results_pose.keypoints is not None:
                keypoints_all = results_pose.keypoints.xy.cpu().numpy()
                boxes_all = results_pose.boxes.xyxy.cpu().numpy()

                # Iterate through detected poses (People)
                for i, keypoints in enumerate(keypoints_all):
                    person_box = boxes_all[i]
                    
                    # Match Pose to Tracker ID
                    # (Simple heuristic: use index `i` as ID for demo stability)
                    worker_id = i + 1 
                    
                    # --- SMART FILTERING (Your Custom Logic) ---
                    gear_list = []
                    for j, class_id in enumerate(detections_gear.class_id):
                        conf = detections_gear.confidence[j]
                        # High conf for Person/Helmet, Low for small gear
                        if class_id in [0, 1] and conf < 0.5: continue
                        if class_id in [2, 3, 4, 5] and conf < 0.25: continue
                        
                        gear_list.append({'class_id': int(class_id), 'bbox': detections_gear.xyxy[j]})

                    # --- COMPLIANCE CHECK ---
                    compliance = check_compliance(person_box, keypoints, gear_list)
                    is_safe = compliance['is_compliant']
                    
                    # Draw Visuals (Red/Green Boxes)
                    color = (0, 255, 0) if is_safe else (0, 0, 255)
                    x1, y1, x2, y2 = map(int, person_box)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    label = "SAFE" if is_safe else "VIOLATION"
                    
                    if not is_safe:
                        violations = compliance['missing_gear'] + compliance['violations']
                        label += f" [{','.join(violations)}]"
                        
                        # LOG TO DATABASE
                        self.log_to_db(worker_id, violations, frame)

                    # Draw Label Background & Text
                    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

            # Encode for Web Streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')