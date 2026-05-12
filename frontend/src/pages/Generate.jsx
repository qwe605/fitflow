import { useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { generateWorkout } from '../api';

const LEVELS = [
  { value: 'beginner', label: '入门', desc: '刚开始健身' },
  { value: 'intermediate', label: '进阶', desc: '有一定基础' },
  { value: 'advanced', label: '高阶', desc: '经验丰富' },
];

export default function Generate() {
  const { videoId } = useParams();
  const { state: locationState } = useLocation();
  const navigate = useNavigate();
  const [level, setLevel] = useState('intermediate');
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState('');

  const isCustom = videoId === 'custom';
  const customSubtitle = locationState?.subtitleText;
  const customTitle = locationState?.title;

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    try {
      const params = isCustom
        ? { subtitleText: customSubtitle, userLevel: level }
        : { videoId, userLevel: level };
      const res = await generateWorkout(params);
      if (res.success) {
        setPlan(res.plan);
      } else {
        setError(res.error || '生成失败，请重试');
      }
    } catch (e) {
      setError('网络错误，请检查连接');
    } finally {
      setLoading(false);
    }
  };

  const startWorkout = () => {
    navigate('/workout', { state: { plan } });
  };

  return (
    <div className="p-4">
      <button onClick={() => navigate('/')} className="text-blue-500 text-sm mb-4">
        ← 返回
      </button>

      {!plan ? (
        <>
          {isCustom && customTitle && (
            <div className="bg-blue-50 rounded-xl p-3 mb-4">
              <p className="text-xs text-blue-600">来源：抖音视频</p>
              <p className="text-sm font-medium text-gray-800">{customTitle}</p>
            </div>
          )}
          <h2 className="text-xl font-bold text-gray-900 mb-2">选择你的体能水平</h2>
          <p className="text-sm text-gray-500 mb-6">AI 会根据你的水平调整训练强度</p>

          <div className="space-y-3 mb-6">
            {LEVELS.map(l => (
              <button
                key={l.value}
                onClick={() => setLevel(l.value)}
                className={`w-full p-4 rounded-xl text-left transition ${
                  level === l.value
                    ? 'bg-blue-50 border-2 border-blue-500'
                    : 'bg-white border border-gray-200'
                }`}
              >
                <div className="font-medium text-gray-900">{l.label}</div>
                <div className="text-sm text-gray-500">{l.desc}</div>
              </button>
            ))}
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full py-3 bg-blue-500 text-white rounded-xl font-medium disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                AI 正在生成训练计划...
              </span>
            ) : '生成训练计划'}
          </button>

          {error && <p className="text-red-500 text-sm mt-3 text-center">{error}</p>}
        </>
      ) : (
        <>
          <h2 className="text-xl font-bold text-gray-900 mb-1">{plan.title}</h2>
          <div className="flex gap-3 text-sm text-gray-500 mb-4">
            <span>⏱ {plan.estimated_time}</span>
            <span>🔥 {plan.calories}</span>
          </div>

          {plan.warmup?.length > 0 && (
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2">热身</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                {plan.warmup.map((w, i) => <li key={i}>• {w}</li>)}
              </ul>
            </div>
          )}

          <div className="space-y-3 mb-4">
            {plan.exercises.map((ex, i) => (
              <div key={i} className="bg-white p-4 rounded-xl border border-gray-100">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium text-gray-900">{ex.name}</div>
                    <div className="text-xs text-gray-500">{ex.target_muscle}</div>
                  </div>
                  <div className="text-sm text-blue-500 font-medium">
                    {ex.sets}组 × {ex.reps}次
                  </div>
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  {ex.key_points.map((p, j) => <span key={j} className="mr-2">✓ {p}</span>)}
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={startWorkout}
            className="w-full py-3 bg-green-500 text-white rounded-xl font-medium"
          >
            开始训练 →
          </button>
        </>
      )}
    </div>
  );
}
