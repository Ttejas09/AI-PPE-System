import cv2
import time
import torch
import numpy as np
from ultralytics import YOLO
import supervision as sv
from logic import check_compliance

# --- CONFIGURATION ---
# UPDATE THIS with your actual path!
MODEL_PATH = 'D:\\ML_Work\\DataPrep\\runs\\detect\\ppe_model_v13\\weights\\best.pt' 
POSE_MODEL_PATH = 'yolov8n-pose.pt'

def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"🚀 Starting AI Safety Monitor on: {device.upper()}")

    try:
        model = YOLO(MODEL_PATH)
        pose_model = YOLO(POSE_MODEL_PATH)
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    fps_start = time.time()
    fps_cnt = 0
    fps_disp = 0

    print("✅ System Ready. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret: break

        # 1. Inference (Low confidence threshold globally, filtered later)
        results_gear = model(frame, verbose=False, conf=0.15, device=device)[0]
        results_pose = pose_model(frame, verbose=False, conf=0.5, device=device)[0]

        detections_gear = sv.Detections.from_ultralytics(results_gear)

        if results_pose.keypoints is not None:
            keypoints_all = results_pose.keypoints.xy.cpu().numpy()
            boxes_all = results_pose.boxes.xyxy.cpu().numpy()
            
            for i, keypoints in enumerate(keypoints_all):
                person_box = boxes_all[i]
                
                # --- SMART FILTERING (UPDATED) ---
                gear_list = []
                for j, class_id in enumerate(detections_gear.class_id):
                    conf = detections_gear.confidence[j]
                    
                    # Rule 1: High confidence (0.5) ONLY for strong classes (Person, Helmet)
                    if class_id in [0, 1] and conf < 0.5:
                        continue
                    
                    # Rule 2: Low confidence (0.25) for weak classes (Vest, Goggles, Boots)
                    # We added Class 2 (Vest) here!
                    if class_id in [2, 3, 4, 5] and conf < 0.25:
                        continue
                        
                    gear_list.append({'class_id': int(class_id), 'bbox': detections_gear.xyxy[j]})

                # Run Logic
                compliance = check_compliance(person_box, keypoints, gear_list)
                
                # Draw
                is_safe = compliance['is_compliant']
                color = (0, 255, 0) if is_safe else (0, 0, 255)
                x1, y1, x2, y2 = map(int, person_box)
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Status Text
                label = "SAFE" if is_safe else "VIOLATION"
                if not is_safe:
                    missing = ",".join(compliance['missing_gear'])
                    if missing: label += f" [Miss: {missing}]"
                    if compliance['violations']: label += f" !{' '.join(compliance['violations'])}"

                # Draw Label
                (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(frame, (x1, y1 - 25), (x1 + w + 10, y1), color, -1)
                cv2.putText(frame, label, (x1 + 5, y1 - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # DEBUG: Draw Boots (Blue Box) & Goggles (Yellow Box) to verify detection
                for g in gear_list:
                    gx1, gy1, gx2, gy2 = map(int, g['bbox'])
                    if g['class_id'] == 4: # Boots
                        cv2.rectangle(frame, (gx1, gy1), (gx2, gy2), (255, 0, 0), 2)
                    if g['class_id'] == 3: # Goggles
                        cv2.rectangle(frame, (gx1, gy1), (gx2, gy2), (0, 255, 255), 2)

        # FPS
        fps_cnt += 1
        if (time.time() - fps_start) > 1:
            fps_disp = fps_cnt
            fps_cnt = 0
            fps_start = time.time()
        
        cv2.putText(frame, f"FPS: {fps_disp}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow("AI Safety Monitor", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()