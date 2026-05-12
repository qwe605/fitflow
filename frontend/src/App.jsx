import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Generate from './pages/Generate';
import Workout from './pages/Workout';
import Complete from './pages/Complete';

export default function App() {
  return (
    <BrowserRouter>
      <div className="max-w-md mx-auto min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/generate/:videoId" element={<Generate />} />
          <Route path="/workout" element={<Workout />} />
          <Route path="/complete" element={<Complete />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
