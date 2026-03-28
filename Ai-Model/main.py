import os
import time
import threading
import cv2
import socketio
import numpy as np
import math
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

# --- Configuration ---
NODE_SERVER_URL = "http://localhost:5000"
frame_lock = threading.Lock()
latest_frame = None
inference_lock = threading.Lock()
draw_data = {"persons": [], "objects": [], "passing_line": None}
last_alert_time = {}

# --- Socket.IO Setup ---
sio = socketio.Client()


def connect_to_node():
    while not sio.connected:
        try:
            sio.connect(NODE_SERVER_URL, transports=["websocket", "polling"])
            print("✅ Connected to Node Bridge Server")
            break
        except Exception:
            time.sleep(2)


threading.Thread(target=connect_to_node, daemon=True).start()

# --- Load AI Models ---
print("⏳ Loading YOLOv8 Models...")
# Objects ke liye Nano model fast chalta hai
model = YOLO("yolov8n.pt")
# Haath aur wrist points ke liye Pose model
pose_model = YOLO("yolov8n-pose.pt")
print("✅ AI Models Ready")

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


def get_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# --- Thread 1: Camera Feed ---
def camera_thread():
    global latest_frame
    while True:
        success, frame = camera.read()
        if success:
            frame = cv2.flip(frame, 1)
            with frame_lock:
                latest_frame = frame.copy()
        time.sleep(0.01)


# --- Thread 2: AI Inference ---
def inference_thread():
    global draw_data
    while True:
        with frame_lock:
            frame = latest_frame.copy() if latest_frame is not None else None
        if frame is None:
            time.sleep(0.05)
            continue

        results = model(frame, conf=0.5, verbose=False)
        pose_results = pose_model(frame, conf=0.4, verbose=False)

        temp_persons = []
        current_objects = []
        person_hands = []
        passing_line = None
        alerts = []

        # 1. Detect & Sort Persons (Left to Right)
        # Taki Seat 1 hamesha left wala banda rahe
        for box in results[0].boxes:
            if int(box.cls[0]) == 0:  # Person class
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                temp_persons.append({"bbox": (x1, y1, x2, y2), "cx": (x1 + x2) / 2})

        sorted_persons = sorted(temp_persons, key=lambda p: p["cx"])

        # 2. Object Detection (Mobile/Books)
        for box in results[0].boxes:
            cls = int(box.cls[0])
            if cls in [67, 73]:  # 67: Mobile, 73: Book
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

                # Check karo mobile kis person ke bounding box ke andar hai
                owner_idx = 0
                for idx, p in enumerate(sorted_persons):
                    px1, py1, px2, py2 = p["bbox"]
                    if px1 < cx < px2 and py1 < cy < py2:
                        owner_idx = idx
                        break

                label = "Mobile" if cls == 67 else "Prohibited Object"
                current_objects.append({"bbox": (x1, y1, x2, y2), "label": label})
                alerts.append(
                    {
                        "msg": f"🚨 {label} Detected!",
                        "type": "object",
                        "seatIndex": owner_idx,
                    }
                )

        # 3. Hand Meeting (Paper Passing) Logic
        if len(pose_results) > 0 and pose_results[0].keypoints is not None:
            kpts_list = pose_results[0].keypoints.xy
            for p_idx, kpts in enumerate(kpts_list):
                # 9 = Left Wrist, 10 = Right Wrist
                for k_idx in [9, 10]:
                    hx, hy = float(kpts[k_idx][0]), float(kpts[k_idx][1])
                    if hx > 0:
                        # Match hand to sorted person index
                        for s_idx, p in enumerate(sorted_persons):
                            px1, py1, px2, py2 = p["bbox"]
                            if px1 < hx < px2 and py1 < hy < py2:
                                person_hands.append({"seat": s_idx, "pos": (hx, hy)})
                                break

        # Check distance between hands of DIFFERENT people
        for i in range(len(person_hands)):
            for j in range(i + 1, len(person_hands)):
                h1, h2 = person_hands[i], person_hands[j]
                if h1["seat"] != h2["seat"]:
                    dist = get_distance(h1["pos"], h2["pos"])
                    if dist < 85:  # Pixel distance threshold
                        passing_line = (h1["pos"], h2["pos"])
                        # Alert Dono Involved Seats ko jayega
                        alerts.append(
                            {
                                "msg": "🤝 Paper Passing Detected!",
                                "type": "passing",
                                "seatIndex": h1["seat"],
                            }
                        )
                        alerts.append(
                            {
                                "msg": "🤝 Paper Passing Detected!",
                                "type": "passing",
                                "seatIndex": h2["seat"],
                            }
                        )

        # --- Send Alerts with Cooldown (5 Seconds) ---
        curr_t = time.time()
        for a in alerts:
            key = f"{a['type']}_{a['seatIndex']}"
            if curr_t - last_alert_time.get(key, 0) > 5:
                if sio.connected:
                    sio.emit("cheating_alert", a)
                    last_alert_time[key] = curr_t

        with inference_lock:
            draw_data = {
                "persons": sorted_persons,
                "objects": current_objects,
                "passing_line": passing_line,
            }
        time.sleep(0.05)


# --- Thread 3: Visual Streaming ---
def stream_frames():
    while True:
        with frame_lock:
            if latest_frame is None:
                continue
            frame = latest_frame.copy()
        with inference_lock:
            data = draw_data.copy()

        # Person Boxes Draw Karo
        for idx, p in enumerate(data["persons"]):
            x1, y1, x2, y2 = p["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"PERSON {idx+1}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        # Prohibited Objects Draw Karo
        for obj in data["objects"]:
            x1, y1, x2, y2 = obj["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(
                frame,
                "MOBILE",
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2,
            )

        # Paper Passing ki Yellow Line
        if data["passing_line"]:
            pt1, pt2 = data["passing_line"]
            cv2.line(
                frame,
                (int(pt1[0]), int(pt1[1])),
                (int(pt2[0]), int(pt2[1])),
                (0, 255, 255),
                4,
            )

        _, buffer = cv2.imencode(".jpg", frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


@app.route("/video_feed")
def video_feed():
    return Response(
        stream_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    threading.Thread(target=camera_thread, daemon=True).start()
    threading.Thread(target=inference_thread, daemon=True).start()
    # Server 5001 par chalega for AI Feed
    app.run(host="0.0.0.0", port=5001, threaded=True)
