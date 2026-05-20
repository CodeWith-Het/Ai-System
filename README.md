🛡️ VisionGuard — Smart Real-Time Exam Monitoring System

An AI-powered proctoring solution that ensures examination integrity using Computer Vision, Real-Time Streaming, and Live Seat-Based Monitoring.

📌 Overview

VisionGuard is an advanced smart examination monitoring system designed to detect and prevent cheating activities in real time.
The platform combines YOLOv8, OpenCV, and YOLOv8-pose with a powerful MERN Stack dashboard to provide supervisors with live alerts and automated violation tracking.

The system identifies:

📱 Mobile phone usage
📚 Unauthorized books/materials
🤝 Paper passing & suspicious hand interactions
🚨 Seat-specific cheating alerts

All detected violations are highlighted instantly on the supervisor dashboard using a dynamic seat-mapping system.

✨ Features
🎥 Real-Time Monitoring
Live low-latency video streaming
Continuous AI-based surveillance
Real-time dashboard updates using Socket.io
📱 Prohibited Object Detection

Detects:

Mobile Phones
Books / Notes

Violations are highlighted with:

🔴 Red Bounding Boxes
🚨 Instant Supervisor Alerts
🤝 Hand Proximity / Paper Passing Detection

Using YOLOv8-pose, the system:

Tracks wrist keypoints
Detects suspicious hand interactions between students
Draws a 🟡 Yellow Line when hands overlap across seats

🪑 Dynamic Seat Layout
Configurable classroom grid
Flexible seat arrangement from supervisor dashboard
Real-time seat status updates

🎯 Targeted Seat Alerts
Coordinate-based violation mapping
Only the specific violating seat turns red
Prevents false-positive classroom alerts

🔐 Secure Authentication
JWT-based authentication
Bcrypt password hashing
Protected Supervisor Dashboard

🛠️ Tech Stack
| Category                | Technologies                             |
| ----------------------- | ---------------------------------------- |
| Frontend                | React.js, Tailwind CSS, React Router DOM |
| Backend                 | Node.js, Express.js, Flask               |
| AI & Vision             | Python, YOLOv8, YOLOv8-pose, OpenCV      |
| Database                | MongoDB Atlas                            |
| Real-Time Communication | Socket.io (WebSockets)                   |
| Security                | JWT, Bcrypt                              |

📂 Project Structure
VisionGuard/
│
├── backend/                 # Node.js + Express Backend
│   ├── models/              # MongoDB Schemas
│   ├── routes/              # Authentication & APIs
│   ├── middleware/          # JWT Verification Middleware
│   ├── server.js            # Main Backend Entry Point
│   └── .env                 # Environment Variables
│
├── frontend/                # React + Tailwind Frontend
│   ├── src/
│   │   ├── components/      # UI Components
│   │   ├── pages/           # Application Pages
│   │   ├── services/        # API & Socket Services
│   │   └── App.jsx          # Main Routing File
│   └── package.json
│
└── Ai-Model/                # AI Detection Engine
    ├── models/              # YOLO Model Weights
    ├── utils/               # Detection Utilities
    └── main.py              # OpenCV + YOLOv8 Pipeline
    
🚀 Getting Started

1️⃣ Clone Repository
git clone <your-repository-url>
cd VisionGuard

⚙️ Backend Setup
Navigate to Backend Folder
cd backend
Install Dependencies
npm install
Create .env File
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret_key
PORT=5000
Start Backend Server
node server.js

Server runs on:

http://localhost:5000

🎨 Frontend Setup
Navigate to Frontend Folder
cd ../frontend
Install Dependencies
npm install
Start Development Server
npm run dev

Frontend runs on:

http://localhost:5173
🤖 AI Model Setup
Navigate to AI Model Folder
cd ../Ai-Model
Install Python Dependencies
pip install ultralytics opencv-python flask flask-cors python-socketio numpy
Run AI Engine
python main.py

🔄 System Workflow
Camera Feed
      ↓
OpenCV Video Processing
      ↓
YOLOv8 / YOLOv8-pose Detection
      ↓
Violation Detection Logic
      ↓
Socket.io Real-Time Event
      ↓
Supervisor Dashboard Alert

🚨 Detection Types
| Detection              | Description                       |
| ---------------------- | --------------------------------- |
| Mobile Detection       | Detects mobile phone usage        |
| Book Detection         | Detects books or notes            |
| Hand Interaction       | Detects suspicious hand proximity |
| Seat Violation Mapping | Highlights only violating seat    |

🔒 Security & Authentication
Authentication
Secure login system using JWT
Password hashing using bcryptjs
API Testing
Tested using Postman
Proper error handling implemented
Real-Time Monitoring
Socket.io events debugged using Chrome DevTools
Optimized for minimal alert latency

📸 Future Enhancements
🎙️ Voice Detection
😴 Drowsiness Detection
👀 Eye Tracking
🧠 Behavior Analysis
☁️ Cloud Deployment
📊 Exam Analytics Dashboard
