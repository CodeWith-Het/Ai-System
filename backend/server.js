const path = require("path");
// 🛠️ PATH FIX: Yeh line ab absolute path se .env load karegi
require("dotenv").config({ path: path.join(__dirname, ".env") });

const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const cors = require("cors");
const axios = require("axios");
const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");

const app = express();
app.use(cors());
app.use(express.json());

// --- Debugging: Check if URI is loading ---
console.log("------------------------------------");
console.log(
  "🔗 Connecting to:",
  process.env.MONGO_URI ? "URI Found ✅" : "URI Not Found ❌",
);
console.log("------------------------------------");

// --- 1. MONGODB CONNECTION ---
mongoose
  .connect(process.env.MONGO_URI)
  .then(() => console.log("📦 MongoDB Connected Successfully!"))
  .catch((err) => {
    console.log("⚠️ MongoDB Connection Error:", err.message);
    console.log(
      "💡 Tip: Check if your IP 0.0.0.0/0 is added in MongoDB Atlas Network Access.",
    );
  });

// --- 2. USER SCHEMA ---
const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
});
const User = mongoose.model("User", userSchema);

// --- 3. AUTH APIs ---
app.post("/api/signup", async (req, res) => {
  try {
    const { email, password } = req.body;
    const existingUser = await User.findOne({ email });
    if (existingUser)
      return res.status(400).json({ message: "User already exists!" });

    const hashedPassword = await bcrypt.hash(password, 10);
    const newUser = new User({ email, password: hashedPassword });
    await newUser.save();

    res
      .status(201)
      .json({ message: "Account created successfully! Please login." });
  } catch (error) {
    console.error("Signup Error:", error);
    res.status(500).json({ message: "Server error during signup" });
  }
});

app.post("/api/login", async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user)
      return res.status(400).json({ message: "Invalid email or password!" });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch)
      return res.status(400).json({ message: "Invalid email or password!" });

    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, {
      expiresIn: "1d",
    });
    res.json({ token, email: user.email, message: "Login Successful!" });
  } catch (error) {
    console.error("Login Error:", error);
    res.status(500).json({ message: "Server error during login" });
  }
});

// --- 4. AI BRIDGE & SOCKET.IO ---
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

io.on("connection", (socket) => {
  console.log("🔗 Frontend Device Linked:", socket.id);

  socket.on("cheating_alert", (data) => {
    io.emit("notify_supervisor", data);
  });

  socket.on("set_active_seat", (data) => {
    axios
      .post("http://localhost:5001/set_seat", { seatNumber: data.seatNumber })
      .catch((err) => console.log("⚠️ Could not reach AI Engine"));
  });
});

app.post("/api/set-seat", (req, res) => {
  const { seatNumber } = req.body;
  io.emit("set_active_seat", { seatNumber });
  res.json({ status: "ok" });
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () =>
  console.log(`🚀 Node Bridge & Auth Server running on Port ${PORT}`),
);
