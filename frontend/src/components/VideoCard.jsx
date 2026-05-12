const CATEGORY_COLORS = {
  '腿部': 'bg-orange-100 text-orange-700',
  '胸部': 'bg-red-100 text-red-700',
  '背部': 'bg-blue-100 text-blue-700',
  '核心': 'bg-yellow-100 text-yellow-700',
  '肩部': 'bg-purple-100 text-purple-700',
  '全身': 'bg-green-100 text-green-700',
};

export default function VideoCard({ video, onClick }) {
  const colorClass = CATEGORY_COLORS[video.category] || 'bg-gray-100 text-gray-700';

  return (
    <button
      onClick={onClick}
      className="w-full bg-white rounded-xl p-4 border border-gray-100 text-left hover:shadow-md transition"
    >
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="font-medium text-gray-900">{video.title}</h3>
          <div className="flex items-center gap-2 mt-2">
            <span className={`px-2 py-0.5 rounded-full text-xs ${colorClass}`}>
              {video.category}
            </span>
            <span className="text-xs text-gray-400">{video.duration}</span>
            <span className="text-xs text-gray-400">{video.difficulty}</span>
          </div>
        </div>
        <span className="text-gray-300 text-xl">→</span>
      </div>
    </button>
  );
}
