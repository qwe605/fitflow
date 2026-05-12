const STORAGE_KEY = 'fitflow_history';

export function getHistory() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

export function saveWorkoutRecord(record) {
  const history = getHistory();
  history.unshift({
    ...record,
    id: Date.now().toString(),
    date: new Date().toISOString(),
  });
  if (history.length > 50) history.pop();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}
