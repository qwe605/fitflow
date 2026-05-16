import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchVideos, parseDouyinUrlStream } from '../api';
import { getHistory } from '../storage';
import VideoCard from '../components/VideoCard';

const CATEGORIES = ['全部', '腿部', '胸部', '背部', '核心', '肩部', '全身'];

const STEP_LABELS = {
  resolving: '正在解析链接...',
  fetching: '正在获取视频信息...',
  downloading: '正在下载视频...',
  extracting: '正在提取关键帧...',
  analyzing: 'AI 正在分析动作...',
};

export default function Home() {
  const [videos, setVideos] = useState([]);
  const [activeCategory, setActiveCategory] = useState('全部');
  const [linkInput, setLinkInput] = useState('');
  const [parsing, setParsing] = useState(false);
  const [parseStep, setParseStep] = useState('');
  const [parsePartial, setParsePartial] = useState('');
  const [parseError, setParseError] = useState('');
  const [history, setHistory] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchVideos().then(setVideos);
    setHistory(getHistory());
  }, []);

  const filtered = activeCategory === '全部'
    ? videos
    : videos.filter(v => v.category === activeCategory);

  const handleParseLInk = async () => {
    if (!linkInput.trim()) return;
    setParsing(true);
    setParseError('');
    setParseStep('');
    setParsePartial('');

    try {
      let result = null;
      await parseDouyinUrlStream(linkInput.trim(), (event) => {
        if (event.step === 'error') {
          setParseError(event.message);
        } else if (event.step === 'done') {
          result = event.data;
        } else if (event.step === 'analyzing' && event.partial) {
          setParsePartial(prev => prev + event.partial);
        } else {
          setParseStep(STEP_LABELS[event.step] || event.message || '');
        }
      });

      if (result) {
        navigate('/generate/custom', {
          state: { subtitleText: result.subtitle_text, title: result.title },
        });
      } else if (!parseError) {
        setParseError('解析失败，请检查链接');
      }
    } catch (e) {
      setParseError(e.message || '解析失败，请检查链接');
    } finally {
      setParsing(false);
      setParseStep('');
      setParsePartial('');
    }
  };

  return (
    <div className="p-4">
      <header className="text-center py-6">
        <h1 className="text-2xl font-bold text-gray-900">FitFlow</h1>
        <p className="text-sm text-gray-500 mt-1">抖音健身视频 → 你的私人训练计划</p>
      </header>

      <div className="bg-white rounded-xl p-4 border border-gray-100 mb-6">
        <p className="text-sm font-medium text-gray-700 mb-2">粘贴抖音视频链接</p>
        <div className="flex gap-2">
          <input
            type="text"
            value={linkInput}
            onChange={e => setLinkInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleParseLInk()}
            placeholder="粘贴抖音分享链接或口令..."
            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-blue-400"
          />
          <button
            onClick={handleParseLInk}
            disabled={parsing || !linkInput.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium disabled:opacity-50 whitespace-nowrap"
          >
            {parsing ? '解析中...' : '解析'}
          </button>
        </div>
        {parsing && parseStep && (
          <div className="mt-2">
            <p className="text-xs text-blue-600 flex items-center gap-1">
              <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              {parseStep}
            </p>
            {parsePartial && (
              <p className="text-xs text-gray-500 mt-1 max-h-20 overflow-y-auto whitespace-pre-wrap">
                {parsePartial.slice(-200)}
              </p>
            )}
          </div>
        )}
        {parseError && <p className="text-red-500 text-xs mt-2">{parseError}</p>}
        <p className="text-xs text-gray-400 mt-2">支持抖音分享链接、短链接或复制的口令</p>
      </div>

      <div className="flex items-center gap-2 mb-3">
        <div className="h-px flex-1 bg-gray-200" />
        <span className="text-xs text-gray-400">或选择精选视频</span>
        <div className="h-px flex-1 bg-gray-200" />
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2 mb-4">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`px-3 py-1 rounded-full text-sm whitespace-nowrap transition ${
              activeCategory === cat
                ? 'bg-blue-500 text-white'
                : 'bg-white text-gray-600 border border-gray-200'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {filtered.map(video => (
          <VideoCard
            key={video.id}
            video={video}
            onClick={() => navigate(`/generate/${video.id}`)}
          />
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="text-center text-gray-400 mt-8">暂无该分类视频</p>
      )}

      {history.length > 0 && (
        <div className="mt-8">
          <h3 className="text-sm font-medium text-gray-700 mb-3">训练记录</h3>
          <div className="space-y-2">
            {history.slice(0, 5).map(record => (
              <div key={record.id} className="bg-white rounded-lg p-3 border border-gray-100 flex justify-between items-center">
                <div>
                  <div className="text-sm font-medium text-gray-800">{record.title}</div>
                  <div className="text-xs text-gray-400">
                    {new Date(record.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
                    {' · '}{record.duration}分钟
                  </div>
                </div>
                <div className="text-sm font-medium text-green-500">{record.percentage}%</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
