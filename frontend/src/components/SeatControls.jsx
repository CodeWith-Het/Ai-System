import React, { useState } from "react";

const SeatControls = ({ onAddSeats, onClearRoom }) => {
  const [count, setCount] = useState("");

  const handleAdd = () => {
    if (count && !isNaN(count)) {
      onAddSeats(parseInt(count));
      setCount("");
    }
  };

  return (
    <div className="bg-slate-800 p-4 rounded-lg mb-6 border border-slate-700">
      <div className="flex flex-wrap items-center gap-4">
        <p className="font-semibold text-gray-300">Room Config:</p>

        <div className="flex items-center gap-2">
          <input
            type="number"
            placeholder="Num seats..."
            className="px-4 py-2 rounded bg-slate-700 border border-slate-600 text-white focus:outline-none focus:border-blue-500 w-32"
            value={count}
            onChange={(e) => setCount(e.target.value)}
          />

          <button
            onClick={handleAdd}
            className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded font-bold transition-colors shadow-lg shadow-blue-900/20"
          >
            Add Seats
          </button>
        </div>

        <button
          onClick={onClearRoom}
          className="bg-red-900/50 hover:bg-red-800 text-red-200 text-sm px-4 py-2 rounded ml-auto border border-red-800 transition-colors"
        >
          Reset Room
        </button>
      </div>
    </div>
  );
};

export default SeatControls;
