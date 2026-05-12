import { useState } from 'react';
import { chatWithAI } from '../api';

export default function ChatBubble({ exercise, onClose }) {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!question.trim()) return;

    const userMsg = question.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setQuestion('');
    setLoading(true);

    try {
      const context = [
        ...exercise.key_points,
        ...exercise.common_mistakes,
        exercise.breathing,
      ].join('；');

      const res = await chatWithAI({
        exerciseName: exercise.name,
        exerciseContext: context,
        question: userMsg,
        history: messages,
      });

      setMessages(prev => [...prev, { role: 'assistant', content: res.answer }]);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: '网络错误，请重试' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-end z-50">
      <div className="bg-white w-full max-w-md mx-auto rounded-t-2xl p-4 max-h-[70vh] flex flex-col">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-medium text-gray-900">关于「{exercise.name}」的问题</h3>
          <button onClick={onClose} className="text-gray-400 text-xl">×</button>
        </div>

        <div className="flex-1 overflow-y-auto space-y-3 mb-3">
          {messages.length === 0 && (
            <p className="text-sm text-gray-400 text-center py-4">
              问问 AI 关于这个动作的任何问题
            </p>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`text-sm ${
              msg.role === 'user' ? 'text-right' : 'text-left'
            }`}>
              <span className={`inline-block px-3 py-2 rounded-xl max-w-[80%] ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700'
              }`}>
                {msg.content}
              </span>
            </div>
          ))}
          {loading && (
            <div className="text-left">
              <span className="inline-block px-3 py-2 rounded-xl bg-gray-100 text-gray-400 text-sm">
                思考中...
              </span>
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="例如：膝盖疼怎么办？"
            className="flex-1 px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:border-blue-400"
          />
          <button
            onClick={handleSend}
            disabled={loading || !question.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-xl text-sm disabled:opacity-50"
          >
            发送
          </button>
        </div>
      </div>
    </div>
  );
}
