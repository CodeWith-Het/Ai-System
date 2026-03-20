import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import io from "socket.io-client";
import Auth from "./components/Auth";
import AlertBox from "./components/AlertBox";
import CameraFeed from "./components/CameraFeed";
import SeatControls from "./components/SeatControls";
import SeatGrid from "./components/SeatGrid";

const socket = io("http://localhost:5000");

// --- 🖥️ DASHBOARD COMPONENT ---
const Dashboard = ({ token, handleLogout }) => {
  const [seats, setSeats] = useState([]);
  const [alertMsg, setAlertMsg] = useState(null);

  useEffect(() => {
    socket.on("notify_supervisor", (data) => {
      setAlertMsg(`${data.msg} at Seat ${data.seatIndex + 1}`);
      setTimeout(() => setAlertMsg(null), 5000);
      markSeatCheating(data.seatIndex);
    });
    return () => socket.off("notify_supervisor");
  }, [seats]);

  const markSeatCheating = (index) => {
    setSeats((prevSeats) => {
      const newSeats = [...prevSeats];
      if (newSeats[index])
        newSeats[index] = { ...newSeats[index], isCheating: true };
      return newSeats;
    });
  };

  const handleResetSeat = (index) => {
    setSeats((prevSeats) => {
      const newSeats = [...prevSeats];
      if (newSeats[index])
        newSeats[index] = { ...newSeats[index], isCheating: false };
      return newSeats;
    });
  };

  const addSeats = (count) => {
    const newSeats = Array.from({ length: count }, (_, i) => ({
      id: seats.length + i + 1,
      isCheating: false,
    }));
    setSeats([...seats, ...newSeats]);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6 font-sans">
      <div className="max-w-7xl mx-auto">
        <header className="mb-6 border-b border-slate-700 pb-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-blue-400">
              🛡️ AI Proctoring System
            </h1>
            <p className="text-slate-400 text-sm">
              Real-time Exam Hall Monitor
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="bg-red-900/50 hover:bg-red-800 border border-red-800 text-red-200 px-4 py-2 rounded"
          >
            Logout
          </button>
        </header>

        <AlertBox message={alertMsg} />
        <CameraFeed />
        <SeatControls onAddSeats={addSeats} onClearRoom={() => setSeats([])} />

        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4 text-slate-300">
            Classroom Layout
          </h2>
          <SeatGrid seats={seats} onResetSeat={handleResetSeat} />
        </div>
      </div>
    </div>
  );
};

// --- 🚀 MAIN APP ---
function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  return (
    <Router>
      <Routes>
        {/* Agar login nahi hai toh Auth dikhao, varna dashboard pe bhejo */}
        <Route
          path="/"
          element={
            !token ? <Auth setToken={setToken} /> : <Navigate to="/dashboard" />
          }
        />

        {/* Agar login hai toh Dashboard dikhao, varna login pe bhejo */}
        <Route
          path="/dashboard"
          element={
            token ? (
              <Dashboard token={token} handleLogout={handleLogout} />
            ) : (
              <Navigate to="/" />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
