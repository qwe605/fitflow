import { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ExerciseCard from '../components/ExerciseCard';
import Timer from '../components/Timer';
import ProgressBar from '../components/ProgressBar';
import ChatBubble from '../components/ChatBubble';

export default function Workout() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const plan = state?.plan;

  const [completed, setCompleted] = useState([]);
  const [resting, setResting] = useState(false);
  const [restSeconds, setRestSeconds] = useState(0);
  const [chatExercise, setChatExercise] = useState(null);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (!plan) navigate('/');
  }, [plan, navigate]);

  if (!plan) return null;

  const exercises = plan.exercises;
  const progress = completed.length / exercises.length;

  const toggleComplete = (index) => {
    if (completed.includes(index)) {
      setCompleted(completed.filter(i => i !== index));
    } else {
      setCompleted([...completed, index]);
      if (completed.length + 1 < exercises.length) {
        setResting(true);
        setRestSeconds(exercises[index].rest_seconds);
      }
    }
  };

  const handleRestEnd = () => {
    setResting(false);
  };

  const handleFinish = () => {
    const duration = Math.round((Date.now() - startTime) / 1000 / 60);
    navigate('/complete', {
      state: {
        plan,
        completedCount: completed.length,
        totalCount: exercises.length,
        duration,
      },
    });
  };

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-gray-900">{plan.title}</h2>
        <span className="text-sm text-gray-500">
          {completed.length}/{exercises.length}
        </span>
      </div>

      <ProgressBar progress={progress} />

      {resting && (
        <Timer seconds={restSeconds} onEnd={handleRestEnd} />
      )}

      <div className="space-y-3 mt-4">
        {exercises.map((ex, i) => (
          <ExerciseCard
            key={i}
            exercise={ex}
            index={i}
            isCompleted={completed.includes(i)}
            onToggle={() => toggleComplete(i)}
            onAskAI={() => setChatExercise(ex)}
          />
        ))}
      </div>

      {completed.length === exercises.length && (
        <button
          onClick={handleFinish}
          className="w-full mt-6 py-3 bg-green-500 text-white rounded-xl font-medium"
        >
          完成训练 🎉
        </button>
      )}

      {chatExercise && (
        <ChatBubble
          exercise={chatExercise}
          onClose={() => setChatExercise(null)}
        />
      )}
    </div>
  );
}
