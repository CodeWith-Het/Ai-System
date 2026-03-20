import os
import time
import threading
import cv2
import socketio
import numpy as np
import math
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from pyngrok import ngrok
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

# --- State & Configuration ---
NODE_SERVER_URL = "http://localhost:5000"
active_seat = 1

frame_lock = threading.Lock()
latest_frame = None
inference_lock = threading.Lock()
draw_data = {
    "persons": [],
    "objects": [],
    "hand_regions": [],
    "passing_line": None,
    "papers": [],
}

# --- Socket.IO ---
sio = socketio.Client()


def connect_to_node():
    while not sio.connected:
        try:
            sio.connect(NODE_SERVER_URL, transports=["websocket", "polling"])
            print(f"✅ Connected to Node Bridge")
            break
        except Exception:
            time.sleep(3)


threading.Thread(target=connect_to_node, daemon=True).start()

# --- Models ---
print("⏳ Loading YOLO Models...")
model = YOLO("yolov8n.pt")
pose_model = YOLO("yolov8n-pose.pt")
print("✅ Models Loaded!")

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# --- WHITE PAPER DETECTION HACK (OpenCV) ---
def detect_white_paper(frame, person_bboxes):
    papers = []
    # Convert to HSV color space to detect White easily
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Define range for white color (Adjust if room lighting is yellow/blue)
    lower_white = np.array([0, 0, 160])
    upper_white = np.array([180, 40, 255])

    mask = cv2.inRange(hsv, lower_white, upper_white)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 4000 < area < 40000:  # Reasonably large paper patch
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            # Check if it's rectangular-ish (not a long thin pipe or a perfect square)
            if 0.5 < aspect_ratio < 2.0:
                cx, cy = x + w / 2, y + h / 2
                # Ensure the white patch belongs to a person (so we don't detect white walls)
                for p_box in person_bboxes:
                    px1, py1, px2, py2 = p_box
                    if px1 < cx < px2 and py1 < cy < py2:
                        papers.append({"bbox": (x, y, x + w, y + h), "type": "paper"})
                        break
    return papers


# --- THREAD 1: CAMERA WORKER ---
def camera_worker():
    global latest_frame
    while True:
        success, frame = camera.read()
        if success:
            frame = cv2.flip(frame, 1)
            with frame_lock:
                latest_frame = frame.copy()
        time.sleep(0.01)


# --- THREAD 2: AI INFERENCE WORKER ---
last_alert_time = {}


def inference_worker():
    global draw_data
    while True:
        with frame_lock:
            frame = latest_frame.copy() if latest_frame is not None else None

        if frame is None:
            time.sleep(0.05)
            continue

        results = model(frame, conf=0.6, imgsz=256, verbose=False)
        pose_results = pose_model(frame, conf=0.5, imgsz=256, verbose=False)

        current_persons = []
        current_objects = []
        alerts_to_send = []
        hand_regions = []
        person_hands = []
        passing_line = None

        # Extract YOLO Objects
        person_bboxes = []
        for box in results[0].boxes:
            cls = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            centroid = ((x1 + x2) / 2, (y1 + y2) / 2)

            if cls == 0:  # Person
                current_persons.append({"bbox": (x1, y1, x2, y2), "centroid": centroid})
                person_bboxes.append((x1, y1, x2, y2))
            elif cls == 67:  # Mobile
                current_objects.append(
                    {"type": "mobile", "bbox": (x1, y1, x2, y2), "centroid": centroid}
                )
            elif cls in [73, 76, 62]:  # Laptop/Book
                current_objects.append(
                    {
                        "type": "prohibited_item",
                        "bbox": (x1, y1, x2, y2),
                        "centroid": centroid,
                    }
                )

        # 📄 NEW: Detect Physical Paper
        detected_papers = detect_white_paper(frame, person_bboxes)
        if len(detected_papers) > 0:
            alerts_to_send.append(
                {
                    "msg": "📄 Physical Paper / Cheat Sheet Detected!",
                    "type": "physical_paper",
                    "seatIndex": active_seat - 1,
                }
            )

        # Process Hands for Collusion / Hand-Passing
        if len(pose_results) > 0 and pose_results[0].keypoints is not None:
            all_kpts = (
                pose_results[0].keypoints.xy
                if hasattr(pose_results[0].keypoints, "xy")
                else pose_results[0].keypoints
            )
            for p_idx, kpts in enumerate(all_kpts):
                if len(kpts) > 10:
                    lx, ly = float(kpts[9][0]), float(kpts[9][1])
                    rx, ry = float(kpts[10][0]), float(kpts[10][1])

                    if not math.isnan(lx) and lx > 0:
                        person_hands.append({"p_idx": p_idx, "pos": (lx, ly)})
                        hand_regions.append((lx, ly))
                    if not math.isnan(rx) and rx > 0:
                        person_hands.append({"p_idx": p_idx, "pos": (rx, ry)})
                        hand_regions.append((rx, ry))

        # Check for Hand Passing (Different people touching hands)
        passing_detected = False
        for i in range(len(person_hands)):
            for j in range(i + 1, len(person_hands)):
                h1, h2 = person_hands[i], person_hands[j]
                if h1["p_idx"] != h2["p_idx"]:
                    if distance(h1["pos"], h2["pos"]) < 80:
                        passing_detected = True
                        passing_line = (h1["pos"], h2["pos"])
                        break
            if passing_detected:
                break

        if passing_detected:
            alerts_to_send.append(
                {
                    "msg": "🤝 Hands Meeting / Collusion Detected!",
                    "type": "hand_passing",
                    "seatIndex": active_seat - 1,
                }
            )

        # Check for Phones
        for obj in current_objects:
            if obj["type"] == "mobile":
                alerts_to_send.append(
                    {
                        "msg": "📱 Phone Detected in Hand!",
                        "type": "mobile",
                        "seatIndex": active_seat - 1,
                    }
                )

        # Emit Alerts
        curr_time = time.time()
        for alert in alerts_to_send:
            if sio.connected:
                a_type = alert["type"]
                if curr_time - last_alert_time.get(a_type, 0) > 4:
                    sio.emit("cheating_alert", alert)
                    last_alert_time[a_type] = curr_time

        sorted_persons = sorted(
            current_persons, key=lambda p: (p["centroid"][1] // 50, p["centroid"][0])
        )

        with inference_lock:
            draw_data = {
                "persons": sorted_persons,
                "objects": current_objects,
                "hand_regions": hand_regions,
                "passing_line": passing_line,
                "papers": detected_papers,
            }

        time.sleep(0.1)


threading.Thread(target=camera_worker, daemon=True).start()
threading.Thread(target=inference_worker, daemon=True).start()


# --- THREAD 3: VIDEO STREAMING ---
def generate_frames():
    while True:
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.05)
                continue
            frame = latest_frame.copy()

        with inference_lock:
            data = draw_data.copy()

        # Draw Hands
        for h_pos in data.get("hand_regions", []):
            cv2.circle(frame, (int(h_pos[0]), int(h_pos[1])), 8, (255, 0, 255), -1)

        # Draw Passing Line
        if data.get("passing_line"):
            p1, p2 = data["passing_line"]
            cv2.line(
                frame,
                (int(p1[0]), int(p1[1])),
                (int(p2[0]), int(p2[1])),
                (0, 255, 255),
                4,
            )
            cv2.putText(
                frame,
                "COLLUSION DETECTED",
                (int(p1[0]), int(p1[1]) - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

        # Draw Detected Physical Paper
        for paper in data.get("papers", []):
            x1, y1, x2, y2 = paper["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.putText(
                frame,
                "PAPER DETECTED",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

        # Draw Persons
        for idx, person in enumerate(data.get("persons", [])):
            x1, y1, x2, y2 = person["bbox"]
            seat_num = idx + 1

            if seat_num == active_seat:
                color = (255, 255, 0)
                label = f"[MONITORING] PERSON {seat_num}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            else:
                color = (0, 255, 0)
                label = f"PERSON {seat_num}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw, y1), color, -1)
            cv2.putText(
                frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2
            )

        # Draw Objects
        for obj in data.get("objects", []):
            x1, y1, x2, y2 = obj["bbox"]
            color = (0, 0, 255) if obj["type"] == "mobile" else (0, 165, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame,
                obj["type"].upper(),
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

        ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ret:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )

        time.sleep(0.03)


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/set_seat", methods=["POST"])
def set_seat():
    global active_seat
    active_seat = request.json.get("seatNumber", 1)
    return jsonify({"status": "ok", "active_seat": active_seat})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, threaded=True, debug=False)
