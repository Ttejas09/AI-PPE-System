import numpy as np

def check_compliance(person_box, keypoints, gear_detections):
    """
    Determines if a person is compliant based on geometric logic.
    """
    
    # 1. Define Keypoint Indices (COCO Standard)
    NOSE = 0
    L_SHOULDER, R_SHOULDER = 5, 6
    L_WRIST, R_WRIST = 9, 10
    L_HIP, R_HIP = 11, 12
    L_ANKLE, R_ANKLE = 15, 16

    missing_gear = []
    violations = []
    
    # --- HELMET LOGIC (Class 1) ---
    helmet_worn = False
    helmet_carried = False
    helmets = [g for g in gear_detections if g['class_id'] == 1]
    
    head_y = keypoints[NOSE][1] if keypoints[NOSE][1] > 0 else person_box[1]
    
    for helmet in helmets:
        hx1, hy1, hx2, hy2 = helmet['bbox']
        helmet_center_y = (hy1 + hy2) / 2
        helmet_center_x = (hx1 + hx2) / 2
        
        if helmet_center_y < head_y + 40: 
            if person_box[0] < helmet_center_x < person_box[2]:
                helmet_worn = True
        
        l_wrist = keypoints[L_WRIST]
        r_wrist = keypoints[R_WRIST]
        if (l_wrist[0] > 0 and point_in_box(l_wrist, helmet['bbox'])) or \
           (r_wrist[0] > 0 and point_in_box(r_wrist, helmet['bbox'])):
            helmet_carried = True

    if not helmet_worn:
        missing_gear.append("Helmet")
        if helmet_carried:
            violations.append("Carrying Helmet")

    # --- VEST LOGIC (Class 2) ---
    vest_worn = False
    vests = [g for g in gear_detections if g['class_id'] == 2]
    
    if keypoints[L_SHOULDER][0] > 0 and keypoints[R_HIP][0] > 0:
        torso_box = [
            min(keypoints[L_SHOULDER][0], keypoints[R_SHOULDER][0]),
            min(keypoints[L_SHOULDER][1], keypoints[R_SHOULDER][1]),
            max(keypoints[L_HIP][0], keypoints[R_HIP][0]),
            max(keypoints[L_HIP][1], keypoints[R_HIP][1])
        ]
        for vest in vests:
            if calculate_iou(vest['bbox'], torso_box) > 0.05:
                vest_worn = True
                break
    else:
        for vest in vests:
            vy_center = (vest['bbox'][1] + vest['bbox'][3]) / 2
            if person_box[1] < vy_center < (person_box[1] + (person_box[3]-person_box[1])*0.6):
                vest_worn = True
                break

    if not vest_worn:
        missing_gear.append("Vest")

    # --- BOOT LOGIC (Class 4) ---
    if keypoints[L_ANKLE][0] > 0 or keypoints[R_ANKLE][0] > 0:
        boots_worn = False
        boots = [g for g in gear_detections if g['class_id'] == 4]
        
        ankles_x = [k[0] for k in [keypoints[L_ANKLE], keypoints[R_ANKLE]] if k[0] > 0]
        ankles_y = [k[1] for k in [keypoints[L_ANKLE], keypoints[R_ANKLE]] if k[1] > 0]
        
        if ankles_x:
            feet_box = [min(ankles_x)-60, min(ankles_y)-60, max(ankles_x)+60, max(ankles_y)+60]
            for boot in boots:
                if calculate_iou(boot['bbox'], feet_box) > 0.05:
                    boots_worn = True
                    break
            if not boots_worn:
                missing_gear.append("Boots")

    # --- GLOVE CHECK (Proxy) ---
    if keypoints[L_WRIST][0] > 0 and keypoints[R_WRIST][0] > 0:
        pass 

    # --- GOGGLES (Class 3) - FIXED ---
    goggles_worn = False
    goggles = [g for g in gear_detections if g['class_id'] == 3]
    
    if keypoints[NOSE][0] > 0:
        head_box = [
            keypoints[NOSE][0] - 30, 
            keypoints[NOSE][1] - 30, 
            keypoints[NOSE][0] + 30, 
            keypoints[NOSE][1] + 30 
        ]
        
        for goggle in goggles:
            if calculate_iou(goggle['bbox'], head_box) > 0.01: 
                goggles_worn = True
                break
        
        if not goggles_worn:
            missing_gear.append("Goggles")

    # --- FINAL RETURN STATEMENT (Crucial!) ---
    is_compliant = (len(missing_gear) == 0) and (len(violations) == 0)
    
    return {
        "is_compliant": is_compliant,
        "missing_gear": missing_gear,
        "violations": violations
    }

# --- Utils ---
def point_in_box(point, bbox):
    x, y = point
    x1, y1, x2, y2 = bbox
    return x1 <= x <= x2 and y1 <= y <= y2

def calculate_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    return inter_area / float(box1_area + box2_area - inter_area + 1e-6)