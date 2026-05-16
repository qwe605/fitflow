const BASE = '/api';

export async function fetchVideos() {
  const res = await fetch(`${BASE}/videos`);
  return res.json();
}

export async function fetchSubtitle(videoId) {
  const res = await fetch(`${BASE}/videos/${videoId}/subtitle`);
  return res.json();
}

export async function generateWorkout({ videoId, subtitleText, userLevel, goal }) {
  const res = await fetch(`${BASE}/workout/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_id: videoId,
      subtitle_text: subtitleText,
      user_level: userLevel,
      goal: goal || '',
    }),
  });
  return res.json();
}

export async function generateWorkoutStream({ videoId, subtitleText, userLevel, goal }, onEvent) {
  const res = await fetch(`${BASE}/workout/generate/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_id: videoId,
      subtitle_text: subtitleText,
      user_level: userLevel,
      goal: goal || '',
    }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || '生成失败');
  }
  await consumeSSE(res, onEvent);
}

export async function chatWithAI({ exerciseName, exerciseContext, question, history }) {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      exercise_name: exerciseName,
      exercise_context: exerciseContext,
      question,
      history: history || [],
    }),
  });
  return res.json();
}

export async function parseDouyinUrl(url) {
  const res = await fetch(`${BASE}/douyin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || '解析失败');
  }
  return res.json();
}

export async function parseDouyinUrlStream(url, onEvent) {
  const res = await fetch(`${BASE}/douyin/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || '解析失败');
  }
  await consumeSSE(res, onEvent);
}

async function consumeSSE(response, onEvent) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop();

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          onEvent(data);
        } catch {}
      }
    }
  }

  if (buffer.startsWith('data: ')) {
    try {
      const data = JSON.parse(buffer.slice(6));
      onEvent(data);
    } catch {}
  }
}
