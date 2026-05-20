# 🛡️ VisionGuard: Smart Real-Time Exam Monitoring System

VisionGuard is an advanced AI-powered proctoring solution designed to maintain examination integrity. By combining computer vision (**YOLOv8 & OpenCV**) with a robust real-time web interface (**MERN Stack & Socket.io**), the system automatically detects exam violations and flags specific student seats on a live supervisor dashboard.

---

## ✨ Key Features

* **Real-Time Live Monitoring:** Low-latency video streaming integrated with advanced AI detection models.
* **Prohibited Object Detection:** Automatically detects mobile phones and books, drawing red bounding boxes around them.
* **Paper Passing (Hand Proximity) Detection:** Utilizes **YOLOv8-pose** to track wrists and draws a yellow line when hands meet between different students, instantly flagging collusion.
* **Dynamic Seat Layout:** Supervisors can configure the classroom grid dynamically from the dashboard.
* **Targeted Alerts:** Uses coordinate-based matching to ensure that only the specific seat committing the violation is turned red.
* **Secure Access Control:** Fully secure Supervisor portal protected by JWT (JSON Web Tokens) and Bcrypt password hashing.

---

## 🛠️ Tech Stack

* **Frontend:** React.js, Tailwind CSS, React Router Dom
* **Backend:** Node.js, Express.js, Flask (Python)
* **AI & Vision:** Python, YOLOv8, YOLOv8-pose, OpenCV
* **Database:** MongoDB Atlas
* **Real-time Sync:** Socket.io (WebSockets)
* **Security:** JWT, Bcrypt

---

## 📂 Project Structure

```text
VisionGuard/
├── backend/            # Node.js + Express Server
│   ├── models/        # MongoDB Schemas
│   ├── server.js      # Core entry point & Auth APIs
│   └── .env           # Environment Variables (MONGO_URI, JWT_SECRET)
├── frontend/           # React + Tailwind Dashboard
│   ├── src/
│   │   ├── components/# Auth, CameraFeed, SeatGrid, AlertBox
│   │   └── App.jsx    # Application Routing & Socket Management
│   └── package.json
└── Ai-Model/           # Python AI Proctoring Engine
    └── main.py        # YOLOv8 Inference, OpenCV Pipeline & Flask Server
```

🚀 Getting Started
1. Backend Setup
Navigate to the backend folder:

Bash
cd backend
Install dependencies:

Bash
npm install
Create a .env file inside the backend directory:

Code snippet
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret_key
PORT=5000
Start the server:

Bash
node server.js
2. Frontend Setup
Navigate to the frontend folder:

Bash
cd ../frontend
Install dependencies:

Bash
npm install
Start the Vite development server:

Bash
npm run dev
3. AI Model Setup
Navigate to the Ai-Model folder:

Bash
cd ../Ai-Model
Install required Python packages:

Bash
pip install ultralytics opencv-python flask flask-cors python-socketio numpy
Run the AI proctoring engine:

Bash
python main.py
🔒 Security & Testing
Authentication: Passwords are securely hashed via bcryptjs before database storage.

API Testing: Verified via Postman for robust error handling during registration and login workflows.

WebSocket Monitoring: Debugged using Chrome DevTools network tracing to maintain zero latency for cheating_alert signals.
