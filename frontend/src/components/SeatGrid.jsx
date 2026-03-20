import React from "react";

const SeatGrid = ({ seats, onResetSeat }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
      {seats.map((seat, index) => (
        <div
          key={index}
          onClick={() => onResetSeat(index)}
          className={`
            relative h-32 rounded-lg border-4 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group
            ${
              seat.isCheating
                ? "bg-red-900/80 border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.6)] scale-105 z-10"
                : "bg-slate-800 border-slate-600 hover:border-slate-500 hover:bg-slate-750"
            }
          `}
        >
          <span
            className={`text-3xl font-bold ${seat.isCheating ? "text-white" : "text-slate-400"}`}
          >
            {seat.id}
          </span>

          <span
            className={`text-[10px] font-bold uppercase mt-2 px-2 py-0.5 rounded ${seat.isCheating ? "bg-red-600 text-white" : "bg-slate-700 text-slate-400"}`}
          >
            {seat.isCheating ? "⚠️ DETECTED" : "ACTIVE"}
          </span>

          {/* Desk Graphic */}
          <div
            className={`w-16 h-1.5 mt-3 rounded-full ${seat.isCheating ? "bg-red-400" : "bg-slate-600 group-hover:bg-slate-500"}`}
          ></div>
        </div>
      ))}
    </div>
  );
};

export default SeatGrid;
