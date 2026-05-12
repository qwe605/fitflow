import { useState, useEffect } from 'react';

export default function Timer({ seconds, onEnd }) {
  const [remaining, setRemaining] = useState(seconds);

  useEffect(() => {
    if (remaining <= 0) {
      onEnd();
      return;
    }
    const timer = setTimeout(() => setRemaining(r => r - 1), 1000);
    return () => clearTimeout(timer);
  }, [remaining, onEnd]);

  const percentage = (remaining / seconds) * 100;

  return (
    <div className="bg-blue-50 rounded-xl p-4 text-center">
      <p className="text-sm text-blue-600 mb-2">组间休息</p>
      <div className="text-3xl font-bold text-blue-700">{remaining}s</div>
      <div className="w-full bg-blue-200 rounded-full h-2 mt-3">
        <div
          className="bg-blue-500 h-2 rounded-full transition-all duration-1000"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <button
        onClick={onEnd}
        className="mt-3 text-sm text-blue-500 underline"
      >
        跳过休息
      </button>
    </div>
  );
}
