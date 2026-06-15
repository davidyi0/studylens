import { useEffect, useState } from "react";

// Default to the local API; overridable via VITE_API_URL for deployed builds.
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type Health = { status: string; checks: Record<string, boolean> };

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-800">StudyLens</h1>
        <p className="mt-1 text-sm text-slate-500">Milestone 0 — backend connectivity check</p>

        <div className="mt-6">
          {error && <p className="text-red-600">API unreachable: {error}</p>}
          {!error && !health && <p className="text-slate-400">Checking…</p>}
          {health && (
            <ul className="space-y-1">
              <li className="font-medium">
                status: <span className="font-mono">{health.status}</span>
              </li>
              {Object.entries(health.checks).map(([dep, ok]) => (
                <li key={dep} className="font-mono text-sm">
                  {ok ? "✅" : "❌"} {dep}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
