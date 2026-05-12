from main import app
from fastapi.testclient import TestClient

c = TestClient(app)

print("=== Route Check ===")
routes = [r.path for r in app.routes]
for r in sorted(routes):
    print(f"  {r}")

r = c.get("/api/videos")
assert r.status_code == 200
print(f"\n=== Videos: {len(r.json())} items ===")

r = c.get("/api/videos/v003")
assert r.status_code == 200
data = r.json()
print(f"Video v003: {data['title']}")

r = c.get("/api/videos/v999")
assert r.status_code == 404
print("404 for missing video: OK")

r = c.post("/api/workout/generate", json={})
assert r.status_code == 400
print("400 for empty generate: OK")

r = c.post("/api/workout/generate", json={"video_id": "v001", "user_level": "beginner"})
assert r.status_code == 200
print("Generate with video_id (no AI key): returns error gracefully")
result = r.json()
print(f"  success={result['success']}, error={result.get('error', 'none')[:50]}")

print("\nAll checks passed!")
