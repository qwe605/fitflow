import { useState } from 'react';

export default function ExerciseCard({ exercise, index, isCompleted, onToggle, onAskAI }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`bg-white rounded-xl border transition ${
      isCompleted ? 'border-green-200 bg-green-50' : 'border-gray-100'
    }`}>
      <div className="p-4 flex items-center gap-3">
        <button
          onClick={onToggle}
          className={`w-7 h-7 rounded-full border-2 flex items-center justify-center shrink-0 transition ${
            isCompleted
              ? 'bg-green-500 border-green-500 text-white'
              : 'border-gray-300'
          }`}
        >
          {isCompleted && '✓'}
        </button>

        <div className="flex-1 min-w-0" onClick={() => setExpanded(!expanded)}>
          <div className="flex items-center justify-between">
            <span className={`font-medium ${isCompleted ? 'text-gray-400 line-through' : 'text-gray-900'}`}>
              {exercise.name}
            </span>
            <span className="text-sm text-blue-500">
              {exercise.sets}×{exercise.reps}
            </span>
          </div>
          <div className="text-xs text-gray-400">{exercise.target_muscle}</div>
        </div>

        <button
          onClick={onAskAI}
          className="w-7 h-7 rounded-full bg-blue-50 text-blue-500 text-sm flex items-center justify-center shrink-0"
        >
          ?
        </button>
      </div>

      {expanded && (
        <div className="px-4 pb-4 border-t border-gray-50 pt-3">
          <div className="text-xs text-gray-600 space-y-1">
            <p className="font-medium text-gray-700">要点：</p>
            {exercise.key_points.map((p, i) => <p key={i}>✓ {p}</p>)}
          </div>
          {exercise.common_mistakes.length > 0 && (
            <div className="text-xs text-red-500 mt-2 space-y-1">
              <p className="font-medium">避免：</p>
              {exercise.common_mistakes.map((m, i) => <p key={i}>✗ {m}</p>)}
            </div>
          )}
          <div className="text-xs text-gray-500 mt-2">
            呼吸：{exercise.breathing}
          </div>
          {exercise.video_search && (
            <a
              href={`https://www.douyin.com/search/${encodeURIComponent(exercise.video_search)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 mt-3 px-3 py-1.5 bg-pink-50 text-pink-600 rounded-lg text-xs font-medium hover:bg-pink-100 transition"
            >
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
              观看教学视频
            </a>
          )}
        </div>
      )}
    </div>
  );
}
