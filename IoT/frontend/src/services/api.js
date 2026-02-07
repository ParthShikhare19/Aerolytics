const API_BASE = "http://127.0.0.1:8000";

export async function fetchLatestData() {
  const res = await fetch(`${API_BASE}/latest`);
  if (!res.ok) throw new Error("Failed to fetch data");
  return res.json();
}
