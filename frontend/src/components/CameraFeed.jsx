import React from "react";

const CameraFeed = () => {
  return (
    <div className="w-full bg-black rounded-xl overflow-hidden border-4 border-slate-700 shadow-lg mb-8 relative">
      <div className="absolute top-2 left-2 bg-red-600 px-3 py-1 text-xs font-bold text-white rounded animate-pulse z-10">
        LIVE
      </div>

      {/* YAHAN CHANGE KIYA HAI: Seedha Python ke port 5001 se video le rahe hain */}
      <img
        src="http://localhost:5001/video_feed"
        alt="AI Video Feed"
        className="w-full h-[400px] object-contain block"
        onError={(e) => {
          e.target.src =
            "https://via.placeholder.com/800x400?text=Please+Start+Python+AI+Engine+First";
        }}
      />

      <div className="absolute bottom-2 right-2 text-[10px] text-slate-500">
        Source: Local AI Engine (Port 5001)
      </div>
    </div>
  );
};

export default CameraFeed;
