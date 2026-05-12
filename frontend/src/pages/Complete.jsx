import { useRef, useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import html2canvas from 'html2canvas';
import { saveWorkoutRecord } from '../storage';

export default function Complete() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const cardRef = useRef(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  if (!state) {
    navigate('/');
    return null;
  }

  const { plan, completedCount, totalCount, duration } = state;
  const percentage = Math.round((completedCount / totalCount) * 100);
  const today = new Date().toLocaleDateString('zh-CN', {
    month: 'long', day: 'numeric', weekday: 'long',
  });

  useEffect(() => {
    saveWorkoutRecord({
      title: plan.title,
      completedCount,
      totalCount,
      duration,
      percentage,
    });
  }, []);

  const handleSaveCard = async () => {
    if (!cardRef.current) return;
    setSaving(true);
    try {
      const canvas = await html2canvas(cardRef.current, {
        scale: 2,
        backgroundColor: null,
      });
      const link = document.createElement('a');
      link.download = `FitFlow_${new Date().toISOString().slice(0, 10)}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      setSaved(true);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-4">
      <div ref={cardRef} className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl p-6 text-white text-center mb-4">
        <div className="text-4xl mb-2">💪</div>
        <h2 className="text-xl font-bold mb-1">训练完成！</h2>
        <p className="text-sm opacity-80">{today}</p>

        <div className="grid grid-cols-3 gap-4 mt-6">
          <div>
            <div className="text-2xl font-bold">{completedCount}/{totalCount}</div>
            <div className="text-xs opacity-70">完成动作</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{duration}</div>
            <div className="text-xs opacity-70">分钟</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{percentage}%</div>
            <div className="text-xs opacity-70">完成率</div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-white/20 text-sm">
          {plan.title}
        </div>

        <div className="mt-3 text-xs opacity-50">
          FitFlow · 让抖音健身视频变成你的训练计划
        </div>
      </div>

      <button
        onClick={handleSaveCard}
        disabled={saving}
        className="w-full py-3 bg-blue-500 text-white rounded-xl font-medium mb-3 disabled:opacity-50"
      >
        {saved ? '已保存 ✓' : saving ? '生成中...' : '保存训练卡到相册'}
      </button>

      {plan.next_suggestion && (
        <div className="bg-white rounded-xl p-4 border border-gray-100 mb-4">
          <h3 className="text-sm font-medium text-gray-700 mb-1">AI 建议</h3>
          <p className="text-sm text-gray-600">{plan.next_suggestion}</p>
        </div>
      )}

      {plan.cooldown?.length > 0 && (
        <div className="bg-white rounded-xl p-4 border border-gray-100 mb-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">拉伸放松</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            {plan.cooldown.map((c, i) => <li key={i}>• {c}</li>)}
          </ul>
        </div>
      )}

      <button
        onClick={() => navigate('/')}
        className="w-full py-3 bg-gray-900 text-white rounded-xl font-medium"
      >
        返回首页
      </button>
    </div>
  );
}
