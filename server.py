from flask import Flask, Response, jsonify
from flask_cors import CORS
import sqlite3
import cv2
# This imports the logic from your other file
from auto_logger import SafetyMonitor 

app = Flask(__name__)
CORS(app)

# Initialize the AI Monitor
monitor = SafetyMonitor()

@app.route('/video_feed')
def video_feed():
    # This grabs the video frames from your auto_logger and sends them to the browser
    return Response(monitor.generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/logs')
def get_logs():
    # This sends the text logs to the frontend
    conn = sqlite3.connect('safety_system.db')
    c = conn.cursor()
    c.execute("SELECT id, timestamp, person_name, violation_type FROM logs ORDER BY id DESC LIMIT 10")
    data = c.fetchall()
    conn.close()
    
    json_data = []
    for row in data:
        json_data.append({
            "id": row[0],
            "timestamp": row[1],
            "name": row[2],
            "violation": row[3]
        })
    return jsonify(json_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)