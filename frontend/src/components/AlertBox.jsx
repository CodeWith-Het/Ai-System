import React from 'react';
import { AlertTriangle } from 'lucide-react';

const AlertBox = ({ message }) => {
  if (!message) return null;

  return (
    <div className="fixed top-5 right-5 z-50 animate-bounce">
      <div className="bg-red-600 text-white px-6 py-4 rounded-lg shadow-2xl border-2 border-white flex items-center gap-3">
        <AlertTriangle size={32} />
        <div>
          <p className="font-bold text-lg">CHEATING DETECTED</p>
          <p className="text-sm">{message}</p>
        </div>
      </div>
    </div>
  );
};

export default AlertBox;
