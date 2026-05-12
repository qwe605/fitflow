export default function ProgressBar({ progress }) {
  const percentage = Math.round(progress * 100);

  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs text-gray-500 mb-1">
        <span>训练进度</span>
        <span>{percentage}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-green-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
